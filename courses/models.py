from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class Category(models.Model):
    """
    Course categories for organization
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color code
    icon = models.CharField(max_length=50, blank=True, null=True)  # Icon class name
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Course model for tutors to create courses
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses', limit_choices_to={'role': 'tutor'})
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    is_free = models.BooleanField(default=True)
    
    # Course details
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_hours = models.PositiveIntegerField(default=0)  # Total course duration in hours
    language = models.CharField(max_length=50, default='English')
    
    # Media
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    preview_video_url = models.URLField(blank=True, null=True)  # YouTube URL for course preview
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    # Statistics
    total_lessons = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_ratings = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Update is_free based on price
        self.is_free = self.price == 0
        super().save(*args, **kwargs)
    
    def update_lesson_count(self):
        """Update the total_lessons count"""
        self.total_lessons = self.lessons.filter(is_published=True).count()
        self.save(update_fields=['total_lessons'])
    
    def get_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return None
    
    def get_preview_video_id(self):
        """Extract YouTube video ID from URL"""
        if self.preview_video_url:
            if 'youtube.com/watch?v=' in self.preview_video_url:
                return self.preview_video_url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in self.preview_video_url:
                return self.preview_video_url.split('youtu.be/')[1].split('?')[0]
        return None


class Lesson(models.Model):
    """
    Individual lessons within a course
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()  # Order of lesson in course
    
    # Content
    content = models.TextField(blank=True, null=True)  # Text content/notes
    video_url = models.URLField(blank=True, null=True)  # YouTube URL
    lesson_type = models.CharField(max_length=20, choices=[
        ('video', 'Video'),
        ('text', 'Text'),
        ('mixed', 'Mixed')
    ], default='text')
    duration_minutes = models.PositiveIntegerField(default=0)
    
    # Resources
    resources = models.JSONField(default=list, blank=True)  # List of resource URLs/files
    
    # Status
    is_published = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - Lesson {self.order}: {self.title}"
    
    def get_video_id(self):
        """Extract YouTube video ID from URL"""
        if self.video_url:
            if 'youtube.com/watch?v=' in self.video_url:
                return self.video_url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in self.video_url:
                return self.video_url.split('youtu.be/')[1].split('?')[0]
        return None
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update course lesson count
        self.course.update_lesson_count()
    
    def delete(self, *args, **kwargs):
        course = self.course
        super().delete(*args, **kwargs)
        # Update course lesson count after deletion
        course.update_lesson_count()


class Quiz(models.Model):
    """
    Quiz for each lesson
    """
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200, default='Quiz')
    description = models.TextField(blank=True, null=True)
    time_limit_minutes = models.PositiveIntegerField(default=30)  # Time limit for quiz
    passing_score = models.PositiveIntegerField(default=70)  # Passing percentage
    max_attempts = models.PositiveIntegerField(default=3)  # Maximum attempts allowed
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quizzes'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
    
    def __str__(self):
        return f"Quiz for {self.lesson.title}"


class QuizQuestion(models.Model):
    """
    Individual questions in a quiz
    """
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    order = models.PositiveIntegerField()
    points = models.PositiveIntegerField(default=1)
    
    # For multiple choice questions
    options = models.JSONField(default=list, blank=True)  # List of answer options
    correct_answer = models.CharField(max_length=500)  # Correct answer
    
    # For short answer questions
    acceptable_answers = models.JSONField(default=list, blank=True)  # List of acceptable answers
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quiz_questions'
        verbose_name = 'Quiz Question'
        verbose_name_plural = 'Quiz Questions'
        ordering = ['quiz', 'order']
        unique_together = ['quiz', 'order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class Enrollment(models.Model):
    """
    Student enrollment in courses
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    progress_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.full_name} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    """
    Track student progress through lessons
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress', limit_choices_to={'role': 'student'})
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    quiz_completed = models.BooleanField(default=False)
    quiz_completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'lesson_progress'
        verbose_name = 'Lesson Progress'
        verbose_name_plural = 'Lesson Progress'
        unique_together = ['student', 'lesson']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.lesson.title}"


class QuizAttempt(models.Model):
    """
    Student quiz attempts
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts', limit_choices_to={'role': 'student'})
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.PositiveIntegerField()
    score = models.FloatField()
    total_questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_passed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'quiz_attempts'
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'
        unique_together = ['student', 'quiz', 'attempt_number']
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.quiz.lesson.title} (Attempt {self.attempt_number})"


class QuizAnswer(models.Model):
    """
    Individual answers in quiz attempts
    """
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    points_earned = models.FloatField(default=0)
    
    class Meta:
        db_table = 'quiz_answers'
        verbose_name = 'Quiz Answer'
        verbose_name_plural = 'Quiz Answers'
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"Answer for {self.question.question_text[:30]}..."


class CourseReview(models.Model):
    """
    Student reviews for courses
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews', limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_reviews'
        verbose_name = 'Course Review'
        verbose_name_plural = 'Course Reviews'
        unique_together = ['student', 'course']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.course.title} ({self.rating} stars)"


class Payment(models.Model):
    """
    Course payment records
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='NGN')  # Nigerian Naira
    
    # Flutterwave specific fields
    flutterwave_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    flutterwave_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    flutterwave_payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Payment status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # card, bank_transfer, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)  # Store additional payment data
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.flutterwave_reference} - {self.student.full_name} - {self.course.title}"
    
    def is_successful(self):
        return self.status == 'completed'
    
    def get_amount_in_kobo(self):
        """Get amount for Flutterwave (Flutterwave v3 expects amount in main currency unit, not kobo)"""
        return float(self.amount)


class Certificate(models.Model):
    """
    Course completion certificates
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates', limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='certificates')
    certificate_id = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    image_file = models.ImageField(upload_to='certificates/', blank=True, null=True)
    is_verified = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'certificates'
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        unique_together = ['student', 'course']
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"Certificate for {self.student.full_name} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{self.id or 'NEW'}-{self.student.id}-{self.course.id}"
        super().save(*args, **kwargs)



