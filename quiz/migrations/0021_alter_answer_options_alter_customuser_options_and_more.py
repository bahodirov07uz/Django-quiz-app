# Generated by Django 5.0.6 on 2025-06-03 02:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0020_alter_answer_options_alter_customuser_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'verbose_name': 'Ответ', 'verbose_name_plural': 'Ответы'},
        ),
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': 'Вопрос', 'verbose_name_plural': 'Вопросы'},
        ),
        migrations.AlterModelOptions(
            name='round',
            options={'ordering': ['order'], 'verbose_name': 'Раунд', 'verbose_name_plural': 'Раунды'},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'verbose_name': 'Тема', 'verbose_name_plural': 'Темы'},
        ),
        migrations.AlterModelOptions(
            name='userround',
            options={'verbose_name': 'Раунд пользователя', 'verbose_name_plural': 'Раунды пользователей'},
        ),
        migrations.AlterField(
            model_name='answer',
            name='answered_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата ответа'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='is_correct',
            field=models.BooleanField(default=False, verbose_name='Правильно?'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='is_passed',
            field=models.BooleanField(default=False, verbose_name='Пропущено?'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question', verbose_name='Вопрос'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='selected_answer',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Выбранный ответ'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='time_spent',
            field=models.DurationField(blank=True, null=True, verbose_name='Затраченное время'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='user_round',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.userround', verbose_name='Раунд пользователя'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Полное имя'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_email_verified',
            field=models.BooleanField(default=False, help_text='Email подтвержден?', verbose_name='Email подтвержден?'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='score',
            field=models.IntegerField(default=0, verbose_name='Общий балл'),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_type',
            field=models.CharField(choices=[('choice', 'Множественный выбор'), ('text', 'Текстовый ответ')], default='choice', max_length=20, verbose_name='Тип ответа'),
        ),
        migrations.AlterField(
            model_name='question',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to='question_audio/', verbose_name='Аудио'),
        ),
        migrations.AlterField(
            model_name='question',
            name='correct_answer',
            field=models.CharField(max_length=255, verbose_name='Правильный ответ'),
        ),
        migrations.AlterField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/', verbose_name='Изображение 1'),
        ),
        migrations.AlterField(
            model_name='question',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/', verbose_name='Изображение 2'),
        ),
        migrations.AlterField(
            model_name='question',
            name='option_1',
            field=models.CharField(max_length=255, verbose_name='Вариант 1'),
        ),
        migrations.AlterField(
            model_name='question',
            name='option_2',
            field=models.CharField(max_length=255, verbose_name='Вариант 2'),
        ),
        migrations.AlterField(
            model_name='question',
            name='option_3',
            field=models.CharField(max_length=255, verbose_name='Вариант 3'),
        ),
        migrations.AlterField(
            model_name='question',
            name='option_4',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Вариант 4'),
        ),
        migrations.AlterField(
            model_name='question',
            name='option_5',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Вариант 5'),
        ),
        migrations.AlterField(
            model_name='question',
            name='score',
            field=models.PositiveIntegerField(verbose_name='Баллы'),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(verbose_name='Текст вопроса'),
        ),
        migrations.AlterField(
            model_name='question',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quiz.topic', verbose_name='Тема'),
        ),
        migrations.AlterField(
            model_name='round',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время окончания'),
        ),
        migrations.AlterField(
            model_name='round',
            name='order',
            field=models.PositiveIntegerField(verbose_name='Порядок'),
        ),
        migrations.AlterField(
            model_name='round',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время начала'),
        ),
        migrations.AlterField(
            model_name='round',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='round',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='quiz.round', verbose_name='Раунд'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='userround',
            name='duration',
            field=models.DurationField(blank=True, null=True, verbose_name='Продолжительность'),
        ),
        migrations.AlterField(
            model_name='userround',
            name='ended_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Завершено'),
        ),
        migrations.AlterField(
            model_name='userround',
            name='round',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.round', verbose_name='Раунд'),
        ),
        migrations.AlterField(
            model_name='userround',
            name='score',
            field=models.IntegerField(default=0, verbose_name='Баллы'),
        ),
        migrations.AlterField(
            model_name='userround',
            name='started_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Начато'),
        ),
        migrations.AlterField(
            model_name='userround',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
