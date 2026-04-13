from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.models import StudentProfile, TutorProfile, AdminProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample users for testing'

    def handle(self, *args, **options):
        # Create sample admin
        admin_user, created = User.objects.get_or_create(
            email='admin@lms.com',
            defaults={
                'username': 'admin',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            AdminProfile.objects.create(
                user=admin_user,
                employee_id='ADM000001',
                hire_date='2024-01-01',
                department='IT',
                position='System Administrator',
                permissions_level='super'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {admin_user.email}')
            )

        # Create sample tutor
        tutor_user, created = User.objects.get_or_create(
            email='tutor@lms.com',
            defaults={
                'username': 'tutor',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'tutor',
                'is_verified': True,
            }
        )
        if created:
            tutor_user.set_password('tutor123')
            tutor_user.save()
            TutorProfile.objects.create(
                user=tutor_user,
                employee_id='TUT000001',
                hire_date='2024-01-01',
                department='Computer Science',
                specialization='Web Development, Python, Django',
                bio='Experienced software developer and educator',
                hourly_rate=50.00
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created tutor user: {tutor_user.email}')
            )

        # Create sample student
        student_user, created = User.objects.get_or_create(
            email='student@lms.com',
            defaults={
                'username': 'student',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'role': 'student',
                'is_verified': True,
            }
        )
        if created:
            student_user.set_password('student123')
            student_user.save()
            StudentProfile.objects.create(
                user=student_user,
                student_id='STU000001',
                enrollment_date='2024-01-01',
                current_level='Beginner',
                gpa=3.5,
                emergency_contact='John Doe',
                emergency_phone='+1234567890'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created student user: {student_user.email}')
            )

        self.stdout.write(
            self.style.SUCCESS('Sample users created successfully!')
        )
        self.stdout.write('Login credentials:')
        self.stdout.write('Admin: admin@lms.com / admin123')
        self.stdout.write('Tutor: tutor@lms.com / tutor123')
        self.stdout.write('Student: student@lms.com / student123')