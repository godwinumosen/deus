# Generated by Django 5.0.1 on 2024-05-03 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deus_magnus', '0016_alter_deusmagnusmainpost_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deusmagnusmainpost',
            options={'ordering': ['-deus_magnus_publish_date']},
        ),
        migrations.AddField(
            model_name='deusmagnusmainpost',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
