from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Voter, Constituency
from .models import Constituency
from .models import Party
from django.db.models import Count
from .models import Candidate, Vote, Constituency, Party
from django.db.models import Count
from .models import Candidate, VotingControl
from django.shortcuts import render
from django.shortcuts import render
from .models import Vote, VotingControl, Candidate
from django.db.models import Count
from collections import defaultdict
from .utils import generate_otp, send_otp_email

def login_view(request):
    error = ''
    if request.method == 'POST':
        uname = request.POST.get('username').strip()
        pwd = request.POST.get('password').strip()
        role = request.POST.get('role')

        try:
            user = User.objects.get(username=uname, password=pwd, role=role)

            # Only admin and voter require OTP
            if role in ['admin', 'voter']:
                otp = generate_otp()
                user.otp = otp
                user.save()
                send_otp_email(user.email, otp)

                # Save login attempt session
                request.session['pending_user'] = uname
                request.session['pending_role'] = role
                return redirect('/verify-otp/')

            # Other roles login directly
            request.session['username'] = uname
            request.session['role'] = user.role
            if role == 'candidate':
                return redirect('/candidatepanel/')
            elif role == 'chairperson':
                return redirect('/partypanel/')

        except User.DoesNotExist:
            error = 'Invalid credentials or role mismatch.'

    return render(request, 'login.html', {'error': error})


def verify_otp(request):
    error = ''
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        uname = request.session.get('pending_user')
        role = request.session.get('pending_role')

        try:
            user = User.objects.get(username=uname, role=role)
            if user.otp == entered_otp:
                user.otp = None
                user.save()

                request.session['username'] = user.username
                request.session['role'] = user.role
                if user.role == 'admin':
                    return redirect('/adminpanel/')
                elif user.role == 'voter':
                    return redirect('/voterpanel/')
            else:
                error = 'Invalid OTP.'
        except User.DoesNotExist:
            error = 'Session expired or user not found.'

    return render(request, 'verify_otp.html', {'error': error})


import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_otp_email(email, otp):
    subject = 'Login Attempt-EMS'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    # Load HTML content from template
    html_content = render_to_string('otp_email.html', {'otp': otp})

    # Create the email
    email_message = EmailMultiAlternatives(subject=subject, body=html_content, from_email=from_email, to=recipient_list)
    email_message.attach_alternative(html_content, "text/html")  # Mark as HTML

    # Send the email
    email_message.send(fail_silently=False)



from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render
from .models import Voter, Constituency

from .models import Voter, User, Constituency
from .utils import generate_otp, send_email_otp  # assume you have this utility
import random

def register_voter(request):
    error = ''
    success = ''
    na_constituencies = Constituency.objects.filter(assembly='NA')
    pa_constituencies = Constituency.objects.filter(assembly='PA')

    if request.method == 'POST':
        cnic = request.POST.get('cnic')
        name = request.POST.get('name')
        email = request.POST.get('email')
        city = request.POST.get('city')
        password = request.POST.get('password')
        na_const_id = request.POST.get('na_constituency')
        pa_const_id = request.POST.get('pa_constituency')

        # Check for existing user
        if Voter.objects.filter(voter_cnic=cnic).exists() or User.objects.filter(username=cnic).exists():
            error = "CNIC already registered."
        else:
            try:
                na_const = Constituency.objects.get(constituency_no=na_const_id, assembly='NA')
                pa_const = Constituency.objects.get(constituency_no=pa_const_id, assembly='PA')

                # Create Voter record
                Voter.objects.create(
                    voter_cnic=cnic,
                    name=name,
                    city=city,
                    na_constituency_no=na_const,
                    pa_constituency_no=pa_const
                )

                # Create User record (OTP will be sent only on login)
                user = User.objects.create(
                    username=cnic,
                    password=password,
                    role='voter',
                    email=email
                )

                success = "✅ Voter registered successfully. You can now log in."
            except Constituency.DoesNotExist:
                error = "Invalid constituency selected."
            except Exception as e:
                error = f"Unexpected error: {str(e)}"

    return render(request, 'register.html', {
        'error': error,
        'success': success,
        'na_constituencies': na_constituencies,
        'pa_constituencies': pa_constituencies
    })


