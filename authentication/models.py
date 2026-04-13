from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string


class User(AbstractUser):
    """
    Custom User model with role-based authentication
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_student(self):
        return self.role == 'student'
    
    def is_tutor(self):
        return self.role == 'tutor'
    
    def is_admin(self):
        return self.role == 'admin'


class StudentProfile(models.Model):
    """
    Extended profile for students
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    current_level = models.CharField(max_length=50, blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
    
    def __str__(self):
        return f"Student Profile: {self.user.full_name}"


class TutorProfile(models.Model):
    """
    Extended profile for tutors
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    hire_date = models.DateField()
    department = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    class Meta:
        db_table = 'tutor_profiles'
        verbose_name = 'Tutor Profile'
        verbose_name_plural = 'Tutor Profiles'
    
    def __str__(self):
        return f"Tutor Profile: {self.user.full_name}"


class AdminProfile(models.Model):
    """
    Extended profile for admins
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    hire_date = models.DateField()
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    permissions_level = models.CharField(max_length=50, default='standard')
    
    class Meta:
        db_table = 'admin_profiles'
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'
    
    def __str__(self):
        return f"Admin Profile: {self.user.full_name}"


class EmailVerificationOTP(models.Model):
    """
    Model for storing email verification OTPs
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_otps')
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'email_verification_otps'
        verbose_name = 'Email Verification OTP'
        verbose_name_plural = 'Email Verification OTPs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.email} - {self.otp_code}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only set expiry on creation
            self.expires_at = timezone.now() + timedelta(minutes=10)  # OTP expires in 10 minutes
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_otp(cls, user, email):
        """
        Generate a new OTP for email verification
        """
        # Invalidate any existing OTPs for this user/email
        cls.objects.filter(user=user, email=email, is_used=False).update(is_used=True)
        
        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Create new OTP
        otp = cls.objects.create(
            user=user,
            email=email,
            otp_code=otp_code
        )
        
        return otp
    
    def is_valid(self):
        """
        Check if OTP is valid (not used and not expired)
        """
        return not self.is_used and timezone.now() < self.expires_at
    
    def verify(self, provided_otp):
        """
        Verify the provided OTP
        """
        if not self.is_valid():
            return False
        
        if self.otp_code != provided_otp:
            self.attempts += 1
            self.save()
            return False
        
        # Mark as used
        self.is_used = True
        self.save()
        
        # Verify user's email
        self.user.is_verified = True
        self.user.save()
        
        return True
    
    def is_expired(self):
        """
        Check if OTP has expired
        """
        return timezone.now() >= self.expires_at