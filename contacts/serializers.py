from rest_framework import serializers
from .models import ContactSubmission


class ContactSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for creating contact form submissions"""
    
    class Meta:
        model = ContactSubmission
        fields = ['first_name', 'last_name', 'email', 'phone', 'message']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'message': {'required': True},
            'phone': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate email format"""
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value.lower()
    
    def validate_message(self, value):
        """Validate message is not empty"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value.strip()


class ContactSubmissionListSerializer(serializers.ModelSerializer):
    """Serializer for listing contact submissions (admin only)"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactSubmission
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 
            'phone', 'message', 'status', 'created_at', 'updated_at', 
            'replied_at', 'ip_address'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'replied_at']
    
    def get_full_name(self, obj):
        return obj.full_name


class ContactSubmissionDetailSerializer(serializers.ModelSerializer):
    """Serializer for contact submission details (admin only)"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactSubmission
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 
            'phone', 'message', 'status', 'created_at', 'updated_at', 
            'replied_at', 'ip_address'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'replied_at', 'ip_address']
    
    def get_full_name(self, obj):
        return obj.full_name




