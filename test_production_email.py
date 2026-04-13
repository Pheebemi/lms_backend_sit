#!/usr/bin/env python
import os
import django

# Force production mode
os.environ['DEBUG'] = 'False'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_production_email():
    print(f"DEBUG mode: {settings.DEBUG}")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print("-" * 50)
    
    try:
        # Send test email
        send_mail(
            'Test OTP Email - Production Mode',
            'Your OTP code is: 123456',
            settings.DEFAULT_FROM_EMAIL,
            ['lemuelemmanuel29@gmail.com'],
            fail_silently=False,
        )
        print("✅ Email sent successfully to real inbox!")
    except Exception as e:
        print(f"❌ Email failed: {e}")

if __name__ == "__main__":
    test_production_email()