def admin_home(request):
    if request.session.get('role') != 'admin':
        return redirect('/login/')
    return render(request, 'admin_home.html')




def add_constituency(request):
    if request.session.get('role') != 'admin':
        return redirect('/login/')

    success = ''
    error = ''
    if request.method == 'POST':
        const_no = request.POST.get('const_no').strip()
        region = request.POST.get('region').strip()
        assembly = request.POST.get('assembly').strip().upper()

        if Constituency.objects.filter(constituency_no=const_no).exists():
            error = "Constituency number already exists."
        else:
            Constituency.objects.create(
                constituency_no=const_no,
                region=region,
                assembly=assembly
            )
            success = "Constituency added successfully."

    return render(request, 'add_constituency.html', {'success': success, 'error': error})



def add_party(request):
    error = ''
    success = ''
    if request.method == 'POST':
        name = request.POST.get('name')
        leader = request.POST.get('leader')
        symbol = request.POST.get('symbol')

        if Party.objects.filter(name=name).exists():
            error = "Party with this name already exists."
        else:
            Party.objects.create(name=name, leader_name=leader, symbol=symbol)
            success = "Party added successfully."

    return render(request, 'add_party.html', {'error': error, 'success': success})


from .models import Voter

def view_all_voters(request):
    voters = Voter.objects.all()
    return render(request, 'view_voters.html', {'voters': voters})


from .models import Party

def view_all_parties(request):
    parties = Party.objects.all()
    return render(request, 'view_parties.html', {'parties': parties})

from .models import Candidate
def view_all_candidates(request):
    if request.session.get('role') != 'admin':
        return redirect('/login/')
    
    candidates_na = Candidate.objects.filter(seat_type='NA').order_by('constituency__constituency_no')
    candidates_pa = Candidate.objects.filter(seat_type='PA').order_by('constituency__constituency_no')

    return render(request, 'view_candidates.html', {
        'candidates_na': candidates_na,
        'candidates_pa': candidates_pa
    })


from .models import VotingControl
from django.utils import timezone

from django.utils import timezone

from django.utils import timezone

def start_voting(request):
    success = ''
    control = VotingControl.objects.first()

    # Auto-deactivate old session if expired
    if control and control.is_active and not control.is_voting_open():
        control.is_active = False
        control.save()

    if request.method == 'POST':
        duration = int(request.POST.get('duration', 120))
        if not control:
            control = VotingControl.objects.create(
                start_time=timezone.now(),
                is_active=True,
                duration_minutes=duration
            )
        else:
            control.start_time = timezone.now()
            control.duration_minutes = duration
            control.is_active = True
            control.save()

        success = "Voting started successfully."

    return render(request, 'start_voting.html', {
        'control': control,
        'success': success
    })





from django.db.models import Count
from django.shortcuts import render
from .models import Vote, Candidate, Party, Constituency

from django.db.models import Count
from collections import defaultdict

from django.db.models import Count
from django.shortcuts import render
from .models import Vote, Candidate

def view_results(request):
    # Group by candidate, seat_type, and count votes
    vote_summary = Vote.objects.values(
        'candidate__candidate_cnic',
        'candidate__name',
        'candidate__party__name',
        'candidate__constituency__constituency_no',
        'candidate__constituency__region',
        'candidate__seat_type'
    ).annotate(total_votes=Count('id'))

    # Separate NA and PA winners
    na_results = []
    pa_results = []

    # Organize winners per constituency
    grouped = {}
    for row in vote_summary:
        key = (row['candidate__constituency__constituency_no'], row['candidate__seat_type'])
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(row)

    for (const_no, seat_type), candidates in grouped.items():
        sorted_candidates = sorted(candidates, key=lambda x: x['total_votes'], reverse=True)
        winner = sorted_candidates[0]
        if seat_type == 'NA':
            na_results.append(winner)
        else:
            pa_results.append(winner)

    return render(request, 'view_results.html', {
        'na_results': na_results,
        'pa_results': pa_results
    })





from django.db.models import Count

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Election

