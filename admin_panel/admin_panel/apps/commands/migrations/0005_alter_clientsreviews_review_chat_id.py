# Generated by Django 4.1.4 on 2022-12-30 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands', '0004_alter_advertisementscalculator_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientsreviews',
            name='review_chat_id',
            field=models.IntegerField(default=0, verbose_name='ID пользователя'),
        ),
    ]
