from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from users.utils import slug_generator, image_resize
from courses.models import Course
from datetime import datetime, timedelta
from ckeditor_uploader.fields import RichTextUploadingField
from .managers import QuizManager
import pytz


User = get_user_model()


class Quiz(models.Model):
    name = models.CharField(max_length=30)
    start = models.DateTimeField(null=True)
    duration = models.IntegerField(null=True, blank=True)
    slug = models.SlugField(max_length=5, null=True, blank=True, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    prof = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={"is_prof": True})
    objects = QuizManager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["name", "course"], name="unique_course")]
        indexes = [models.Index(fields=["slug"], name="quiz_idx")]

    def __str__(self):
        return f"{self.name} {self.course.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_generator(self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("create-quiz-question", kwargs={"slug": self.slug})

    @property
    def get_end_time(self):
        return self.start + timedelta(minutes=self.duration)

    @property
    def is_open(self):
        if pytz.utc.localize(datetime.utcnow()) > self.get_end_time:
            return False
        return True

    @property
    def get_quiz_grade(self):
        total = 0
        for question in self.questions.all():
            total += question.grade
        return total


class QuizQuestion(models.Model):
    body = RichTextUploadingField(null=True, blank=True)
    grade = models.FloatField(default=0, null=True, blank=True)
    slug = models.SlugField(max_length=5, null=True, blank=True, unique=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["body", "quiz"], name="body_of_the_question")]
        indexes = [models.Index(fields=["slug"], name="question_idx")]

    def __str__(self):
        return f"question:{self.body} quiz:{self.quiz.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_generator(self)

        for token in self.body.split():
            if token.startswith("src="):
                filepath = token.split("=")[1].strip('"')
                filepath = filepath.replace("/media", settings.MEDIA_ROOT)
                image_resize(filepath)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("create-q-choice", kwargs={"slug": self.slug})

    @property
    def get_course(self):
        return self.quiz.course

    @property
    def get_author(self):
        return self.quiz.prof


class QuizQuestionChoices(models.Model):
    body = models.TextField(verbose_name="choice", blank=True, null=True)
    is_correct = models.BooleanField(verbose_name="Correct Answer", default=False)
    slug = models.SlugField(max_length=5, null=True, blank=True, unique=True)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="choices")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["body", "question"], name="non_repeating_choices")]
        indexes = [models.Index(fields=["slug"], name="choice_idx")]

    def __str__(self):
        return f"{self.body}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_generator(self)
        return super().save(*args, **kwargs)

    @property
    def get_grade(self):
        return self.question.grade

    @property
    def get_author(self):
        return self.question.get_author

    @property
    def get_count(self):
        return self.student_ans.count()


class QuizAttempts(models.Model):
    students = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"is_prof": False})
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="students_attempts")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.students.college_id},{self.quiz.name},{self.timestamp}"


class StudentQuizAnswers(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"is_prof": False})
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="student_answers")
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    choice = models.ForeignKey(QuizQuestionChoices, on_delete=models.CASCADE, related_name="student_ans")
    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "question"], name="one_answer_only")]

    def __str__(self):
        return f"student:{self.student.college_id}//quiz:{self.question.body}"

    @property
    def is_right(self):
        return self.choice.is_correct

    def get_grade(self):
        if self.is_right:
            return self.question.grade
        return 0


