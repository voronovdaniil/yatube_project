# Generated by Django 2.2.6 on 2021-12-25 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20211225_0259'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': ('Подписка',), 'verbose_name_plural': 'Подписки'},
        ),
    ]
