# Generated by Django 5.0.6 on 2024-06-23 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_hashtag_post_hashtags"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="published",
            field=models.BooleanField(default=True),
        ),
    ]
