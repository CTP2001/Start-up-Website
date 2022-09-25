from django.contrib import admin
from django.db import models

from crowdfunding.models import Project, Category, Comment, Profile,ProjectImage, Payment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class CommentInLine(admin.StackedInline):
    model = Comment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'fund', 'date', 'user')
    search_fields = ('name',)
    list_filter = ('category',)
    inlines = [CommentInLine]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'city',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'fund_support', 'date',)