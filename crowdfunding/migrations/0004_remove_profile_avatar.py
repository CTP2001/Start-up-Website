# Generated by Django 3.2.8 on 2021-12-23 03:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0003_auto_20211208_0043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='avatar',
        ),
    ]