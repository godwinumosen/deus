# Generated by Django 5.0.1 on 2024-10-05 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deus_magnus', '0013_remove_lastdeusmagnusmainpicturepost_last_deus_magnus_author_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectPicture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deus_magnus_project_p', models.ImageField(upload_to='project_p/')),
            ],
        ),
    ]