def create_election(request):
    success = None

    if request.method == 'POST':
        title = request.POST.get('title')
        start_time = request.POST.get('start_time')
        duration = request.POST.get('duration_minutes')

        if title and start_time and duration:
            Election.objects.create(
                title=title,
                start_time=start_time,
                duration_minutes=int(duration)
            )
            success = "Election created successfully."

    return render(request, 'create_election.html', {'success': success})




from django.shortcuts import render, redirect
from .models import Election

from django.shortcuts import redirect
from django.utils.http import urlencode

def create_election(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        start_time = request.POST.get('start_time')
        duration = request.POST.get('duration_minutes')

        Election.objects.create(
            title=title,
            start_time=start_time,
            duration_minutes=duration
        )

        # ✅ Redirect with ?success=1 to show popup
        return redirect('/adminpanel/create-election/?success=1')

    return render(request, 'create_election.html')


from .models import Candidate, Party, User
from django.contrib.auth.decorators import login_required

@login_required
def candidate_join_party(request):
    username = request.session.get('username')
    candidate = Candidate.objects.filter(candidate_cnic=username).first()
    parties = Party.objects.all()
    success = ''
    error = ''

    if request.method == 'POST':
        selected_party_id = request.POST.get('party_id')
        selected_party = Party.objects.get(id=selected_party_id)
        
        if candidate:
            candidate.requested_party = selected_party
            candidate.is_party_approved = False
            candidate.save()
            success = "Party join request sent. Waiting for chairperson approval."
        else:
            error = " Candidate not found."

    return render(request, 'candidate_join_party.html', {
        'candidate': candidate,
        'parties': parties,
        'success': success,
        'error': error
    })

@login_required
def view_party_requests(request):
    if request.session.get('role') != 'chairperson':
        return redirect('/login/')

    requests = Candidate.objects.filter(requested_party__isnull=False, is_party_approved=False)
    return render(request, 'party_requests.html', {'requests': requests})

@login_required
def approve_party_request(request, candidate_cnic):
    if request.session.get('role') != 'chairperson':
        return redirect('/login/')

    candidate = Candidate.objects.get(candidate_cnic=candidate_cnic)
    if candidate and candidate.requested_party:
        candidate.party = candidate.requested_party
        candidate.is_party_approved = True
        candidate.save()

    return redirect('/partypanel/requests/')

from django.shortcuts import render, redirect
from .models import Voter, Candidate, Vote, VotingControl
from django.utils import timezone

from .models import Election, Vote
from django.utils import timezone

from .models import Election

from django.shortcuts import render, redirect
from .models import Voter, Election
from django.utils import timezone

def voter_panel(request):
    if request.session.get('role') != 'voter':
        return redirect('/login/')

    voter = Voter.objects.get(voter_cnic=request.session.get('username'))
    elections = Election.objects.filter(is_active=True)
    open_elections = [e for e in elections if e.is_open()]

    return render(request, 'voter_panel.html', {
        'voter': voter,
        'elections': open_elections
    })





from django.shortcuts import render, redirect, get_object_or_404
from .models import Voter, Candidate, Vote, Election
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail  # For email (optional)
from django.conf import settings
from .models import Voter, Candidate, Election, Vote
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.contrib import messages

def cast_vote(request, election_id):
    if request.session.get('role') != 'voter':
        return redirect('/login/')

    voter_cnic = request.session.get('username')
    voter = get_object_or_404(Voter, voter_cnic=voter_cnic)
    election = get_object_or_404(Election, id=election_id)

    if not election.is_open():
        messages.error(request, "Election is closed.")
        return redirect('cast_vote', election_id=election.id)

    if request.method == 'POST':
        candidate_cnic = request.POST.get('candidate_cnic')
        try:
            selected_candidate = Candidate.objects.get(candidate_cnic=candidate_cnic)
        except Candidate.DoesNotExist:
            messages.error(request, "Candidate not found.")
            return redirect('cast_vote', election_id=election.id)

        seat_type = selected_candidate.seat_type

        already_voted = Vote.objects.filter(
            voter=voter,
            election=election,
            seat_type=seat_type
        ).exists()

        if already_voted:
            messages.warning(request, f"You have already voted for {seat_type} seat.")
            return redirect('cast_vote', election_id=election.id)

        Vote.objects.create(
            voter=voter,
            candidate=selected_candidate,
            election=election,
            seat_type=seat_type
        )

        # Send real-time update
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'live_results',
            {
                'type': 'vote_cast',
                'candidate_cnic': selected_candidate.candidate_cnic,
                'seat_type': seat_type,
                'constituency': selected_candidate.constituency
            }
        )

        messages.success(request, "Your vote has been submitted successfully.")
        return redirect('cast_vote', election_id=election.id)

    na_candidates = Candidate.objects.filter(
        seat_type='NA',
        constituency=voter.na_constituency_no
    )
    pa_candidates = Candidate.objects.filter(
        seat_type='PA',
        constituency=voter.pa_constituency_no
    )

    return render(request, 'cast_vote.html', {
        'voter': voter,
        'na_candidates': na_candidates,
        'pa_candidates': pa_candidates,
        'election': election
    })

