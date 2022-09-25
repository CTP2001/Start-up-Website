from django.db import models
from django.conf import settings
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.db.models import Sum

class Category(models.Model):
    name = models.CharField(max_length=100, help_text='Category Name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class Project(models.Model):
    name = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    video = models.FileField(null=True, blank=True, upload_to="videos/")
    description = models.TextField()
    body = models.TextField(null=True)
    fund = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    

class ProjectImage(models.Model):
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images_of_project")

class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, related_name="user_profile", on_delete=models.CASCADE)
    phone    = models.CharField(max_length=32, null=True, blank=True)
    address  = models.CharField(max_length=255, null=True, blank=True)
    city     = models.CharField(max_length=50, null=True, blank=True)
    

class Payment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, related_name="user_payment", on_delete=models.CASCADE)
    email = models.CharField(max_length=32, null=True, blank=True)
    fund_support = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)