# Generated by Django 4.2.4 on 2023-08-21 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0006_alter_comment_post_alter_comment_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='age',
            field=models.IntegerField(),
        ),
    ]