from django.db import models
from django.utils import timezone


class ContactSubmission(models.Model):
    """Model to store contact form submissions"""
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    
    # Contact Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    
    # Status and Metadata
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    
    # Optional: IP address for tracking
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"Contact from {self.first_name} {self.last_name} - {self.email}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def mark_as_read(self):
        """Mark the submission as read"""
        self.status = 'read'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_replied(self):
        """Mark the submission as replied"""
        self.status = 'replied'
        self.replied_at = timezone.now()
        self.save(update_fields=['status', 'replied_at', 'updated_at'])
