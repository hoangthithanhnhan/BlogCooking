# Generated by Django 5.1.3 on 2024-12-02 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appfood', '0005_remove_recipe_average_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classify',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='classify',
        ),
        migrations.AddField(
            model_name='recipe',
            name='classify',
            field=models.ManyToManyField(blank=True, related_name='recipes', to='appfood.classify'),
        ),
    ]