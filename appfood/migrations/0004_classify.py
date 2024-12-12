# Generated by Django 5.1.3 on 2024-12-01 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appfood', '0003_alter_recipe_classify'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classify',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('snacks', 'Món Ăn Vặt'), ('vegetarian', 'Chay'), ('asian', 'Món Á'), ('european', 'Món Âu'), ('grill', 'Nướng'), ('appetizer', 'Khai Vị'), ('dessert', 'Tráng Miện')], max_length=10)),
            ],
        ),
    ]