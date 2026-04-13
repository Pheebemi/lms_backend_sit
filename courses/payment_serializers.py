from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment, Course

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment records"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'student', 'course', 'course_title', 'student_name',
            'amount', 'amount_display', 'currency', 'status', 'payment_method',
            'flutterwave_reference', 'flutterwave_transaction_id',
            'created_at', 'updated_at', 'paid_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_amount_display(self, obj):
        return f"₦{obj.amount:,.2f}"


class CreatePaymentSerializer(serializers.Serializer):
    """Serializer for creating payment requests"""
    course_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    currency = serializers.CharField(default='NGN', max_length=3)
    
    def validate_course_id(self, value):
        try:
            course = Course.objects.get(id=value)
            if course.is_free:
                raise serializers.ValidationError("This course is free and does not require payment.")
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found.")
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value


class FlutterwavePaymentSerializer(serializers.Serializer):
    """Serializer for Flutterwave payment verification"""
    tx_ref = serializers.CharField()
    transaction_id = serializers.CharField()
    status = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    payment_type = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(required=False)




