# Generated by Django 5.1.6 on 2025-03-15 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0005_alter_email_attachment_alter_reply_attachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='attachments/'),
        ),
        migrations.AlterField(
            model_name='reply',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='attachments/replies/'),
        ),
    ]
