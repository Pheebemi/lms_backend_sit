from django.contrib import admin
from .models import (
    Category, Course, Lesson, Quiz, QuizQuestion,
    Enrollment, LessonProgress, QuizAttempt, QuizAnswer, CourseReview, Payment, Certificate
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'price', 'is_free', 'status', 'total_students', 'average_rating', 'created_at']
    list_filter = ['status', 'is_free', 'difficulty', 'category', 'created_at']
    search_fields = ['title', 'description', 'instructor__first_name', 'instructor__last_name']
    readonly_fields = ['id', 'total_students', 'average_rating', 'total_ratings', 'created_at', 'updated_at']
    filter_horizontal = []


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'duration_minutes', 'is_published', 'created_at']
    list_filter = ['is_published', 'course', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    ordering = ['course', 'order']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'time_limit_minutes', 'passing_score', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'lesson__title', 'lesson__course__title']


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'question_type', 'order', 'points', 'created_at']
    list_filter = ['question_type', 'quiz__lesson__course']
    search_fields = ['question_text', 'quiz__lesson__title']
    ordering = ['quiz', 'order']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'is_completed', 'progress_percentage']
    list_filter = ['is_completed', 'enrolled_at', 'course']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
    readonly_fields = ['enrolled_at']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'is_completed', 'time_spent_minutes', 'completed_at']
    list_filter = ['is_completed', 'lesson__course']
    search_fields = ['student__first_name', 'student__last_name', 'lesson__title']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'attempt_number', 'score', 'is_passed', 'started_at']
    list_filter = ['is_passed', 'started_at', 'quiz__lesson__course']
    search_fields = ['student__first_name', 'student__last_name', 'quiz__lesson__title']
    readonly_fields = ['started_at']


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct', 'points_earned']
    list_filter = ['is_correct', 'attempt__quiz__lesson__course']
    search_fields = ['answer_text', 'question__question_text']


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'course']
    search_fields = ['student__first_name', 'student__last_name', 'course__title', 'review_text']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'amount', 'currency', 'status', 'payment_method', 'created_at', 'paid_at']
    list_filter = ['status', 'currency', 'payment_method', 'created_at', 'paid_at']
    search_fields = ['student__first_name', 'student__last_name', 'course__title', 'flutterwave_reference', 'flutterwave_transaction_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'paid_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('student', 'course', 'amount', 'currency', 'status')
        }),
        ('Flutterwave Details', {
            'fields': ('flutterwave_reference', 'flutterwave_transaction_id', 'flutterwave_payment_id', 'payment_method')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_id', 'student', 'course', 'issued_at', 'is_verified']
    list_filter = ['is_verified', 'issued_at', 'course']
    search_fields = ['certificate_id', 'student__first_name', 'student__last_name', 'course__title']
    readonly_fields = ['certificate_id', 'issued_at']
    ordering = ['-issued_at']
    
    fieldsets = (
        ('Certificate Info', {
            'fields': ('student', 'course', 'enrollment', 'certificate_id')
        }),
        ('Certificate Details', {
            'fields': ('issued_at', 'is_verified', 'pdf_file')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'course', 'enrollment')









