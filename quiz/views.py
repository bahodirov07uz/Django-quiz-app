from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Topic, Question, Round, Answer, UserRound, CustomUser
from .serializers import RoundSerializer, TopicSerializer, QuestionSerializer, AnswerSerializer
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Max
from datetime import timedelta

class Home(LoginRequiredMixin, ListView):
    template_name = 'index.html'
    model = Round

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rounds'] = Round.objects.all().order_by('order')
        return context 

class RoundListView(APIView):
    def get(self, request):
        rounds = Round.objects.order_by('order')
        return Response(RoundSerializer(rounds, many=True).data)

class TopicListView(APIView):
    def get(self, request):
        round_id = request.GET.get('round')
        qs = Topic.objects.filter(round_id=round_id) if round_id else Topic.objects.all()
        return Response(TopicSerializer(qs, many=True).data)

class QuestionListView(APIView):
    def get(self, request):
        topic_id = request.GET.get('topic')
        qs = Question.objects.filter(topic_id=topic_id)
        return Response(QuestionSerializer(qs, many=True, context={'request': request}).data)
    
User = get_user_model()

class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """GET: Get question state"""
        question_id = request.query_params.get('question')
        if not question_id:
            return Response({"error": "Question ID was not provided."}, status=400)
        
        try:
            question = Question.objects.get(id=question_id)
            answered = Answer.objects.filter(user=request.user, question=question).exists()
            image_url = request.build_absolute_uri(question.image.url) if question.image else None
            image2_url = request.build_absolute_uri(question.image2.url) if question.image2 else None
            audio_url = request.build_absolute_uri(question.audio.url) if question.audio else None

            image_urls = []
            if question.image:
                image_urls.append(request.build_absolute_uri(question.image.url))
            if question.image2:
                image_urls.append(request.build_absolute_uri(question.image2.url))

            # options har doim tuzilsin, if ichida emas!
            options = [
                question.option_1,
                question.option_2,
                question.option_3,
                question.option_4,
                question.option_5,
            ]
            options = [o for o in options if o] 

            return Response({
                "question_id": question.id,
                "answered": answered,
                "text": question.text,
                "options": options,
                "correct_answer": question.correct_answer,
                "score": question.score,
                "type": question.answer_type,
                "image_url": image_urls[0] if image_urls else None,
                "audio_url": audio_url,
                "image_urls": image_urls,
            })
        except Question.DoesNotExist:
            return Response({"error": "Question not found."}, status=404)

    def post(self, request):
        user = request.user
        question_id = request.data.get('question_id')
        selected_answer = request.data.get('selected_answer')
        time_spent_ms = request.data.get('time_spent')
        user_round_id = request.data.get('user_round_id') 
        if not question_id:
            return Response({"error": "Question ID was not provided."}, status=400)
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found."}, status=404)
        
        answer = Answer.objects.create(
            user=user,
            question=question,
            selected_answer=selected_answer if selected_answer else None,
            time_spent=timedelta(milliseconds=int(time_spent_ms)) if time_spent_ms else None
        )

        print('user_round_id:', request.data.get('user_round_id'))
        score_change = 0
        result = "passed"
        correct_answer = question.correct_answer
        round_obj = question.topic.round
        if user_round_id:
            try:
                user_round = UserRound.objects.get(id=user_round_id, user=user)
            except UserRound.DoesNotExist:
                user_round = UserRound.objects.create(user=user, round=round_obj)
        else:
            user_round = UserRound.objects.filter(user=user, round=round_obj).order_by('-started_at').first()
            if not user_round:
                user_round = UserRound.objects.create(user=user, round=round_obj)


        if selected_answer:
            if answer.is_correct:
                user_round.score += question.score    
                user.score += question.score
                score_change = question.score
                result = "correct"
            else:
                user.score -= question.score
                user_round.score -= question.score  
                score_change = question.score
                result = "incorrect"

            user.save()
            user_round.save()
        return Response({
            "result": result,
            "is_correct": answer.is_correct,
            "score_change": score_change,
            "total_score": user.score,
            "correct_answer": correct_answer,
            "user_round_score": user_round.score,
            "user_round_id": user_round.id,

        })

class SaveUserRoundView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        round_id = request.data.get('round_id')
        score = int(request.data.get('score', 0))
        end = request.data.get('end', False)
        time_spent = int(request.data.get('time_spent', 0))
        user_round_id = request.data.get('user_round_id')  # Frontdan kelishi kerak!

        if not round_id or not user_round_id:
            return Response({'error': 'round_id and user_round_id required.'}, status=400)
        try:
            user_round = UserRound.objects.get(id=user_round_id, user=user, round_id=round_id)

        except UserRound.DoesNotExist:
            return Response({'error': 'UserRound1 not found.'}, status=404)
        if score > user_round.score:
            user_round.score = score
        if end:
            user_round.ended_at = timezone.now()
        if time_spent:
            user_round.duration = timedelta(milliseconds=time_spent)
        user_round.save()
        return Response({'status': 'updated', 'score': user_round.score})
    
