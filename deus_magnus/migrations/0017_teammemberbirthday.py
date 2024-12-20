# Generated by Django 5.0.1 on 2024-11-18 09:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deus_magnus', '0016_deusmagnusmainpost_deus_magnus_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamMemberBirthday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birthday_name', models.CharField(max_length=200)),
                ('birthday_date', models.DateField()),
                ('birthday_image', models.ImageField(upload_to='birthday_p/')),
                ('birthday_publish_date', models.DateTimeField(auto_now_add=True)),
                ('birthday_author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-birthday_publish_date'],
            },
        ),
    ]
