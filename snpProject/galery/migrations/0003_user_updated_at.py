# Generated by Django 5.1.4 on 2024-12-22 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galery', '0002_alter_comment_options_alter_photo_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
