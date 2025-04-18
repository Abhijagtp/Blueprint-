# Generated by Django 5.1.6 on 2025-03-28 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0020_post_content_id_post_content_type_alter_post_caption'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry_type', models.CharField(max_length=100)),
                ('organization_name', models.CharField(max_length=200)),
                ('total_employees', models.IntegerField()),
                ('description', models.TextField()),
                ('revenue', models.DecimalField(decimal_places=2, max_digits=15)),
                ('gst_number', models.CharField(max_length=15)),
                ('start_year', models.IntegerField()),
                ('business_type', models.CharField(max_length=100)),
                ('business_nature', models.CharField(max_length=100)),
                ('challenges', models.TextField()),
                ('digital_assets', models.TextField()),
                ('desired_assets', models.TextField()),
                ('skills', models.TextField()),
                ('wish_to_expand', models.BooleanField()),
                ('locations', models.TextField()),
                ('education', models.CharField(max_length=50)),
                ('website_link', models.URLField()),
                ('open_positions', models.TextField()),
                ('willing_to_collaborate', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
