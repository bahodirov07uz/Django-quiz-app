from django.contrib import admin
from django.urls import path,include
from .views import Home, game_view, RoundListView, TopicListView, QuestionListView, SubmitAnswerView,load_all_rounds,top_reyting_for_round
from .views import RoundDetailView,RoundQuestionsCountView,SaveScoreView,SaveUserRoundView,kabinet_view,top_reyting,check_user_round,start_user_round
from django.conf import settings
from django.conf.urls.static import static
app_name = 'quiz'
urlpatterns = [
    path('',Home.as_view(), name='index'),
    path('game/', game_view, name='game'),
    path('api/rounds/', RoundListView.as_view(), name='round-list'),
    path('api/topics/', TopicListView.as_view(), name='topic-list'),
    path('api/questions/', QuestionListView.as_view(), name='question-list'),
    path('api/submit-answer/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('ajax/load-rounds/', load_all_rounds, name='load_rounds'),
    path('api/rounds/<int:pk>/', RoundDetailView.as_view(), name='round-detail'),
    path('api/rounds/<int:pk>/questions-count/', RoundQuestionsCountView.as_view(), name='round-questions-count'),
    path('api/save-score/', SaveScoreView.as_view(), name='save-score'),
    path('api/save-user-round/', SaveUserRoundView.as_view(), name='save-user-round'),
    path('kabinet/', kabinet_view, name='kabinet'),
    path('api/top-reyting/', top_reyting, name='top-reyting'),
    path('api/check-user-round/', check_user_round, name='check_user_round'),
    path('api/start-user-round/', start_user_round, name='start_user_round'),
    path('api/round/<int:round_id>/top-reyting/', top_reyting_for_round, name='top_reyting_for_round'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
