# Generated by Django 4.1.2 on 2023-01-24 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_author_rating_normalized_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='send_email_notifications',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='show_contacts',
            field=models.BooleanField(default=False),
        ),
    ]
