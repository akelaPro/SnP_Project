# Generated by Django 5.1.4 on 2025-03-12 14:04

import django.db.models.deletion
import galery.models.customToken.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galery', '0014_alter_comment_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token_hash', models.CharField(db_index=True, max_length=64, unique=True)),
                ('access_token_expires', models.DateTimeField(default=galery.models.customToken.models.get_default_access_expires)),
                ('refresh_token_hash', models.CharField(db_index=True, max_length=64, unique=True)),
                ('refresh_token_expires', models.DateTimeField(default=galery.models.customToken.models.get_default_refresh_expires)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='token', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
