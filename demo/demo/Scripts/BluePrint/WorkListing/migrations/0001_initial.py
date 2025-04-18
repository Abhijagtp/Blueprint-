# Generated by Django 5.1.6 on 2025-02-27 08:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('experience_required', models.IntegerField()),
                ('skills_required', models.JSONField(default=list)),
                ('starting_date', models.DateField()),
                ('submission_date', models.DateField()),
                ('payment', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('org', models.ForeignKey(limit_choices_to={'user_type': 'organizational'}, on_delete=django.db.models.deletion.CASCADE, related_name='posted_projects', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('professional', models.ForeignKey(limit_choices_to={'user_type': 'professional'}, on_delete=django.db.models.deletion.CASCADE, related_name='project_requests', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='WorkListing.project')),
            ],
        ),
    ]
