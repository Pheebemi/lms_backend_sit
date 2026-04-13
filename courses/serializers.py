from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Course, Lesson, Quiz, QuizQuestion,
    Enrollment, LessonProgress, QuizAttempt, QuizAnswer, CourseReview, Certificate, Payment
)

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'icon', 'created_at']


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list views (minimal data)"""
    instructor_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    preview_video_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'short_description', 'instructor_name', 'category_name',
            'price', 'is_free', 'difficulty', 'duration_hours', 'language',
            'thumbnail_url', 'preview_video_id', 'status', 'is_featured',
            'total_lessons', 'total_students', 'average_rating', 'total_ratings',
            'created_at', 'published_at'
        ]
    
    def get_instructor_name(self, obj):
        return obj.instructor.full_name
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def get_thumbnail_url(self, obj):
        return obj.get_thumbnail_url()
    
    def get_preview_video_id(self, obj):
        return obj.get_preview_video_id()


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed course views"""
    instructor_name = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    preview_video_id = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'short_description', 'instructor_name',
            'category', 'price', 'is_free', 'difficulty', 'duration_hours',
            'language', 'thumbnail_url', 'preview_video_id', 'status',
            'is_featured', 'total_lessons', 'total_students', 'average_rating',
            'total_ratings', 'lessons', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_instructor_name(self, obj):
        return obj.instructor.full_name
    
    def get_thumbnail_url(self, obj):
        return obj.get_thumbnail_url()
    
    def get_preview_video_id(self, obj):
        return obj.get_preview_video_id()
    
    def get_lessons(self, obj):
        lessons = obj.lessons.filter(is_published=True).order_by('order')
        return LessonListSerializer(lessons, many=True).data


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating courses"""
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'short_description', 'category', 'price',
            'difficulty', 'duration_hours', 'language', 'thumbnail',
            'preview_video_url', 'status', 'is_featured'
        ]
    
    def create(self, validated_data):
        # Set instructor from request user
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)


class LessonListSerializer(serializers.ModelSerializer):
    """Serializer for lesson list views"""
    video_id = serializers.SerializerMethodField()
    has_quiz = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'order', 'lesson_type', 'duration_minutes',
            'video_id', 'has_quiz', 'is_published', 'created_at'
        ]
    
    def get_video_id(self, obj):
        return obj.get_video_id()
    
    def get_has_quiz(self, obj):
        return hasattr(obj, 'quiz') and obj.quiz.is_published


class LessonDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed lesson views"""
    video_id = serializers.SerializerMethodField()
    quiz = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'order', 'content', 'video_url', 'video_id',
            'lesson_type', 'duration_minutes', 'resources', 'is_published', 'quiz',
            'created_at', 'updated_at'
        ]
    
    def get_video_id(self, obj):
        return obj.get_video_id()
    
    def get_quiz(self, obj):
        if hasattr(obj, 'quiz') and obj.quiz.is_published:
            return QuizDetailSerializer(obj.quiz).data
        return None


class LessonCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating lessons"""
    class Meta:
        model = Lesson
        fields = [
            'title', 'description', 'order', 'content', 'video_url',
            'duration_minutes', 'resources', 'is_published'
        ]
    
    def create(self, validated_data):
        # Set course from context
        validated_data['course'] = self.context['course']
        return super().create(validated_data)


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer for quiz questions"""
    class Meta:
        model = QuizQuestion
        fields = [
            'id', 'question_text', 'question_type', 'order', 'points',
            'options', 'correct_answer', 'acceptable_answers'
        ]


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed quiz views"""
    questions = QuizQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'time_limit_minutes', 'passing_score',
            'max_attempts', 'is_published', 'questions', 'created_at', 'updated_at'
        ]


class QuizCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating quizzes"""
    questions = QuizQuestionSerializer(many=True, required=False)
    
    class Meta:
        model = Quiz
        fields = [
            'title', 'description', 'time_limit_minutes', 'passing_score',
            'max_attempts', 'is_published', 'questions'
        ]
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        
        for question_data in questions_data:
            QuizQuestion.objects.create(quiz=quiz, **question_data)
        
        return quiz
    
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', [])
        
        # Update quiz fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update questions
        if questions_data:
            # Delete existing questions
            instance.questions.all().delete()
            
            # Create new questions
            for question_data in questions_data:
                QuizQuestion.objects.create(quiz=instance, **question_data)
        
        return instance


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for course enrollments"""
    course_title = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course_title', 'student_name', 'enrolled_at',
            'completed_at', 'is_completed', 'progress_percentage'
        ]
        read_only_fields = ['enrolled_at', 'completed_at']
    
    def get_course_title(self, obj):
        return obj.course.title
    
    def get_student_name(self, obj):
        return obj.student.full_name


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for lesson progress"""
    lesson_title = serializers.SerializerMethodField()
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson_title', 'is_completed', 'completed_at',
            'time_spent_minutes'
        ]
        read_only_fields = ['completed_at']
    
    def get_lesson_title(self, obj):
        return obj.lesson.title


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for student enrollments with course and progress data"""
    course = CourseDetailSerializer(read_only=True)
    lesson_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'enrolled_at', 'completed_at', 
            'is_completed', 'progress_percentage', 'lesson_progress'
        ]
        read_only_fields = ['enrolled_at', 'completed_at']
    
    def get_lesson_progress(self, obj):
        # Get lesson progress for lessons in this course
        course_lessons = obj.course.lessons.all()
        lesson_progress = []
        
        for lesson in course_lessons:
            progress = lesson.progress.filter(student=obj.student).first()
            if progress:
                lesson_progress.append({
                    'lesson_id': lesson.id,
                    'lesson_title': lesson.title,
                    'is_completed': progress.is_completed,
                    'completed_at': progress.completed_at,
                    'time_spent_minutes': progress.time_spent_minutes,
                    'quiz_completed': progress.quiz_completed,
                    'quiz_completed_at': progress.quiz_completed_at
                })
            else:
                lesson_progress.append({
                    'lesson_id': lesson.id,
                    'lesson_title': lesson.title,
                    'is_completed': False,
                    'completed_at': None,
                    'time_spent_minutes': 0,
                    'quiz_completed': False,
                    'quiz_completed_at': None
                })
        
        return lesson_progress


class QuizAnswerSerializer(serializers.ModelSerializer):
    """Serializer for quiz answers"""
    question_text = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAnswer
        fields = [
            'id', 'question_text', 'answer_text', 'is_correct', 'points_earned'
        ]
        read_only_fields = ['is_correct', 'points_earned']
    
    def get_question_text(self, obj):
        return obj.question.question_text


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for quiz attempts"""
    quiz_title = serializers.SerializerMethodField()
    answers = QuizAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz_title', 'attempt_number', 'score', 'total_questions',
            'correct_answers', 'started_at', 'completed_at', 'is_passed', 'answers'
        ]
        read_only_fields = ['started_at', 'completed_at', 'is_passed']
    
    def get_quiz_title(self, obj):
        return obj.quiz.lesson.title


