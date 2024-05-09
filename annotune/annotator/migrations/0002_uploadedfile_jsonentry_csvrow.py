# Generated by Django 5.0.4 on 2024-05-06 16:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/%Y/%m/%d/')),
                ('file_name', models.CharField(max_length=255)),
                ('file_type', models.CharField(max_length=50)),
                ('size', models.PositiveIntegerField()),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JSONEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotator.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='CSVRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField()),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotator.uploadedfile')),
            ],
        ),
    ]
