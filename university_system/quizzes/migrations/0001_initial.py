# Generated by Django 3.1.13 on 2021-09-14 14:43

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion
import users.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('quiz_images', models.ImageField(default='images\\quiz_images\\default.png', upload_to=users.utils.PathAndRename('images\\quiz_images'))),
                ('slug', models.SlugField(blank=True, max_length=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuizAttempts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuizQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('grade', models.FloatField(blank=True, default=0, null=True)),
                ('slug', models.SlugField(blank=True, max_length=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuizQuestionChoices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(blank=True, null=True, verbose_name='choice')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Correct Answer')),
                ('slug', models.SlugField(blank=True, max_length=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentQuizAnswers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.quizquestionchoices')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.quizquestion')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.quiz')),
            ],
        ),
    ]
