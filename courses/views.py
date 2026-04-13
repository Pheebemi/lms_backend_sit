from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    Category, Course, Lesson, Quiz, QuizQuestion,
    Enrollment, LessonProgress, QuizAttempt, QuizAnswer, CourseReview, Certificate
)
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer, CourseCreateUpdateSerializer,
    LessonListSerializer, LessonDetailSerializer, LessonCreateUpdateSerializer,
    QuizDetailSerializer, QuizCreateUpdateSerializer,
    EnrollmentSerializer, StudentEnrollmentSerializer, LessonProgressSerializer, QuizAttemptSerializer,
    CourseReviewSerializer, CourseEnrollmentSerializer, QuizSubmissionSerializer, CertificateSerializer
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


# Category Views
class CategoryListAPIView(generics.ListAPIView):
    """List all categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# Course Views
class CourseListAPIView(generics.ListAPIView):
    """List all published courses with filtering and search"""
    serializer_class = CourseListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published').select_related('instructor', 'category')
        
        # Filtering
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        is_free = self.request.query_params.get('is_free')
        if is_free is not None:
            queryset = queryset.filter(is_free=is_free.lower() == 'true')
        
        is_featured = self.request.query_params.get('is_featured')
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(short_description__icontains=search) |
                Q(instructor__first_name__icontains=search) |
                Q(instructor__last_name__icontains=search)
            )
        
        # Sorting
        sort_by = self.request.query_params.get('sort_by', 'created_at')
        if sort_by == 'rating':
            queryset = queryset.order_by('-average_rating', '-total_ratings')
        elif sort_by == 'students':
            queryset = queryset.order_by('-total_students')
        elif sort_by == 'price':
            queryset = queryset.order_by('price')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset


class CourseDetailAPIView(generics.RetrieveAPIView):
    """Get detailed course information"""
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Course.objects.filter(status='published').select_related('instructor', 'category').prefetch_related('lessons')


class CourseCreateAPIView(generics.CreateAPIView):
    """Create a new course (tutors only)"""
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        if not self.request.user.is_tutor():
            raise PermissionDenied('Only tutors can create courses')
        serializer.save(instructor=self.request.user)


class CourseUpdateAPIView(generics.UpdateAPIView):
    """Update course (tutors only, own courses)"""
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class CourseDeleteAPIView(generics.DestroyAPIView):
    """Delete course (tutors only, own courses)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


# Lesson Views
class LessonListAPIView(generics.ListAPIView):
    """List lessons for a specific course"""
    serializer_class = LessonListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Lesson.objects.filter(
            course_id=course_id, 
            is_published=True
        ).order_by('order')


class LessonDetailAPIView(generics.RetrieveAPIView):
    """Get detailed lesson information"""
    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Lesson.objects.filter(is_published=True).select_related('course')


class LessonCreateAPIView(generics.CreateAPIView):
    """Create a new lesson (tutors only, own courses)"""
    serializer_class = LessonCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id, instructor=self.request.user)
        context['course'] = course
        return context


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Update lesson (tutors only, own courses)"""
    serializer_class = LessonCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Lesson.objects.filter(course__instructor=self.request.user)


class LessonDeleteAPIView(generics.DestroyAPIView):
    """Delete lesson (tutors only, own courses)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Lesson.objects.filter(course__instructor=self.request.user)


# Quiz Views
class QuizDetailAPIView(generics.RetrieveAPIView):
    """Get quiz details for a lesson"""
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Quiz.objects.filter(is_published=True).prefetch_related('questions')


class QuizCreateAPIView(generics.CreateAPIView):
    """Create quiz for a lesson (tutors only)"""
    serializer_class = QuizCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        lesson_id = self.kwargs['lesson_id']
        lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=self.request.user)
        context['lesson'] = lesson
        return context
    
    def perform_create(self, serializer):
        lesson_id = self.kwargs['lesson_id']
        lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=self.request.user)
        serializer.save(lesson=lesson)


class QuizUpdateAPIView(generics.UpdateAPIView):
    """Update quiz (tutors only, own courses)"""
    serializer_class = QuizCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Quiz.objects.filter(lesson__course__instructor=self.request.user)


