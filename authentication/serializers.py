from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, StudentProfile, TutorProfile, AdminProfile, EmailVerificationOTP


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'phone_number')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 
                 'phone_number', 'profile_picture', 'date_of_birth', 'is_verified', 
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for student profile
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = '__all__'


class TutorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for tutor profile
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TutorProfile
        fields = '__all__'


class AdminProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for admin profile
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AdminProfile
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Comprehensive user profile serializer
    """
    student_profile = StudentProfileSerializer(read_only=True)
    tutor_profile = TutorProfileSerializer(read_only=True)
    admin_profile = AdminProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 
                 'phone_number', 'profile_picture', 'date_of_birth', 'is_verified', 
                 'created_at', 'updated_at', 'student_profile', 'tutor_profile', 'admin_profile')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value


class OTPVerificationSerializer(serializers.Serializer):
    """
    Serializer for OTP verification
    """
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('OTP must contain only digits')
        return value


class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for resending OTP
    """
    email = serializers.EmailField()