# Generated by Django 5.0 on 2024-11-02 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0003_remove_user_address_remove_user_dob_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='max_otp_try',
            field=models.IntegerField(default=3),
        ),
    ]