class CourseReviewSerializer(serializers.ModelSerializer):
    """Serializer for course reviews"""
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseReview
        fields = [
            'id', 'student_name', 'rating', 'review_text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.full_name


class CourseEnrollmentSerializer(serializers.Serializer):
    """Serializer for enrolling in a course"""
    course_id = serializers.UUIDField()
    
    def validate_course_id(self, value):
        try:
            course = Course.objects.get(id=value, status='published')
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found or not published")
        return value


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for certificates"""
    course = CourseListSerializer(read_only=True)
    student = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id',
            'certificate_id',
            'student',
            'course',
            'enrollment',
            'issued_at',
            'pdf_file',
            'image_file',
            'image_file_url',
            'is_verified'
        ]
        read_only_fields = ['certificate_id', 'issued_at']
    
    image_file_url = serializers.SerializerMethodField()
    
    def get_image_file_url(self, obj):
        """Return the full URL for the certificate image"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                try:
                    # Use the regular media URL - Django should serve it correctly
                    media_url = request.build_absolute_uri(obj.image_file.url)
                    return media_url
                except Exception:
                    # Fallback: construct URL manually if build_absolute_uri fails
                    from django.conf import settings
                    if hasattr(obj.image_file, 'url'):
                        file_url = obj.image_file.url
                        if file_url.startswith('http'):
                            return file_url
                        # Construct absolute URL
                        scheme = request.scheme
                        host = request.get_host()
                        return f"{scheme}://{host}{file_url}"
            # Fallback to relative URL
            return obj.image_file.url if hasattr(obj.image_file, 'url') else None
        return None


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for submitting quiz answers"""
    answers = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_answers(self, value):
        for answer in value:
            if 'question_id' not in answer or 'answer_text' not in answer:
                raise serializers.ValidationError("Each answer must have question_id and answer_text")
        return value


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for certificates"""
    course = CourseListSerializer(read_only=True)
    student = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id',
            'certificate_id',
            'student',
            'course',
            'enrollment',
            'issued_at',
            'pdf_file',
            'image_file',
            'image_file_url',
            'is_verified'
        ]
        read_only_fields = ['certificate_id', 'issued_at']
    
    image_file_url = serializers.SerializerMethodField()
    
    def get_image_file_url(self, obj):
        """Return the full URL for the certificate image"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                try:
                    # Use the regular media URL - Django should serve it correctly
                    media_url = request.build_absolute_uri(obj.image_file.url)
                    return media_url
                except Exception:
                    # Fallback: construct URL manually if build_absolute_uri fails
                    from django.conf import settings
                    if hasattr(obj.image_file, 'url'):
                        file_url = obj.image_file.url
                        if file_url.startswith('http'):
                            return file_url
                        # Construct absolute URL
                        scheme = request.scheme
                        host = request.get_host()
                        return f"{scheme}://{host}{file_url}"
            # Fallback to relative URL
            return obj.image_file.url if hasattr(obj.image_file, 'url') else None
        return None


    """Serializer for detailed quiz views"""

    questions = QuizQuestionSerializer(many=True, read_only=True)

    

    class Meta:

        model = Quiz

        fields = [

            'id', 'title', 'description', 'time_limit_minutes', 'passing_score',

            'max_attempts', 'is_published', 'questions', 'created_at', 'updated_at'

        ]










class EnrollmentSerializer(serializers.ModelSerializer):

    """Serializer for course enrollments"""

    course_title = serializers.SerializerMethodField()

    student_name = serializers.SerializerMethodField()

    

    class Meta:

        model = Enrollment

        fields = [

            'id', 'course_title', 'student_name', 'enrolled_at',

            'completed_at', 'is_completed', 'progress_percentage'

        ]

        read_only_fields = ['enrolled_at', 'completed_at']

    

    def get_course_title(self, obj):

        return obj.course.title

    

    def get_student_name(self, obj):
        return obj.student.full_name






class LessonProgressSerializer(serializers.ModelSerializer):

    """Serializer for lesson progress"""

    lesson_title = serializers.SerializerMethodField()

    

    class Meta:

        model = LessonProgress

        fields = [

            'id', 'lesson_title', 'is_completed', 'completed_at',

            'time_spent_minutes'

        ]

        read_only_fields = ['completed_at']

    

    def get_lesson_title(self, obj):

        return obj.lesson.title





class QuizAnswerSerializer(serializers.ModelSerializer):

    """Serializer for quiz answers"""

    question_text = serializers.SerializerMethodField()

    

    class Meta:

        model = QuizAnswer

        fields = [

            'id', 'question_text', 'answer_text', 'is_correct', 'points_earned'

        ]

        read_only_fields = ['is_correct', 'points_earned']

    

    def get_question_text(self, obj):

        return obj.question.question_text





class QuizAttemptSerializer(serializers.ModelSerializer):

    """Serializer for quiz attempts"""

    quiz_title = serializers.SerializerMethodField()

    answers = QuizAnswerSerializer(many=True, read_only=True)

    

    class Meta:

        model = QuizAttempt

        fields = [

            'id', 'quiz_title', 'attempt_number', 'score', 'total_questions',

            'correct_answers', 'started_at', 'completed_at', 'is_passed', 'answers'

        ]

        read_only_fields = ['started_at', 'completed_at', 'is_passed']

    

    def get_quiz_title(self, obj):

        return obj.quiz.lesson.title





class CourseReviewSerializer(serializers.ModelSerializer):

    """Serializer for course reviews"""

    student_name = serializers.SerializerMethodField()

    

    class Meta:

        model = CourseReview

        fields = [

            'id', 'student_name', 'rating', 'review_text', 'created_at', 'updated_at'

        ]

        read_only_fields = ['created_at', 'updated_at']

    

    def get_student_name(self, obj):
        return obj.student.full_name






class CourseEnrollmentSerializer(serializers.Serializer):

    """Serializer for enrolling in a course"""

    course_id = serializers.UUIDField()

    

    def validate_course_id(self, value):

        try:

            course = Course.objects.get(id=value, status='published')

        except Course.DoesNotExist:

            raise serializers.ValidationError("Course not found or not published")

        return value


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for certificates"""
    course = CourseListSerializer(read_only=True)
    student = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id',
            'certificate_id',
            'student',
            'course',
            'enrollment',
            'issued_at',
            'pdf_file',
            'image_file',
            'image_file_url',
            'is_verified'
        ]
        read_only_fields = ['certificate_id', 'issued_at']
    
    image_file_url = serializers.SerializerMethodField()
    
    def get_image_file_url(self, obj):
        """Return the full URL for the certificate image"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                try:
                    # Use the regular media URL - Django should serve it correctly
                    media_url = request.build_absolute_uri(obj.image_file.url)
                    return media_url
                except Exception:
                    # Fallback: construct URL manually if build_absolute_uri fails
                    from django.conf import settings
                    if hasattr(obj.image_file, 'url'):
                        file_url = obj.image_file.url
                        if file_url.startswith('http'):
                            return file_url
                        # Construct absolute URL
                        scheme = request.scheme
                        host = request.get_host()
                        return f"{scheme}://{host}{file_url}"
            # Fallback to relative URL
            return obj.image_file.url if hasattr(obj.image_file, 'url') else None
        return None















class CourseEnrollmentSerializer(serializers.Serializer):


    """Serializer for enrolling in a course"""


    course_id = serializers.UUIDField()


    
    
    def validate_course_id(self, value):


        try:


            course = Course.objects.get(id=value, status='published')

        except Course.DoesNotExist:

            raise serializers.ValidationError("Course not found or not published")

        return value


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for certificates"""
    course = CourseListSerializer(read_only=True)
    student = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id',
            'certificate_id',
            'student',
            'course',
            'enrollment',
            'issued_at',
            'pdf_file',
            'image_file',
            'image_file_url',
            'is_verified'
        ]
        read_only_fields = ['certificate_id', 'issued_at']
    
    image_file_url = serializers.SerializerMethodField()
    
    def get_image_file_url(self, obj):
        """Return the full URL for the certificate image"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                try:
                    # Use the regular media URL - Django should serve it correctly
                    media_url = request.build_absolute_uri(obj.image_file.url)
                    return media_url
                except Exception:
                    # Fallback: construct URL manually if build_absolute_uri fails
                    from django.conf import settings
                    if hasattr(obj.image_file, 'url'):
                        file_url = obj.image_file.url
                        if file_url.startswith('http'):
                            return file_url
                        # Construct absolute URL
                        scheme = request.scheme
                        host = request.get_host()
                        return f"{scheme}://{host}{file_url}"
            # Fallback to relative URL
            return obj.image_file.url if hasattr(obj.image_file, 'url') else None
        return None









