# Generated by Django 5.0.1 on 2024-10-10 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deus_magnus', '0014_projectpicture'),
    ]

    operations = [
        migrations.AddField(
            model_name='seconddeusmagnusmainpicturepost',
            name='second_deus_magnus_status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]