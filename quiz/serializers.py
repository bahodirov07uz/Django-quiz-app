from rest_framework import serializers
from .models import Round, Topic, Question, Answer

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ['id', 'title', 'order']

class TopicSerializer(serializers.ModelSerializer):
    round = RoundSerializer(read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'title', 'round']

class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    answered = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()  
    audio_url = serializers.SerializerMethodField() 
    class Meta:
        model = Question
        fields = ['id', 'text', 'score', 'correct_answer', 'options','answered', 'image_url','audio_url']

    def get_options(self, obj):
        opts = [
            obj.option_1,
            obj.option_2,
            obj.option_3,
            obj.option_4,
            obj.option_5,
        ]
        return [o for o in opts if o]
    
    def get_answered(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return Answer.objects.filter(user=user, question=obj).exists()
        return False
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return obj.image.url
        return None

    def get_audio_url(self, obj):
        request = self.context.get('request')
        if obj.audio:
            return request.build_absolute_uri(obj.audio.url)
        return None
    
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'selected_answer', 'is_correct', 'is_passed', 'answered_at']
        read_only_fields = ['is_correct', 'is_passed', 'answered_at']