# utils.py (ya views.py)

from django.core.mail import send_mail
from django.conf import settings

def send_vote_confirmation_email(voter_email, voter_name, election_name):
    subject = 'Vote Cast Confirmation'
    message = f'Dear {voter_name},\n\nYou have successfully cast your vote in the election: {election_name}.\n\nThank you for participating!'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [voter_email]

    send_mail(subject, message, from_email, recipient_list)



from .models import Candidate, Constituency, Party

from django.shortcuts import render, redirect
from .models import Candidate, Constituency, Party
from django.contrib import messages

def add_candidate(request):
    # Check if user is admin
    if request.session.get('role') != 'admin':
        return redirect('/login/')

    # Success and error message placeholders for NA and PA
    success_na = ''
    success_pa = ''
    error_na = ''
    error_pa = ''

    # Fetch NA and PA constituencies, all parties, and elections
    constituencies_na = Constituency.objects.filter(assembly='NA')
    constituencies_pa = Constituency.objects.filter(assembly='PA')
    parties = Party.objects.all()
    elections = Election.objects.all()

    if request.method == 'POST':
        seat_type = request.POST.get('seat_type')   # NA or PA
        name = request.POST.get('name', '').strip()
        cnic = request.POST.get('cnic', '').replace('-', '').strip()
        constituency_no = request.POST.get('constituency')
        party_id = request.POST.get('party')
        election_id = request.POST.get('election')

        # Validation: All fields must be filled
        if not all([name, cnic, constituency_no, party_id, election_id]):
            msg = "Please fill in all fields including election."
            if seat_type == 'NA':
                error_na = msg
            else:
                error_pa = msg

        elif not cnic.isdigit() or len(cnic) != 13:
            msg = "CNIC must be 13 digits only."
            if seat_type == 'NA':
                error_na = msg
            else:
                error_pa = msg

        elif Candidate.objects.filter(candidate_cnic=cnic, seat_type=seat_type).exists():
            msg = "Candidate with this CNIC already exists for this seat type."
            if seat_type == 'NA':
                error_na = msg
            else:
                error_pa = msg

        elif Candidate.objects.filter(
            constituency__constituency_no=constituency_no,
            constituency__assembly=seat_type,
            party__id=party_id,
            seat_type=seat_type
        ).exists():
            msg = "This party already has a candidate in this constituency."
            if seat_type == 'NA':
                error_na = msg
            else:
                error_pa = msg

        else:
            try:
                constituency = Constituency.objects.get(constituency_no=constituency_no, assembly=seat_type)
                party = Party.objects.get(id=party_id)
                election = Election.objects.get(id=election_id)

                Candidate.objects.create(
                    name=name,
                    candidate_cnic=cnic,
                    seat_type=seat_type,
                    constituency=constituency,
                    party=party,
                    election=election
                )

                msg = f"✅ {seat_type} Candidate added successfully."
                if seat_type == 'NA':
                    success_na = msg
                else:
                    success_pa = msg

            except (Constituency.DoesNotExist, Party.DoesNotExist, Election.DoesNotExist):
                msg = "Invalid selection."
                if seat_type == 'NA':
                    error_na = msg
                else:
                    error_pa = msg

    return render(request, 'add_candidate.html', {
        'success_na': success_na,
        'error_na': error_na,
        'success_pa': success_pa,
        'error_pa': error_pa,
        'constituencies_na': constituencies_na,
        'constituencies_pa': constituencies_pa,
        'parties': parties,
        'elections': elections  # Pass to template
    })


