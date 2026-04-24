from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import User, StudentProfile, TutorProfile, AdminProfile, EmailVerificationOTP
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, ChangePasswordSerializer, OTPVerificationSerializer,
    ResendOTPSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create role-specific profile
        if user.role == 'student':
            StudentProfile.objects.create(
                user=user,
                student_id=f"STU{user.id:06d}",
                enrollment_date=user.created_at.date()
            )
        elif user.role == 'tutor':
            TutorProfile.objects.create(
                user=user,
                employee_id=f"TUT{user.id:06d}",
                hire_date=user.created_at.date()
            )
        elif user.role == 'admin':
            AdminProfile.objects.create(
                user=user,
                employee_id=f"ADM{user.id:06d}",
                hire_date=user.created_at.date()
            )
        
        # Generate OTP for email verification
        otp = EmailVerificationOTP.generate_otp(user, user.email)
        
        # Send OTP via email
        try:
            send_mail(
                subject='Verify your email - LMS by SIT Technologies',
                message=f'''Hello {user.first_name},

Thank you for registering with LMS by SIT Technologies.

Your verification code is:

{otp.otp_code}

This code expires in 10 minutes.

If you did not create an account, you can ignore this email.

LMS by SIT Technologies
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"OTP sent to {user.email}")
        except Exception as e:
            print(f"Failed to send email to {user.email}: {e}")
            print(f"Email: {user.email}")
            print(f"OTP Code: {otp.otp_code}")
            print(f"Expires at: {otp.expires_at}")
        
        return Response({
            'message': 'User registered successfully. Please verify your email.',
            'user': UserSerializer(user).data,
            'email_verification_required': True,
            'email': user.email
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User login endpoint
    """
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    
    # Check if email is verified
    if not user.is_verified:
        return Response({
            'error': 'Email not verified',
            'message': 'Please verify your email before signing in',
            'email': user.email,
            'verification_required': True
        }, status=status.HTTP_400_BAD_REQUEST)
    
    login(request, user)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view - get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info_view(request):
    """
    Get current user information
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """
    Change user password
    """
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def role_based_users_view(request):
    """
    Get users based on role (admin only)
    """
    if not request.user.is_admin():
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    role = request.GET.get('role')
    if role:
        users = User.objects.filter(role=role)
    else:
        users = User.objects.all()
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email_otp(request):
    """
    Verify email OTP
    """
    serializer = OTPVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp_code']
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get the most recent valid OTP
    otp = EmailVerificationOTP.objects.filter(
        user=user, 
        email=email, 
        is_used=False
    ).order_by('-created_at').first()
    
    if not otp:
        return Response({
            'error': 'No valid OTP found. Please request a new one.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if otp.is_expired():
        return Response({
            'error': 'OTP has expired. Please request a new one.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if otp.attempts >= 3:
        return Response({
            'error': 'Too many failed attempts. Please request a new OTP.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if otp.verify(otp_code):
        # Generate JWT tokens after successful verification
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Email verified successfully!',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid OTP code',
            'attempts_remaining': 3 - otp.attempts - 1
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_otp(request):
    """
    Resend OTP for email verification
    """
    serializer = ResendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if user.is_verified:
        return Response({
            'error': 'Email is already verified'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate new OTP
    otp = EmailVerificationOTP.generate_otp(user, email)
    
    # Send OTP via email
    try:
        send_mail(
            subject='New verification code - LMS by SIT Technologies',
            message=f'''Hello {user.first_name},

Here is your new verification code:

{otp.otp_code}

This code expires in 10 minutes. The previous code is no longer valid.

If you did not request this, you can ignore this email.

LMS by SIT Technologies
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"Resend OTP sent to {email}")
    except Exception as e:
        print(f"Failed to resend email to {email}: {e}")
        print(f"Email: {email}")
        print(f"OTP Code: {otp.otp_code}")
        print(f"Expires at: {otp.expires_at}")
    
    return Response({
        'message': 'OTP sent successfully',
        'email': email
    }, status=status.HTTP_200_OK)