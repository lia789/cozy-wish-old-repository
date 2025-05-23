# Generated by Django 5.2 on 2025-05-14 04:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'), ('view', 'View'), ('approve', 'Approve'), ('reject', 'Reject'), ('login', 'Login'), ('logout', 'Logout'), ('other', 'Other')], max_length=20)),
                ('target_model', models.CharField(blank=True, max_length=100)),
                ('target_id', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('user', models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, related_name='admin_activities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Admin Activities',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='AdminPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')], default='light', max_length=10)),
                ('sidebar_collapsed', models.BooleanField(default=False)),
                ('show_quick_actions', models.BooleanField(default=True)),
                ('items_per_page', models.PositiveIntegerField(default=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, related_name='admin_preferences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdminTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('assigned_to', models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, related_name='created_tasks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50)),
                ('model_name', models.CharField(max_length=100)),
                ('object_id', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('changes', models.JSONField(blank=True, default=dict)),
                ('object_pk', models.CharField(blank=True, max_length=255, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='SecurityEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('failed_login', 'Failed Login'), ('successful_login', 'Successful Login'), ('logout', 'Logout'), ('password_change', 'Password Change'), ('password_reset', 'Password Reset'), ('account_lockout', 'Account Lockout'), ('permission_change', 'Permission Change'), ('suspicious_activity', 'Suspicious Activity'), ('other', 'Other')], max_length=20)),
                ('severity', models.CharField(choices=[('info', 'Information'), ('warning', 'Warning'), ('critical', 'Critical')], default='info', max_length=10)),
                ('description', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolution_notes', models.TextField(blank=True)),
                ('resolved_by', models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_security_events', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='security_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='SystemConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maintenance_mode', models.BooleanField(default=False)),
                ('maintenance_message', models.TextField(blank=True)),
                ('registration_enabled', models.BooleanField(default=True)),
                ('max_login_attempts', models.PositiveIntegerField(default=5)),
                ('login_lockout_duration', models.PositiveIntegerField(default=30, help_text='Duration in minutes')),
                ('password_expiry_days', models.PositiveIntegerField(default=90)),
                ('session_timeout_minutes', models.PositiveIntegerField(default=30)),
                ('enable_two_factor_auth', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='system_config_updates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'System Configuration',
                'verbose_name_plural': 'System Configuration',
            },
        ),
    ]
