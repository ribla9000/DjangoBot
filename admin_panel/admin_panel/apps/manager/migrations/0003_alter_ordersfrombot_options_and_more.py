# Generated by Django 4.1.4 on 2022-12-30 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_ordersfrombot_user_contact_info'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ordersfrombot',
            options={'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterModelOptions(
            name='statusorder',
            options={'verbose_name': 'Статус', 'verbose_name_plural': 'Статусы'},
        ),
        migrations.AlterField(
            model_name='ordersfrombot',
            name='chat_id_user',
            field=models.PositiveIntegerField(verbose_name='ID пользователя'),
        ),
        migrations.AlterField(
            model_name='ordersfrombot',
            name='is_active',
            field=models.ForeignKey(default=True, on_delete=django.db.models.deletion.DO_NOTHING, to='manager.statusorder', verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='ordersfrombot',
            name='order_price',
            field=models.IntegerField(blank=True, verbose_name='Цена заказа'),
        ),
        migrations.AlterField(
            model_name='ordersfrombot',
            name='services_name',
            field=models.TextField(blank=True, verbose_name='Наименование услуги'),
        ),
        migrations.AlterField(
            model_name='ordersfrombot',
            name='user_contact_info',
            field=models.TextField(blank=True, verbose_name='Информация о пользователе'),
        ),
        migrations.AlterField(
            model_name='ordersfrombot',
            name='user_name',
            field=models.TextField(blank=True, verbose_name='Имя пользователя'),
        ),
        migrations.AlterField(
            model_name='statusorder',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активен?'),
        ),
        migrations.AlterField(
            model_name='statusorder',
            name='status_name',
            field=models.TextField(verbose_name='Статус заказа'),
        ),
    ]