from django.contrib.auth import logout as auth_logout

def logout_view(request):
    request.session.flush()
    return redirect('/login/')

def cast_vote_page(request):
    if request.session.get('role') != 'voter':
        return redirect('/login/')

    voter = Voter.objects.get(voter_cnic=request.session.get('username'))

    # Get NA & PA candidates for voter's constituency
    na_candidates = Candidate.objects.filter(
        constituency=voter.na_constituency_no,
        seat_type='NA'
    )
    pa_candidates = Candidate.objects.filter(
        constituency=voter.pa_constituency_no,
        seat_type='PA'
    )

    return render(request, 'cast_vote.html', {
        'voter': voter,
        'na_candidates': na_candidates,
        'pa_candidates': pa_candidates
    })
from django.db.models import Count

from django.shortcuts import render
from django.db.models import Count
from .models import Vote, Election, Candidate, Voter, Constituency

from django.shortcuts import render
from django.db.models import Count
from .models import Vote, Election, Candidate, Voter, Constituency

from django.shortcuts import render
from django.db.models import Count
from .models import Vote, Voter, Party, Candidate

from django.shortcuts import render
from .models import Constituency, Candidate, Election, Vote
from django.db.models import Count

from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Election, Vote, Candidate, Constituency

from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from .models import Election, Vote, Candidate, Constituency


from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from .models import Election, Vote, Candidate, Constituency
from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from .models import Election, Candidate, Vote, Constituency

from django.shortcuts import render
from django.utils import timezone
from collections import defaultdict
from datetime import timedelta
from .models import Election, Vote, Candidate, Constituency

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Election, Vote, Candidate, Constituency

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from .models import Election, Vote, Candidate, Constituency

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Election, Vote, Candidate, Constituency

from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from .models import Election, Vote, Candidate, Constituency

from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from .models import Election, Vote, Candidate, Constituency

def view_results(request):
    results_data = []
    now = timezone.now()

    selected_constituency_id = request.GET.get('constituency_id')

    elections = Election.objects.filter(start_time__lte=now).order_by('-start_time')

    for election in elections:
        end_time = election.start_time + timedelta(minutes=election.duration_minutes)
        is_declared = now >= end_time

        # Filter only selected constituency if provided
        if selected_constituency_id:
            constituencies = Constituency.objects.filter(id=selected_constituency_id, candidate__election=election).distinct()
        else:
            constituencies = Constituency.objects.filter(candidate__election=election).distinct()

        for constituency in constituencies:
            candidates = Candidate.objects.filter(election=election, constituency=constituency).select_related('party')

            election_candidates = []
            for candidate in candidates:
                vote_count = Vote.objects.filter(candidate=candidate, election=election).count()
                election_candidates.append({
                    'candidate': candidate,
                    'votes': vote_count
                })

            if not election_candidates:
                continue

            election_candidates.sort(key=lambda x: x['votes'], reverse=True)

            result_status = "Declared" if is_declared else "Pending"
            winner = election_candidates[0]['candidate'] if is_declared else None

            # Assign status for template
            for entry in election_candidates:
                if not is_declared:
                    entry['status'] = 'Pending'
                elif entry['candidate'] == winner:
                    entry['status'] = 'Winner'
                else:
                    entry['status'] = 'Loser'

            results_data.append({
                'election': election,
                'constituency': constituency,
                'candidates': election_candidates,
                'winner': winner,
                'result_status': result_status,
                'end_time': end_time
            })

    return render(request, 'view_results.html', {
        'results_data': results_data,
        'constituencies': Constituency.objects.all(),
        'selected_constituency_id': int(selected_constituency_id) if selected_constituency_id else None
    })









from django.db.models import Count

