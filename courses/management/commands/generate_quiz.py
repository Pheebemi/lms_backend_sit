from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from courses.models import Lesson, Quiz, QuizQuestion
import random

class Command(BaseCommand):
    help = 'Automatically generate quiz questions for lessons that don\'t have quizzes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lesson-id',
            type=int,
            help='Generate quiz for specific lesson ID',
        )
        parser.add_argument(
            '--course-id',
            type=str,
            help='Generate quizzes for all lessons in a specific course',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate quizzes for all lessons without quizzes',
        )
        parser.add_argument(
            '--questions',
            type=int,
            default=5,
            help='Number of questions to generate per quiz (default: 5)',
        )
        parser.add_argument(
            '--difficulty',
            choices=['easy', 'medium', 'hard'],
            default='medium',
            help='Difficulty level for generated questions',
        )

    def handle(self, *args, **options):
        if options['lesson_id']:
            self.generate_quiz_for_lesson(options['lesson_id'], options['questions'], options['difficulty'])
        elif options['course_id']:
            self.generate_quizzes_for_course(options['course_id'], options['questions'], options['difficulty'])
        elif options['all']:
            self.generate_quizzes_for_all(options['questions'], options['difficulty'])
        else:
            raise CommandError('Please specify --lesson-id, --course-id, or --all')

    def generate_quiz_for_lesson(self, lesson_id, num_questions, difficulty):
        """Generate quiz for a specific lesson"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            raise CommandError(f'Lesson with ID {lesson_id} does not exist')

        if hasattr(lesson, 'quiz'):
            self.stdout.write(f'Lesson "{lesson.title}" already has a quiz. Skipping...')
            return

        quiz = self.create_quiz_for_lesson(lesson, num_questions, difficulty)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated quiz for lesson "{lesson.title}" with {num_questions} questions')
        )

    def generate_quizzes_for_course(self, course_id, num_questions, difficulty):
        """Generate quizzes for all lessons in a course"""
        lessons = Lesson.objects.filter(course_id=course_id)
        if not lessons:
            raise CommandError(f'No lessons found for course ID {course_id}')

        generated = 0
        for lesson in lessons:
            if not hasattr(lesson, 'quiz'):
                self.create_quiz_for_lesson(lesson, num_questions, difficulty)
                generated += 1

        self.stdout.write(
            self.style.SUCCESS(f'Generated quizzes for {generated} lessons in course {course_id}')
        )

    def generate_quizzes_for_all(self, num_questions, difficulty):
        """Generate quizzes for all lessons without quizzes"""
        lessons_without_quiz = Lesson.objects.filter(is_published=True).exclude(quiz__isnull=False)
        total = lessons_without_quiz.count()

        if total == 0:
            self.stdout.write('All published lessons already have quizzes!')
            return

        self.stdout.write(f'Generating quizzes for {total} lessons...')

        for lesson in lessons_without_quiz:
            self.create_quiz_for_lesson(lesson, num_questions, difficulty)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated quizzes for {total} lessons')
        )

    def create_quiz_for_lesson(self, lesson, num_questions, difficulty):
        """Create a quiz with auto-generated questions"""
        # Create quiz
        quiz = Quiz.objects.create(
            lesson=lesson,
            title=f"{lesson.title} Quiz",
            description=f"Auto-generated quiz for {lesson.title}",
            time_limit_minutes=30,
            passing_score=70,
            max_attempts=3,
            is_published=True
        )

        # Generate questions based on lesson content and difficulty
        questions_data = self.generate_questions_for_lesson(lesson, num_questions, difficulty)

        for i, question_data in enumerate(questions_data, 1):
            QuizQuestion.objects.create(
                quiz=quiz,
                question_text=question_data['question'],
                question_type=question_data['type'],
                order=i,
                points=question_data.get('points', 1),
                options=question_data.get('options', []),
                correct_answer=question_data['correct_answer'],
                acceptable_answers=question_data.get('acceptable_answers', [])
            )

        return quiz

    def generate_questions_for_lesson(self, lesson, num_questions, difficulty):
        """Generate questions based on lesson content"""
        questions = []

        # Base questions that work for any lesson
        base_questions = [
            {
                'question': f"What is the main topic of the lesson '{lesson.title}'?",
                'type': 'short_answer',
                'correct_answer': lesson.title.lower(),
                'acceptable_answers': [lesson.title.lower(), lesson.title],
                'points': 2
            },
            {
                'question': f"True or False: This lesson is titled '{lesson.title}'.",
                'type': 'true_false',
                'correct_answer': 'True',
                'points': 1
            }
        ]

        # Add lesson-specific questions based on content
        if lesson.description:
            base_questions.append({
                'question': f"Based on the lesson description, what is one key point mentioned?",
                'type': 'short_answer',
                'correct_answer': 'varies',
                'acceptable_answers': ['learning', 'course', 'lesson', lesson.title.split()[0].lower()],
                'points': 2
            })

        # Multiple choice questions
        mc_questions = [
            {
                'question': f"Which of the following is the title of this lesson?",
                'type': 'multiple_choice',
                'options': [
                    lesson.title,
                    f"Advanced {lesson.title}",
                    f"Introduction to {lesson.title}",
                    f"{lesson.title} Basics"
                ],
                'correct_answer': lesson.title,
                'points': 1
            },
            {
                'question': f"What type of content is covered in '{lesson.title}'?",
                'type': 'multiple_choice',
                'options': ['Video', 'Text', 'Interactive', 'Mixed'],
                'correct_answer': 'Mixed',
                'points': 1
            }
        ]

        # Difficulty-based question variations
        if difficulty == 'easy':
            # Use simpler questions
            questions.extend(base_questions[:2])
            questions.extend(mc_questions[:1])
        elif difficulty == 'medium':
            # Mix of all question types
            questions.extend(base_questions)
            questions.extend(mc_questions[:2])
        else:  # hard
            # More complex questions
            questions.extend(base_questions)
            questions.extend(mc_questions)

            # Add harder questions
            questions.append({
                'question': f"Explain in one sentence what you learned from '{lesson.title}'.",
                'type': 'short_answer',
                'correct_answer': 'varies',
                'acceptable_answers': ['learning', 'understand', 'knowledge', 'skills'],
                'points': 3
            })

        # Ensure we have exactly num_questions
        while len(questions) < num_questions:
            # Duplicate or create variations
            if questions:
                new_q = questions[-1].copy()
                new_q['question'] += " (Review)"
                questions.append(new_q)

        return questions[:num_questions]
