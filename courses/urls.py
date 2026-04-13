from django.urls import path, re_path
from . import views
from . import certificate_views
from . import payment_views
from . import mock_payment_views

app_name = 'courses'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListAPIView.as_view(), name='category-list'),
    
    # Courses
    path('courses/', views.CourseListAPIView.as_view(), name='course-list'),
    path('courses/<uuid:pk>/', views.CourseDetailAPIView.as_view(), name='course-detail'),
    path('courses/create/', views.CourseCreateAPIView.as_view(), name='course-create'),
    path('courses/<uuid:pk>/update/', views.CourseUpdateAPIView.as_view(), name='course-update'),
    path('courses/<uuid:pk>/delete/', views.CourseDeleteAPIView.as_view(), name='course-delete'),
    
    # Lessons
    path('courses/<uuid:course_id>/lessons/', views.LessonListAPIView.as_view(), name='lesson-list'),
    path('lessons/<uuid:pk>/', views.LessonDetailAPIView.as_view(), name='lesson-detail'),
    path('courses/<uuid:course_id>/lessons/create/', views.LessonCreateAPIView.as_view(), name='lesson-create'),
    path('lessons/<uuid:pk>/update/', views.LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lessons/<uuid:pk>/delete/', views.LessonDeleteAPIView.as_view(), name='lesson-delete'),
    
    # Quizzes
    path('quizzes/<int:pk>/', views.QuizDetailAPIView.as_view(), name='quiz-detail'),
    path('lessons/<uuid:lesson_id>/quiz/create/', views.QuizCreateAPIView.as_view(), name='quiz-create'),
    path('quizzes/<int:pk>/update/', views.QuizUpdateAPIView.as_view(), name='quiz-update'),
    
    # Enrollment
    path('enroll/', views.enroll_in_course, name='enroll-course'),
    path('enrollments/', views.get_student_enrollments, name='student-enrollments'),
    
    # Progress
    path('lessons/<uuid:lesson_id>/complete/', views.mark_lesson_complete, name='mark-lesson-complete'),
    path('courses/<uuid:course_id>/progress/', views.get_lesson_progress, name='lesson-progress'),
    
    # Quiz Attempts
    path('quizzes/<int:quiz_id>/submit/', views.submit_quiz, name='submit-quiz'),
    path('quizzes/<int:quiz_id>/attempts/', views.get_quiz_attempts, name='quiz-attempts'),
    
    # Reviews
    path('courses/<uuid:course_id>/reviews/', views.get_course_reviews, name='course-reviews'),
    path('courses/<uuid:course_id>/review/', views.create_course_review, name='create-review'),
    
    # Tutor Dashboard
    path('tutor/courses/', views.get_tutor_courses, name='tutor-courses'),
    path('tutor/courses/<uuid:course_id>/', views.get_tutor_course_detail, name='tutor-course-detail'),
    path('tutor/courses/<uuid:course_id>/lessons/<uuid:lesson_id>/', views.get_tutor_lesson_detail, name='tutor-lesson-detail'),
    path('tutor/courses/<uuid:course_id>/lessons/<uuid:lesson_id>/generate-quiz/', views.auto_generate_quiz, name='auto-generate-quiz'),
    path('tutor/courses/<uuid:course_id>/stats/', views.get_tutor_course_stats, name='tutor-course-stats'),
    path('tutor/dashboard/', views.get_tutor_dashboard_stats, name='tutor-dashboard-stats'),
    
    # Student Dashboard
    path('student/dashboard/', views.get_student_dashboard_stats, name='student-dashboard-stats'),
    path('student/enrollments/', views.get_student_enrollments, name='student-enrollments'),
    
    # Certificates
    path('student/certificates/', views.get_student_certificates, name='student-certificates'),
    path('student/certificates/generate/<int:enrollment_id>/', views.generate_certificate, name='generate-certificate'),
    path('student/certificates/<int:certificate_id>/', views.get_certificate_detail, name='certificate-detail'),
    
    # Certificate Images (serve with proper headers)
    re_path(r'^certificates/images/(?P<path>.*)$', certificate_views.serve_certificate_image, name='certificate-image'),
    
    # Payments
    path('payments/initiate/', payment_views.initiate_payment, name='initiate-payment'),
    path('payments/verify/', payment_views.verify_payment, name='verify-payment'),
    path('payments/history/', payment_views.payment_history, name='payment-history'),
    path('payments/<uuid:payment_id>/status/', payment_views.payment_status, name='payment-status'),
    
    # Mock Payments (for local development)
    path('mock-payments/initiate/', mock_payment_views.mock_initiate_payment, name='mock-initiate-payment'),
    path('mock-payments/verify/', mock_payment_views.mock_verify_payment, name='mock-verify-payment'),
]




















































