# Generated by Django 5.1.3 on 2024-12-04 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appfood', '0015_alter_recipe_author_alter_comment_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
