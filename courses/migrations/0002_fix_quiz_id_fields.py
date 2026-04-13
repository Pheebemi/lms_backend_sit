# Generated manually to fix SQLite integer overflow issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        # Change Quiz id from BigAutoField to AutoField to fix SQLite compatibility
        migrations.AlterField(
            model_name='quiz',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        # Change QuizQuestion id from BigAutoField to AutoField
        migrations.AlterField(
            model_name='quizquestion',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        # Change QuizAttempt id from BigAutoField to AutoField
        migrations.AlterField(
            model_name='quizattempt',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        # Change QuizAnswer id from BigAutoField to AutoField
        migrations.AlterField(
            model_name='quizanswer',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        # Change LessonProgress id from BigAutoField to AutoField
        migrations.AlterField(
            model_name='lessonprogress',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        # Change Enrollment id from BigAutoField to AutoField
        migrations.AlterField(
            model_name='enrollment',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        # Change CourseReview id from BigAutoField to AutoField
        migrations.AlterField(
            model_name='coursereview',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

