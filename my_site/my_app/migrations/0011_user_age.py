# Generated by Django 4.2.4 on 2023-08-21 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0010_remove_user_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='age',
            field=models.IntegerField(default=18, null=True),
        ),
    ]
