from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from .models import Course, Payment, Enrollment
from .payment_serializers import CreatePaymentSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mock_initiate_payment(request):
    """
    Mock Flutterwave payment for local development
    """
    serializer = CreatePaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    course_id = serializer.validated_data['course_id']
    amount = serializer.validated_data['amount']
    currency = serializer.validated_data['currency']
    
    try:
        course = Course.objects.get(id=course_id)
        student = request.user
        
        # Check if user is already enrolled
        if Enrollment.objects.filter(student=student, course=course).exists():
            return Response({
                'error': 'You are already enrolled in this course'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already has a pending payment for this course
        existing_payment = Payment.objects.filter(
            student=student,
            course=course,
            status='pending'
        ).first()
        
        if existing_payment:
            return Response({
                'message': 'You already have a pending payment for this course',
                'payment_url': f"{settings.FRONTEND_URL}/mock-payment?tx_ref={existing_payment.flutterwave_reference}",
                'tx_ref': existing_payment.flutterwave_reference,
                'payment_id': str(existing_payment.id)
            }, status=status.HTTP_200_OK)
        
        # Create payment record
        payment = Payment.objects.create(
            student=student,
            course=course,
            amount=amount,
            currency=currency,
            status='pending'
        )
        
        # Set the flutterwave reference after payment is created
        payment.flutterwave_reference = f"MOCK-{payment.id}"
        payment.save()
        
        # Return mock payment URL
        return Response({
            'message': 'Mock payment initiated successfully',
            'payment_id': str(payment.id),
            'flutterwave_reference': payment.flutterwave_reference,
            'payment_url': f"{settings.FRONTEND_URL}/mock-payment?tx_ref={payment.flutterwave_reference}",
            'amount': float(amount),
            'currency': currency,
            'course_title': course.title
        }, status=status.HTTP_200_OK)
        
    except Course.DoesNotExist:
        return Response({
            'error': 'Course not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'An error occurred while initiating payment',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mock_verify_payment(request):
    """
    Mock payment verification for local development
    """
    tx_ref = request.data.get('tx_ref')
    
    if not tx_ref:
        return Response({
            'error': 'Transaction reference is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payment = Payment.objects.get(
            flutterwave_reference=tx_ref,
            student=request.user,
            status='pending'
        )
        
        # Mock successful payment
        payment.status = 'completed'
        payment.payment_method = 'mock_card'
        payment.save()
        
        # Enroll user in the course
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=payment.course)
        
        # Update course student count if new enrollment
        if created:
            payment.course.total_students += 1
            payment.course.save(update_fields=['total_students'])
        
        return Response({
            'message': 'Mock payment verified and course enrolled successfully!'
        }, status=status.HTTP_200_OK)
        
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'An error occurred while verifying payment',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




