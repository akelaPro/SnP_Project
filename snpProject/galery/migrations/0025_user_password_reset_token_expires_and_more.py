# Generated by Django 5.1.4 on 2025-04-28 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galery', '0024_alter_photo_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password_reset_token_expires',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='password_reset_token_hash',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
