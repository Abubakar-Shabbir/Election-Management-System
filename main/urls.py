from django.urls import path
from django.shortcuts import render
from django.shortcuts import render, redirect
from .import views

urlpatterns = [
    
    path('', lambda request: redirect('login')),  # Redirect to login
    path('login/', views.login_view, name='login'),
    path('register/', views.register_voter, name='register_voter'),
    path('adminpanel/', views.admin_home, name='admin_home'),
     path('adminpanel/add-constituency/', views.add_constituency, name='add_constituency'),
     path('adminpanel/add-party/', views.add_party, name='add_party'),
     path('adminpanel/view-voters/', views.view_all_voters, name='view_all_voters'),
     path('adminpanel/view-parties/', views.view_all_parties, name='view_all_parties'),
     path('adminpanel/view-candidates/', views.view_all_candidates, name='view_all_candidates'),
     path('adminpanel/create-election/', views.create_election, name='create_election'),
      path('adminpanel/view_results/', views.view_results, name='view_results'),
      path('adminpanel/add-candidate/', views.add_candidate, name='add_candidate'),
      path('voterpanel/', views.voter_panel, name='voter_panel'),
    path('castvote/', views.cast_vote, name='cast_vote'),
    path('register/', views.register_voter, name='register'),
     path('start-voting/', views.start_voting, name='start_voting'),
     path('voterpanel/vote/', views.cast_vote_page, name='cast_vote_page'),
      path('voterpanel/results/', views.view_results_page, name='view_results_page'),
      path('castvote/<int:election_id>/', views.cast_vote, name='cast_vote'),
      path('voterpanel/cast/', views.cast_vote_page, name='cast_vote_page'),
      path('verify-otp/', views.verify_otp, name='verify_otp'),
      
    path('logout/', views.logout_view, name='logout'),
    # main/urls.py
path('voterpanel/vote/<int:election_id>/', views.cast_vote, name='cast_vote'),







    # dummy redirect pages for now
    path('adminpanel/', lambda r: render(r, 'dummy.html', {'role': 'Admin'})),
    path('voterpanel/', lambda r: render(r, 'dummy.html', {'role': 'Voter'})),
    path('candidatepanel/', lambda r: render(r, 'dummy.html', {'role': 'Candidate'})),
    path('partypanel/', lambda r: render(r, 'dummy.html', {'role': 'Party Chairperson'})),
    
]




