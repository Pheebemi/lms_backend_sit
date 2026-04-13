from django.core.management.base import BaseCommand
from courses.models import Course


class Command(BaseCommand):
    help = 'Update lesson counts for all courses'

    def handle(self, *args, **options):
        courses = Course.objects.all()
        updated_count = 0
        
        for course in courses:
            old_count = course.total_lessons
            course.update_lesson_count()
            new_count = course.total_lessons
            
            if old_count != new_count:
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {course.title}: {old_count} -> {new_count} lessons'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated lesson counts for {updated_count} courses'
            )
        )