# Enrollment Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enroll_in_course(request):
    """Enroll student in a course"""
    if not request.user.is_student():
        return Response(
            {'error': 'Only students can enroll in courses'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = CourseEnrollmentSerializer(data=request.data)
    if serializer.is_valid():
        course_id = serializer.validated_data['course_id']
        course = get_object_or_404(Course, id=course_id, status='published')
        
        # Check if already enrolled
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'enrolled_at': timezone.now()}
        )
        
        if created:
            return Response(
                {'message': 'Successfully enrolled in course'}, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Already enrolled in this course'}, 
                status=status.HTTP_200_OK
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_enrollments(request):
    """Get student's enrolled courses"""
    if not request.user.is_student():
        return Response(
            {'error': 'Only students can view enrollments'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    serializer = StudentEnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)


# Lesson Progress Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as completed for a student"""
    if not request.user.is_student():
        return Response(
            {'error': 'Only students can mark lessons complete'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    lesson = get_object_or_404(Lesson, id=lesson_id, is_published=True)
    
    # Check if student is enrolled in the course
    enrollment = get_object_or_404(
        Enrollment, 
        student=request.user, 
        course=lesson.course
    )
    
    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
        defaults={
            'is_completed': True,
            'completed_at': timezone.now()
        }
    )
    
    if not created and not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
    
    # Update course progress
    total_lessons = lesson.course.lessons.filter(is_published=True).count()
    completed_lessons = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=lesson.course,
        is_completed=True
    ).count()
    
    progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    enrollment.progress_percentage = progress_percentage
    enrollment.is_completed = progress_percentage == 100
    if enrollment.is_completed:
        enrollment.completed_at = timezone.now()
    enrollment.save()
    
    return Response({'message': 'Lesson marked as completed'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_lesson_progress(request, course_id):
    """Get student's progress for a course"""
    if not request.user.is_student():
        return Response(
            {'error': 'Only students can view progress'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    progress = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=course
    ).select_related('lesson')
    
    serializer = LessonProgressSerializer(progress, many=True)
    return Response({
        'enrollment': EnrollmentSerializer(enrollment).data,
        'progress': serializer.data
    })


# Quiz Attempt Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_quiz(request, quiz_id):
    """Submit quiz answers"""
    if not request.user.is_student():
        return Response(
            {'error': 'Only students can submit quizzes'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    quiz = get_object_or_404(Quiz, id=quiz_id, is_published=True)
    
    # Check if student is enrolled in the course
    enrollment = get_object_or_404(
        Enrollment, 
        student=request.user, 
        course=quiz.lesson.course
    )
    
    # Check attempt limit
    attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz).count()
    if attempts >= quiz.max_attempts:
        return Response(
            {'error': 'Maximum attempts reached'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = QuizSubmissionSerializer(data=request.data)
    if serializer.is_valid():
        answers_data = serializer.validated_data['answers']
        
        correct_answers = 0
        total_points = 0
        earned_points = 0
        
        # Process answers first to calculate score
        for answer_data in answers_data:
            question = get_object_or_404(QuizQuestion, id=answer_data['question_id'], quiz=quiz)
            answer_text = answer_data['answer_text']
            
            is_correct = False
            points_earned = 0
            
            if question.question_type == 'multiple_choice':
                is_correct = answer_text == question.correct_answer
            elif question.question_type == 'true_false':
                is_correct = answer_text.lower() == question.correct_answer.lower()
            elif question.question_type == 'short_answer':
                is_correct = answer_text.lower() in [ans.lower() for ans in question.acceptable_answers]
            
            if is_correct:
                points_earned = question.points
                correct_answers += 1
            
            total_points += question.points
            earned_points += points_earned
        
        # Calculate score
        score = (earned_points / total_points) * 100 if total_points > 0 else 0
        
        # Create quiz attempt with all required fields
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            attempt_number=attempts + 1,
            score=score,
            total_questions=quiz.questions.count(),
            correct_answers=correct_answers,
            completed_at=timezone.now(),
            is_passed=score >= quiz.passing_score
        )
        
        # Create quiz answers
        for answer_data in answers_data:
            question = get_object_or_404(QuizQuestion, id=answer_data['question_id'], quiz=quiz)
            answer_text = answer_data['answer_text']
            
            is_correct = False
            points_earned = 0
            
            if question.question_type == 'multiple_choice':
                is_correct = answer_text == question.correct_answer
            elif question.question_type == 'true_false':
                is_correct = answer_text.lower() == question.correct_answer.lower()
            elif question.question_type == 'short_answer':
                is_correct = answer_text.lower() in [ans.lower() for ans in question.acceptable_answers]
            
            if is_correct:
                points_earned = question.points
            
            QuizAnswer.objects.create(
                attempt=attempt,
                question=question,
                answer_text=answer_text,
                is_correct=is_correct,
                points_earned=points_earned
            )
        
        # Update lesson progress to mark quiz as completed
        lesson_progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=quiz.lesson,
            defaults={
                'quiz_completed': True,
                'quiz_completed_at': timezone.now()
            }
        )
        
        if not created:
            lesson_progress.quiz_completed = True
            lesson_progress.quiz_completed_at = timezone.now()
            lesson_progress.save()
        
        return Response({
            'message': 'Quiz submitted successfully',
            'score': score,
            'passed': attempt.is_passed,
            'correct_answers': correct_answers,
            'total_questions': attempt.total_questions
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_quiz_attempts(request, quiz_id):
    """Get student's quiz attempts"""
    if not request.user.is_student():
        return Response(
            {'error': 'Only students can view quiz attempts'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    quiz = get_object_or_404(Quiz, id=quiz_id, is_published=True)
    attempts = QuizAttempt.objects.filter(
        student=request.user, 
        quiz=quiz
    ).prefetch_related('answers__question')
    
    serializer = QuizAttemptSerializer(attempts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def auto_generate_quiz(request, course_id, lesson_id):
    """Auto-generate quiz for a lesson"""
    if not request.user.is_tutor():
        return Response(
            {'error': 'Only tutors can generate quizzes'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id, course__instructor=request.user)

        # Check if lesson already has a quiz
        if hasattr(lesson, 'quiz'):
            return Response(
                {'error': 'Lesson already has a quiz'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get parameters from request
        num_questions = request.data.get('num_questions', 5)
        difficulty = request.data.get('difficulty', 'medium')

        # Validate parameters
        if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 20:
            return Response(
                {'error': 'Number of questions must be between 1 and 20'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if difficulty not in ['easy', 'medium', 'hard']:
            return Response(
                {'error': 'Difficulty must be easy, medium, or hard'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Import the quiz generation logic
        from .management.commands.generate_quiz import Command
        cmd = Command()

        # Generate the quiz
        quiz = cmd.create_quiz_for_lesson(lesson, num_questions, difficulty)

        # Return the created quiz data
        serializer = QuizDetailSerializer(quiz)
        return Response({
            'message': f'Quiz generated successfully with {num_questions} questions',
            'quiz': serializer.data
        }, status=status.HTTP_201_CREATED)

    except Lesson.DoesNotExist:
        return Response(
            {'error': 'Lesson not found or you do not have permission to modify it'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to generate quiz: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


# Course Review Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_course_review(request, course_id):
    """Create or update course review"""
    if not request.user.is_student():
        return Response(
            {'error': 'Only students can create reviews'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    course = get_object_or_404(Course, id=course_id, status='published')
    
    # Check if student is enrolled and completed the course
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    if not enrollment.is_completed:
        return Response(
            {'error': 'Must complete course before reviewing'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    review, created = CourseReview.objects.get_or_create(
        student=request.user,
        course=course,
        defaults=request.data
    )
    
    if not created:
        serializer = CourseReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Update course rating
    reviews = CourseReview.objects.filter(course=course)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    course.average_rating = round(avg_rating, 1)
    course.total_ratings = reviews.count()
    course.save()
    
    return Response(
        {'message': 'Review created successfully'}, 
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_course_reviews(request, course_id):
    """Get course reviews"""
    course = get_object_or_404(Course, id=course_id)
    reviews = CourseReview.objects.filter(course=course).select_related('student')
    serializer = CourseReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# Tutor Dashboard Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_tutor_courses(request):
    """Get tutor's courses with statistics"""
    if not request.user.is_tutor():
        return Response(
            {'error': 'Only tutors can view this data'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    courses = Course.objects.filter(instructor=request.user).annotate(
        total_enrollments=Count('enrollments'),
        total_reviews=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    )
    
    serializer = CourseListSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_tutor_course_detail(request, course_id):
    """Get detailed course information for tutor's own course"""
    if not request.user.is_tutor():
        return Response(
            {'error': 'Only tutors can view this data'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    serializer = CourseDetailSerializer(course)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_tutor_lesson_detail(request, course_id, lesson_id):
    """Get detailed lesson information for tutor's own lesson"""
    if not request.user.is_tutor():
        return Response(
            {'error': 'Only tutors can view this data'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    serializer = LessonDetailSerializer(lesson)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_tutor_course_stats(request, course_id):
    """Get detailed statistics for a tutor's course"""
    if not request.user.is_tutor():
        return Response(
            {'error': 'Only tutors can view this data'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    stats = {
        'course': CourseDetailSerializer(course).data,
        'total_enrollments': course.enrollments.count(),
        'completed_enrollments': course.enrollments.filter(is_completed=True).count(),
        'average_progress': course.enrollments.aggregate(Avg('progress_percentage'))['progress_percentage__avg'] or 0,
        'recent_enrollments': EnrollmentSerializer(
            course.enrollments.order_by('-enrolled_at')[:5], 
            many=True
        ).data,
        'recent_reviews': CourseReviewSerializer(
            course.reviews.order_by('-created_at')[:5], 
            many=True
        ).data
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_certificates(request):
    """Get all certificates for the authenticated student"""
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can access certificates'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    certificates = Certificate.objects.filter(
        student=request.user
    ).select_related('course', 'enrollment').order_by('-issued_at')
    
    serializer = CertificateSerializer(certificates, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_certificate(request, enrollment_id):
    """Generate a certificate for a completed course"""
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can generate certificates'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        enrollment = get_object_or_404(
            Enrollment,
            id=enrollment_id,
            student=request.user,
            is_completed=True
        )
        
        # Check if certificate already exists
        certificate, created = Certificate.objects.get_or_create(
            student=request.user,
            course=enrollment.course,
            enrollment=enrollment,
            defaults={
                'certificate_id': f"C{abs(hash(str(enrollment.id))) % 10000:04d}"  # 5 characters: C + 4-digit number
            }
        )
        
        # Generate PNG certificate image if it doesn't exist or if newly created
        if not certificate.image_file or created:
            from .certificate_generator import save_certificate_image
            
            student_name = f"{request.user.first_name} {request.user.last_name}"
            certificate_id = certificate.certificate_id
            
            save_certificate_image(
                certificate=certificate,
                student_name=student_name,
                course_title=enrollment.course.title,
                certificate_id=certificate_id,
                issued_date=certificate.issued_at,
                completed_date=enrollment.completed_at
            )
        
        serializer = CertificateSerializer(certificate, context={'request': request})
        
        if created:
            return Response({
                'message': 'Certificate generated successfully',
                'certificate': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Certificate already exists',
                'certificate': serializer.data
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        import traceback
        return Response(
            {'error': str(e), 'traceback': traceback.format_exc()},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_certificate_detail(request, certificate_id):
    """Get details of a specific certificate"""
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can access certificates'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        certificate = get_object_or_404(
            Certificate,
            id=certificate_id,
            student=request.user
        )
        
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_tutor_dashboard_stats(request):
    """Get tutor dashboard statistics"""
    if not request.user.is_tutor():
        return Response(
            {'error': 'Only tutors can view this data'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get tutor's courses
    courses = Course.objects.filter(instructor=request.user)
    
    # Calculate total statistics
    total_courses = courses.count()
    total_students = sum(course.total_students for course in courses)
    total_earnings = sum(course.price * course.total_students for course in courses if not course.is_free)
    
    # Calculate average rating across all courses
    all_ratings = []
    for course in courses:
        if course.average_rating > 0:
            all_ratings.append(course.average_rating)
    average_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0
    
    # Get recent enrollments across all courses
    recent_enrollments = Enrollment.objects.filter(
        course__instructor=request.user
    ).select_related('student', 'course').order_by('-enrolled_at')[:10]
    
    # Get recent reviews across all courses
    recent_reviews = CourseReview.objects.filter(
        course__instructor=request.user
    ).select_related('student', 'course').order_by('-created_at')[:10]
    
    stats = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_earnings': total_earnings,
        'average_rating': round(average_rating, 1),
        'recent_enrollments': EnrollmentSerializer(recent_enrollments, many=True).data,
        'recent_reviews': CourseReviewSerializer(recent_reviews, many=True).data
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_certificates(request):
    """Get all certificates for the authenticated student"""
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can access certificates'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    certificates = Certificate.objects.filter(
        student=request.user
    ).select_related('course', 'enrollment').order_by('-issued_at')
    
    serializer = CertificateSerializer(certificates, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_certificate(request, enrollment_id):
    """Generate a certificate for a completed course"""
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can generate certificates'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        enrollment = get_object_or_404(
            Enrollment,
            id=enrollment_id,
            student=request.user,
            is_completed=True
        )
        
        # Check if certificate already exists
        certificate, created = Certificate.objects.get_or_create(
            student=request.user,
            course=enrollment.course,
            enrollment=enrollment,
            defaults={
                'certificate_id': f"C{abs(hash(str(enrollment.id))) % 10000:04d}"  # 5 characters: C + 4-digit number
            }
        )
        
        # Generate PNG certificate image if it doesn't exist or if newly created
        if not certificate.image_file or created:
            from .certificate_generator import save_certificate_image
            
            student_name = f"{request.user.first_name} {request.user.last_name}"
            certificate_id = certificate.certificate_id
            
            save_certificate_image(
                certificate=certificate,
                student_name=student_name,
                course_title=enrollment.course.title,
                certificate_id=certificate_id,
                issued_date=certificate.issued_at,
                completed_date=enrollment.completed_at
            )
        
        serializer = CertificateSerializer(certificate, context={'request': request})
        
        if created:
            return Response({
                'message': 'Certificate generated successfully',
                'certificate': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Certificate already exists',
                'certificate': serializer.data
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        import traceback
        return Response(
            {'error': str(e), 'traceback': traceback.format_exc()},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_certificate_detail(request, certificate_id):
    """Get details of a specific certificate"""
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can access certificates'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        certificate = get_object_or_404(
            Certificate,
            id=certificate_id,
            student=request.user
        )
        
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_dashboard_stats(request):
    """Get student dashboard statistics"""
    if not request.user.is_student():
        return Response(
            {'error': 'Only students can view this data'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get student's enrollments
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    # Calculate statistics
    total_enrollments = enrollments.count()
    completed_courses = enrollments.filter(is_completed=True).count()
    
    # Calculate total study hours (sum of course durations)
    total_study_hours = sum(enrollment.course.duration_hours for enrollment in enrollments)
    
    # Calculate average progress
    progress_values = [enrollment.progress_percentage for enrollment in enrollments]
    average_progress = sum(progress_values) / len(progress_values) if progress_values else 0
    
    # Get recent activity (lesson progress)
    recent_activity = LessonProgress.objects.filter(
        student=request.user
    ).select_related('lesson__course').order_by('-completed_at')[:10]
    
    # Get upcoming lessons (next lessons in enrolled courses)
    upcoming_lessons = []
    for enrollment in enrollments.filter(is_completed=False):
        next_lesson = enrollment.course.lessons.filter(
            is_published=True,
            order__gt=enrollment.progress_percentage / 100 * enrollment.course.lessons.count()
        ).order_by('order').first()
        if next_lesson:
            upcoming_lessons.append({
                'lesson': LessonListSerializer(next_lesson).data,
                'course': CourseListSerializer(enrollment.course).data,
                'enrollment': EnrollmentSerializer(enrollment).data
            })
    
    stats = {
        'total_enrollments': total_enrollments,
        'completed_courses': completed_courses,
        'total_study_hours': total_study_hours,
        'average_progress': round(average_progress, 1),
        'recent_activity': LessonProgressSerializer(recent_activity, many=True).data,
        'upcoming_lessons': upcoming_lessons[:5]  # Limit to 5 upcoming lessons
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_certificates(request):
    """Get all certificates for the authenticated student"""
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can access certificates'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    certificates = Certificate.objects.filter(
        student=request.user
    ).select_related('course', 'enrollment').order_by('-issued_at')
    
    serializer = CertificateSerializer(certificates, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_certificate(request, enrollment_id):
    """Generate a certificate for a completed course"""
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can generate certificates'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        enrollment = get_object_or_404(
            Enrollment,
            id=enrollment_id,
            student=request.user,
            is_completed=True
        )
        
        # Check if certificate already exists
        certificate, created = Certificate.objects.get_or_create(
            student=request.user,
            course=enrollment.course,
            enrollment=enrollment,
            defaults={
                'certificate_id': f"C{abs(hash(str(enrollment.id))) % 10000:04d}"  # 5 characters: C + 4-digit number
            }
        )
        
        # Generate PNG certificate image if it doesn't exist or if newly created
        if not certificate.image_file or created:
            from .certificate_generator import save_certificate_image
            
            student_name = f"{request.user.first_name} {request.user.last_name}"
            certificate_id = certificate.certificate_id
            
            save_certificate_image(
                certificate=certificate,
                student_name=student_name,
                course_title=enrollment.course.title,
                certificate_id=certificate_id,
                issued_date=certificate.issued_at,
                completed_date=enrollment.completed_at
            )
        
        serializer = CertificateSerializer(certificate, context={'request': request})
        
        if created:
            return Response({
                'message': 'Certificate generated successfully',
                'certificate': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Certificate already exists',
                'certificate': serializer.data
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        import traceback
        return Response(
            {'error': str(e), 'traceback': traceback.format_exc()},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_certificate_detail(request, certificate_id):
    """Get details of a specific certificate"""
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can access certificates'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        certificate = get_object_or_404(
            Certificate,
            id=certificate_id,
            student=request.user
        )
        
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