def view_results_page(request):
    if request.session.get('role') != 'voter':
        return redirect('/login/')

    voter = Voter.objects.get(voter_cnic=request.session.get('username'))

    # Results for voter's constituencies
    na_results = Vote.objects.filter(candidate__constituency=voter.na_constituency_no, candidate__seat_type='NA') \
                    .values('candidate__name', 'candidate__party__name') \
                    .annotate(total_votes=Count('id')) \
                    .order_by('-total_votes')

    pa_results = Vote.objects.filter(candidate__constituency=voter.pa_constituency_no, candidate__seat_type='PA') \
                    .values('candidate__name', 'candidate__party__name') \
                    .annotate(total_votes=Count('id')) \
                    .order_by('-total_votes')

    return render(request, 'voter_results.html', {
        'voter': voter,
        'na_results': na_results,
        'pa_results': pa_results
    })


from django.shortcuts import render, redirect
from .models import Voter, Vote, Constituency
from django.db.models import Count

def admin_home(request):
    if request.session.get('role') != 'admin':
        return redirect('/login/')

    # Count total voters
    total_voters = Voter.objects.count()

    # Count total who have voted
    voted_count = Vote.objects.values('voter').distinct().count()
    not_voted_count = total_voters - voted_count

    # Constituency-wise votes (bar chart)
    vote_data = Vote.objects.values('candidate__constituency__region') \
        .annotate(total_votes=Count('id')) \
        .order_by('-total_votes')

    # Prepare data for chart
    constituency_labels = []
    constituency_votes = []

    for item in vote_data:
        constituency_labels.append(item['candidate__constituency__region'])
        constituency_votes.append(item['total_votes'])

    return render(request, 'admin_home.html', {
        'total_voters': total_voters,
        'voted_count': voted_count,
        'not_voted_count': not_voted_count,
        'constituency_labels': constituency_labels,
        'constituency_votes': constituency_votes,
        'total_candidates': Candidate.objects.count(),
    })


from django.db.models import Count, Sum
from .models import  Constituency, Party
from django.db.models import Count, Sum

def voter_results(request):
    voter = request.user.voter

    # Filters
    constituency_filter = request.GET.get('constituency')
    party_filter = request.GET.get('party')
    seat_type_filter = request.GET.get('seat_type')

    queryset = Result.objects.values(
        'candidate__name',
        'candidate__party__name',
        'candidate__constituency__constituency_no',
        'candidate__seat_type'
    ).annotate(total_votes=Count('id'))

    if constituency_filter:
        queryset = queryset.filter(candidate__constituency__constituency_no=constituency_filter)
    if party_filter:
        queryset = queryset.filter(candidate__party__name=party_filter)
    if seat_type_filter:
        queryset = queryset.filter(candidate__seat_type=seat_type_filter)

    # Pass filters and dropdown data
    constituencies = Constituency.objects.all()
    parties = Party.objects.all()

    return render(request, 'results.html', {
        'voter': voter,
        'filtered_results': queryset,
        'constituencies': constituencies,
        'parties': parties
    })

# views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Election

def start_voting(request):
    success = ''
    error = ''
    elections = Election.objects.all().order_by('-start_time')

    # Auto-deactivate expired elections
    for e in elections:
        if e.is_active and not e.is_open():
            e.is_active = False
            e.save()

    if request.method == 'POST':
        election_id = request.POST.get('election_id')
        duration = request.POST.get('duration', 120)
        try:
            election = Election.objects.get(id=election_id)
            election.start_time = timezone.now()
            election.duration_minutes = duration
            election.is_active = True
            election.save()
            success = f"✅ Election '{election.title}' started successfully."
        except Election.DoesNotExist:
            error = "Election not found."

    return render(request, 'start_voting.html', {
        'elections': elections,
        'success': success,
        'error': error
    })


from django.shortcuts import render
from django.db.models import Count
from .models import Vote, Party, Candidate, Constituency, Voter

def view_results_dashboard(request):
    # Vote count per party
    party_votes = (
        Vote.objects.values('candidate__party__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Total votes per constituency
    constituency_votes = (
        Vote.objects.values('candidate__constituency__constituency_no')
        .annotate(total=Count('id'))
    )

    context = {
        'party_votes': party_votes,
        'constituency_votes': constituency_votes,
        'total_voters': Voter.objects.count(),
        'total_votes_cast': Vote.objects.count(),
        'total_candidates': Candidate.objects.count(),
    }

    return render(request, 'adminpanel/results_dashboard.html', context)


# ////////////





