# Generated by Django 5.0.6 on 2025-05-30 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_remove_answer_time_spent_remove_question_answer_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='time_spent',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='answer_type',
            field=models.CharField(choices=[('choice', 'Multiple Choice'), ('text', 'Text Answer')], default='choice', max_length=20),
        ),
        migrations.AddField(
            model_name='question',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to='question_audio/'),
        ),
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/'),
        ),
        migrations.AddField(
            model_name='round',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='round',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
