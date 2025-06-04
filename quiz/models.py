from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom foydalanuvchi modeli
class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)
    score = models.IntegerField(default=0)  # umumiy ball
    is_email_verified = models.BooleanField(default=False, help_text="Email tasdiqlanganmi?")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    def __str__(self):
        return self.username


class Round(models.Model):
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField()  # masalan: Round 1, Round 2
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Round {self.order}: {self.title}"


class Topic(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} (Round {self.round.order})"


class Question(models.Model):
    answer_type = models.CharField(
    max_length=20,
    choices=[('choice', 'Multiple Choice'), ('text', 'Text Answer')],
    default='choice'
    )

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    score = models.PositiveIntegerField()  # masalan: 100, 200, 300
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='question_images/',null=True,blank=True)
    audio = models.FileField(upload_to='question_audio/', null=True, blank=True)

    correct_answer = models.CharField(max_length=255)
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    option_4 = models.CharField(max_length=255, blank=True, null=True)
    option_5 = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.text} - {self.topic.title}"


class Answer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=255, blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    is_passed = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    user_round = models.ForeignKey('UserRound', on_delete=models.CASCADE,null=True,blank=True)  
    time_spent = models.DurationField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.selected_answer:
            if self.question.answer_type == 'text':
                self.is_correct = (
                    self.selected_answer.strip().lower() == self.question.correct_answer.strip().lower()
                )
            else:
                self.is_correct = (self.selected_answer == self.question.correct_answer)
        else:
            self.is_passed = True
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.username} - {self.question.text[:30]}..."

class UserRound(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0) 
    duration = models.DurationField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if self.started_at and self.ended_at:
            self.duration = self.ended_at - self.started_at
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.username} - {self.round.title}"

