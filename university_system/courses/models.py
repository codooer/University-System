from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from ckeditor.fields import RichTextField
from users.utils import slug_generator, PathAndRename, image_resize
from .managers import AssignmentManager,AnnouncementManager

User = get_user_model()

class Course(models.Model):
    name = models.CharField(max_length=30)
    professor = models.ManyToManyField(User, related_name="tutoring",limit_choices_to={'is_prof':True})
    students = models.ManyToManyField(User, related_name="courses",blank=True,limit_choices_to={'is_prof':False})
    course_image = models.ImageField(
        upload_to=PathAndRename("images\\course_images"),default="images\\course_images\\default.png"
    )
    course_code = models.CharField(max_length=6,unique=True,null=True,blank=True)
    descreption = RichTextField(null=True,blank=True)
    slug = models.SlugField(max_length=5, null=True, blank=True,unique=True)

    class Meta():
        indexes =[
            models.Index(name='code_index',fields=['course_code'])#re check this
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_generator(self)
        super().save(*args, **kwargs)
        image_resize(self.course_image.path)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('course-view',kwargs={'slug':self.slug})

    def check_user_enrollment(self,user):
        if user not in self.students.all() and user not in self.professor.all():
            return False
        return True


class Assignment(models.Model):
    file = models.FileField(upload_to='docs\\assignments')
    deadline = models.DateTimeField(null=True, blank=True)
    max_mark = models.PositiveSmallIntegerField(null=True,blank=True)
    notes = models.CharField(max_length=150,null=True,blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    professor = models.ForeignKey(User, on_delete=models.CASCADE,limit_choices_to={'is_prof':True})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=5,null=True,blank=True,unique=True)
    objects = AssignmentManager()

    class Meta():
        constraints = [
            models.UniqueConstraint(fields=['file','course'],name='non_repeating_files'),
        ]
        indexes = [models.Index(fields=['slug'],name='slug_idx')]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_generator(self)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.file.name

    def get_absolute_url(self):
        return reverse('assignment_view',kwargs={'slug':self.slug})

    @property
    def get_max_mark(self):
        return self.max_mark if self.max_mark else 'Unspecified'

    @property
    def get_notes(self):
        return self.notes if self.notes else 'No Notes'


class CourseFiles(models.Model):
    file = models.FileField(upload_to='docs\\files')
    upload_date = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    uploader = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    slug = models.SlugField(max_length=5, null=True, blank=True,unique=True)

    class Meta():
        constraints = [
            models.UniqueConstraint(fields=['file','course'],name='non_repeating_course_file')
        ]
        indexes = [models.Index(fields=['slug'],name='slug_index')]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_generator(self)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.file.name

    def get_absolute_url(self):
        return reverse('course_files_view',kwargs={'slug':self.slug})


class Announcement(models.Model):
    body = models.TextField(verbose_name="Announcement", null=True, blank=True)
    public = models.BooleanField(default=False)
    date_posted = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=5, null=True, blank=True,unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,limit_choices_to={'is_prof':True})
    course = models.ForeignKey(Course, on_delete=models.CASCADE,blank=True)
    objects = AnnouncementManager()

    class Meta():
        constraints = [
            models.UniqueConstraint(fields=['body','course'],name='non_repeating_announcement')
        ]
        indexes = [models.Index(fields=['slug'],name='announcement_idx')]
    def __str__(self):
        return f'{self.author.name}/{self.date_posted}'

    def save(self, *args, **kwargs):
        if not self.slug:self.slug = slug_generator(self)
        if not self.course:self.public=True

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('announcement-view',kwargs={'slug':self.slug})
