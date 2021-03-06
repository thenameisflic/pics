# Generated by Django 2.1.4 on 2019-03-28 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0003_photo_disguised_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='original',
            field=models.FileField(default='images/missing.jpg', upload_to='images/original/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='photo',
            name='disguised_image',
            field=models.FileField(upload_to='images/anon/'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.FileField(upload_to='images/auth/'),
        ),
    ]
