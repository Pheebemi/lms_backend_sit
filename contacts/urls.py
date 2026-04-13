from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    # Public URL (No Authentication Required)
    path('submit/', views.ContactSubmissionCreateView.as_view(), name='contact_submit'),
    
    # Admin URLs (Authentication Required)
    path('admin/submissions/', views.ContactSubmissionListView.as_view(), name='admin_contact_list'),
    path('admin/submissions/<int:pk>/', views.ContactSubmissionDetailView.as_view(), name='admin_contact_detail'),
    path('admin/stats/', views.contact_stats, name='admin_contact_stats'),
]




