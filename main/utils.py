import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp):
    subject = "🔐 Your Login OTP - Election Management System"
    message = f"Dear User,\n\nYour OTP for login is: {otp}\n\nRegards,\nElection System"
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user_email])

# main/utils.py

from django.core.mail import send_mail
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_email_otp(email, otp):
    subject = 'Your OTP for Voter Registration'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    # Load HTML content from template
    html_content = render_to_string('otp_email.html', {'otp': otp})

    # Create the email
    email_message = EmailMultiAlternatives(subject=subject, body=html_content, from_email=from_email, to=recipient_list)
    email_message.attach_alternative(html_content, "html")  # Mark as HTML

    # Send the email
    email_message.send(fail_silently=False)


# ///////////////////////////


