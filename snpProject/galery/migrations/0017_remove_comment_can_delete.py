# Generated by Django 5.1.7 on 2025-03-19 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('galery', '0016_comment_can_delete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='can_delete',
        ),
    ]
