from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import ContactSubmission
from .serializers import (
    ContactSubmissionSerializer,
    ContactSubmissionListSerializer,
    ContactSubmissionDetailSerializer
)


class ContactSubmissionCreateView(generics.CreateAPIView):
    """
    Public endpoint to submit contact form.
    No authentication required.
    """
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Create the contact submission
        contact = serializer.save(ip_address=ip_address)
        
        return Response({
            'success': True,
            'message': 'Thank you for contacting us! We will get back to you soon.',
            'data': {
                'id': contact.id,
                'email': contact.email,
                'created_at': contact.created_at
            }
        }, status=status.HTTP_201_CREATED)


# Admin Views (Authentication Required)
class ContactSubmissionListView(generics.ListAPIView):
    """
    List all contact submissions.
    Admin only.
    """
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ContactSubmission.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(message__icontains=search)
            )
        
        return queryset.order_by('-created_at')


class ContactSubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a contact submission.
    Admin only.
    """
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # If status is being updated to 'replied', set replied_at
        if 'status' in request.data and request.data['status'] == 'replied':
            instance.mark_as_replied()
            return Response(serializer.data)
        
        # If status is being updated to 'read', mark as read
        if 'status' in request.data and request.data['status'] == 'read':
            instance.mark_as_read()
            return Response(serializer.data)
        
        self.perform_update(serializer)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def contact_stats(request):
    """
    Get statistics about contact submissions.
    Admin only.
    """
    total = ContactSubmission.objects.count()
    new = ContactSubmission.objects.filter(status='new').count()
    read = ContactSubmission.objects.filter(status='read').count()
    replied = ContactSubmission.objects.filter(status='replied').count()
    archived = ContactSubmission.objects.filter(status='archived').count()
    
    return Response({
        'total': total,
        'new': new,
        'read': read,
        'replied': replied,
        'archived': archived,
    })
