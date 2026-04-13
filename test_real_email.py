#!/usr/bin/env python
import os
import django

# Enable real email sending
os.environ['SEND_REAL_EMAIL'] = 'True'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_real_email():
    print(f"DEBUG mode: {settings.DEBUG}")
    print(f"SEND_REAL_EMAIL: {settings.SEND_REAL_EMAIL}")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print("-" * 50)
    
    try:
        # Send test email
        send_mail(
            'Test OTP Email - Real Email',
            'Your OTP code is: 123456',
            settings.DEFAULT_FROM_EMAIL,
            ['lemuelemmanuel29@gmail.com'],
            fail_silently=False,
        )
        print("✅ Real email sent successfully to inbox!")
    except Exception as e:
        print(f"❌ Email failed: {e}")

if __name__ == "__main__":
    test_real_email()




