# Generated by Django 4.1.4 on 2022-12-30 23:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commands', '0006_alter_companyposts_options_delete_staffincompany'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CompanyPosts',
        ),
        migrations.AlterModelOptions(
            name='advertisementscalculator',
            options={'verbose_name': 'Сотрудник', 'verbose_name_plural': 'Сотрудники'},
        ),
    ]
