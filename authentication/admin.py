from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, TutorProfile, AdminProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'created_at')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('LMS Info', {'fields': ('role', 'is_verified', 'profile_picture')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """
    Student Profile admin
    """
    list_display = ('user', 'student_id', 'enrollment_date', 'current_level', 'gpa')
    list_filter = ('enrollment_date', 'current_level')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'student_id')
    readonly_fields = ('student_id',)


@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    """
    Tutor Profile admin
    """
    list_display = ('user', 'employee_id', 'hire_date', 'department', 'specialization')
    list_filter = ('hire_date', 'department')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'employee_id')
    readonly_fields = ('employee_id',)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    """
    Admin Profile admin
    """
    list_display = ('user', 'employee_id', 'hire_date', 'department', 'position', 'permissions_level')
    list_filter = ('hire_date', 'department', 'permissions_level')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'employee_id')
    readonly_fields = ('employee_id',)