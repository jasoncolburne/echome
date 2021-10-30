# Generated by Django 3.2.6 on 2021-09-13 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kube', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kubecluster',
            name='status',
            field=models.CharField(choices=[('1', 'Building'), ('2', 'Failed'), ('3', 'Ready'), ('4', 'Updating'), ('5', 'Deleting'), ('6', 'Terminated')], default='1', max_length=4),
        ),
    ]
