from django.contrib import admin
from django.utils.html import format_html
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'full_name_display', 'email', 'phone', 'status', 
        'created_at', 'message_preview'
    ]
    list_filter = ['status', 'created_at', 'replied_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'message']
    readonly_fields = ['created_at', 'updated_at', 'replied_at', 'ip_address']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status & Metadata', {
            'fields': ('status', 'created_at', 'updated_at', 'replied_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_archived']
    
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Name'
    full_name_display.admin_order_field = 'first_name'
    
    def message_preview(self, obj):
        """Show first 50 characters of message"""
        if len(obj.message) > 50:
            return format_html(
                '<span title="{}">{}...</span>',
                obj.message,
                obj.message[:50]
            )
        return obj.message
    message_preview.short_description = 'Message Preview'
    
    def mark_as_read(self, request, queryset):
        """Mark selected submissions as read"""
        updated = queryset.update(status='read')
        self.message_user(request, f'{updated} contact submission(s) marked as read.')
    mark_as_read.short_description = "Mark selected as read"
    
    def mark_as_replied(self, request, queryset):
        """Mark selected submissions as replied"""
        from django.utils import timezone
        updated = queryset.update(status='replied', replied_at=timezone.now())
        self.message_user(request, f'{updated} contact submission(s) marked as replied.')
    mark_as_replied.short_description = "Mark selected as replied"
    
    def mark_as_archived(self, request, queryset):
        """Mark selected submissions as archived"""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} contact submission(s) archived.')
    mark_as_archived.short_description = "Archive selected"
