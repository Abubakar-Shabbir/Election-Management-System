from django.db import models
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import render
from django.db import models
from django.utils import timezone
from django.shortcuts import render, redirect





class User(models.Model):
    ROLES = [
        ('admin', 'Admin'),
        ('voter', 'Voter'),
        ('candidate', 'Candidate'),
        ('chairperson', 'Chairperson'),
    ]
    
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLES)
    email = models.EmailField(null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    


class Constituency(models.Model):
    constituency_no = models.CharField(primary_key=True, max_length=20)
    region = models.CharField(max_length=100)
    assembly = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.constituency_no} - {self.region} ({self.assembly})"

class Voter(models.Model):
    voter_cnic = models.CharField(primary_key=True, max_length=15)
    name = models.CharField(max_length=100)
    
    city = models.CharField(max_length=100)
    na_constituency_no = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='na_constituency', null=True)
    pa_constituency_no = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='pa_constituency', null=True)

    def __str__(self):
        return f"{self.name} ({self.voter_cnic})"

class Party(models.Model):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=100)
    leader_name = models.CharField(max_length=100)  # or 'chairman', pick one name

    def __str__(self):
        return self.name

    
class Candidate(models.Model):
    candidate_cnic = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=100)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    seat_type = models.CharField(max_length=10, choices=[('NA', 'NA'), ('PA', 'PA')])
    election = models.ForeignKey('Election', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.party.name})"


def voter_panel(request):
    cnic = request.session.get('voter_cnic')
    if not cnic:
        return redirect('/voter_login/')

    voter = Voter.objects.get(voter_cnic=cnic)
    already_voted = Vote.objects.filter(voter=voter).exists()

    na_candidates = Candidate.objects.filter(constituency=voter.na_constituency_no, seat_type='NA')
    pa_candidates = Candidate.objects.filter(constituency=voter.pa_constituency_no, seat_type='PA')

    return render(request, 'voter_panel.html', {
        'voter': voter,
        'already_voted': already_voted,
        'na_candidates': na_candidates,
        'pa_candidates': pa_candidates
    })


from django.http import HttpResponse

def cast_vote(request, candidate_id):
    cnic = request.session.get('voter_cnic')
    if not cnic:
        return redirect('/voter_login/')

    voter = Voter.objects.get(voter_cnic=cnic)
    candidate = Candidate.objects.get(pk=candidate_id)
    seat_type = candidate.seat_type

    # Get current active election
    election = Election.objects.filter(is_active=True).first()
    if not election:
        return HttpResponse("No active election found", status=400)

    # ✅ Prevent duplicate voting for same seat type in same election
    if Vote.objects.filter(voter=voter, election=election, seat_type=seat_type).exists():
        return HttpResponse(f"You already voted for {seat_type}", status=403)

    # ✅ Save vote
    Vote.objects.create(
        voter=voter,
        candidate=candidate,
        election=election,
        seat_type=seat_type
    )

    return render(request, 'vote_success.html')




    

   

from datetime import timedelta

class VotingControl(models.Model):
    start_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    duration_minutes = models.IntegerField(default=120)

    def voting_end_time(self):
        return self.start_time + timedelta(minutes=self.duration_minutes)

    def is_voting_open(self):
        from django.utils import timezone
        return self.is_active and timezone.now() < self.voting_end_time()


from django.db import models

from django.utils import timezone
from datetime import timedelta



def voter_panel(request):
    if request.session.get('role') != 'voter':
        return redirect('/login/')

    voter = Voter.objects.get(voter_cnic=request.session.get('username'))
    elections = Election.objects.all()

    # Auto-deactivate expired ones
    for e in elections:
        if e.is_active and not e.is_open():
            e.is_active = False
            e.save()

    # Annotate open/closed status
    for e in elections:
        e.is_open = e.is_open()

    return render(request, 'voter_panel.html', {
        'voter': voter,
        'elections': elections
    })



class Vote(models.Model):
    voter = models.ForeignKey('Voter', on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    election = models.ForeignKey('Election', on_delete=models.CASCADE)  # <-- Wrapped in quotes
    cast_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.voter.name} voted for {self.candidate.name}"


# models.py
from django.utils import timezone
from datetime import timedelta

from datetime import timedelta

# models.py
from django.db import models
from django.utils import timezone

class Election(models.Model):
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=120)
    is_active = models.BooleanField(default=False)  # manually or automatically activated

    def is_open(self):
        now = timezone.now()
        end_time = self.start_time + timezone.timedelta(minutes=self.duration_minutes)
        return self.is_active and self.start_time <= now <= end_time

    def auto_update_status(self):
        """Automatically update election's active status based on time"""
        now = timezone.now()
        if self.start_time <= now <= self.start_time + timezone.timedelta(minutes=self.duration_minutes):
            self.is_active = True
        else:
            self.is_active = False
        self.save()
    # In your Election model
    from datetime import timedelta

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.duration_minutes or 0)




class Vote(models.Model):
    voter = models.ForeignKey('Voter', on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    election = models.ForeignKey('Election', on_delete=models.CASCADE, null=True, blank=True)
    seat_type = models.CharField(max_length=10, choices=[('NA', 'NA'), ('PA', 'PA')])  # ✅ Add this
    cast_at = models.DateTimeField(auto_now_add=True)

    class Meta:
     unique_together = ('voter', 'election', 'seat_type')  # ✅ updated
 # ✅ Enforce one vote per seat type per voter

    def __str__(self):
        return f"{self.voter.name} voted for {self.candidate.name} ({self.seat_type})"



