# Generated by Django 5.1.4 on 2025-03-31 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0003_notification_send_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='send_email',
        ),
        migrations.AddField(
            model_name='notification',
            name='email_sent',
            field=models.BooleanField(default=False),
        ),
    ]
