# Generated by Django 3.2.4 on 2022-10-08 06:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home_app', '0003_auto_20221004_2053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='complete',
        ),
    ]