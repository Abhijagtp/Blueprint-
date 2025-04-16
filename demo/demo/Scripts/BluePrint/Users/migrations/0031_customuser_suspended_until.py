from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0030_customuser_account_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='suspended_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