@login_required
def game_view(request):
    return render(request, 'game.html')

def load_all_rounds(request):
    rounds = Round.objects.all().order_by('order')
    return render(request, 'partials/round_modal.html', {'rounds': rounds})

class RoundDetailView(APIView):
    def get(self, request, pk):
        round = get_object_or_404(Round, pk=pk)
        return Response(RoundSerializer(round).data)

class RoundQuestionsCountView(APIView):
    def get(self, request, pk):
        count = Question.objects.filter(topic__round_id=pk).count()
        answered_count = Answer.objects.filter(
            question__topic__round_id=pk,
            user=request.user
        ).count()
        return Response({
            'total_questions': count,
            'answered_questions': answered_count
        })

class SaveScoreView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        user.score = request.data.get('score', 0)
        user.save()
        return Response({'status': 'success'})
    
from django.db.models import Max

@login_required
def kabinet_view(request):
    user = request.user
    userrounds = UserRound.objects.filter(user=user).order_by('-ended_at')
    correct_answer = Answer.objects.filter(user=user, is_correct=True).count()
    
    # Eng yaxshi natijalar: har bir raund bo‘yicha userning eng yuqori score'lari
    best_rounds = (
        UserRound.objects
        .filter(user=user)
        .values('round__title')  # yoki 'round__id', 'round__title'
        .annotate(best_score=Max('score'), ended_at=Max('ended_at'))
        .order_by('-best_s' \
        'core')[:5]  # eng yuqori 5 natija
    )
    print(best_rounds)
    # best_rounds bu ko‘rinishda bo‘ladi: [{'round__title': 'Matematika', 'best_score': 88}, ...]

    return render(request, 'kabinet.html', {
        'user': user,
        'userrounds': userrounds,
        'correct_answers': correct_answer,
        'best_rounds': best_rounds,
    })

def top_reyting(request):
    # CustomUser modelidagi score ustuni bo‘yicha tartiblaymiz
    from .models import CustomUser
    users = (
        CustomUser.objects
        .order_by('-score')[:10]  # Eng yuqori 10 ta foydalanuvchi
    )
    data = [
        {
            'username': user.username,
            'full_name': user.full_name,
            'score': user.score,
            'avatar': user.avatar.url if user.avatar else None,
        }
        for user in users
    ]
    return JsonResponse(data, safe=False)

@login_required
def check_user_round(request):
    round_id = request.GET.get('round')
    user = request.user
    already_played = UserRound.objects.filter(user=user, round_id=round_id).exists()
    return JsonResponse({'already_played': already_played})

from django.views.decorators.http import require_POST

@login_required
@require_POST
def start_user_round(request):
    round_id = request.GET.get('round')
    user = request.user

    # round_id tekshir!
    if not round_id:
        return JsonResponse({'error': 'round_id required'}, status=400)

    # round mavjudligini tekshir!
    try:
        round_obj = Round.objects.get(id=round_id)
    except Round.DoesNotExist:
        return JsonResponse({'error': 'Round not found'}, status=404)

    # User uchun yangi UserRound ochamiz
    user_round = UserRound.objects.create(
        user=user,
        round=round_obj,
        started_at=timezone.now(),
        ended_at=None,
        score=0,
    )
    return JsonResponse({'status': 'ok', 'user_round_id': user_round.id})

def top_reyting_for_round(request, round_id):
    # Faqat shu round uchun natijalar
    top_rounds_all = (
        UserRound.objects
        .filter(round_id=round_id)
        .select_related('user', 'round')
        .order_by('-score', '-ended_at')
    )

    seen = set()
    unique_rounds = []
    for ur in top_rounds_all:
        key = (ur.user_id, ur.score)
        if key not in seen:
            seen.add(key)
            unique_rounds.append(ur)
        if len(unique_rounds) >= 10:
            break
    data = [
        {
            'username': ur.user.username,
            'full_name': getattr(ur.user, 'full_name', ''),
            'round_title': ur.round.title,
            'score': ur.score,
            'date': ur.ended_at,
            'duration': f"{ur.duration.total_seconds():.2f}" if ur.duration else "0.00"
        }
        for ur in unique_rounds
    ]
    return JsonResponse(data, safe=False)