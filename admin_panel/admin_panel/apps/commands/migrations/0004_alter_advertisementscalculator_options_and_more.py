# Generated by Django 4.1.4 on 2022-12-30 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands', '0003_alter_advertisementscalculator_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='advertisementscalculator',
            options={'verbose_name': 'Калькулятор рекламы', 'verbose_name_plural': 'Калькулятор рекламы'},
        ),
        migrations.AddField(
            model_name='clientsreviews',
            name='review_chat_id',
            field=models.IntegerField(default=0, unique=True, verbose_name='ID пользователя'),
        ),
        migrations.AddField(
            model_name='clientsreviews',
            name='review_username',
            field=models.TextField(null=True, verbose_name='Пользователь который оставил'),
        ),
        migrations.AlterField(
            model_name='serviceslist',
            name='service_price',
            field=models.IntegerField(help_text='Цена за единицу', verbose_name='Цена'),
        ),
    ]