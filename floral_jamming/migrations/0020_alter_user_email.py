# Generated by Django 5.0.4 on 2024-05-08 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('floral_jamming', '0019_emailconfirmationtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]