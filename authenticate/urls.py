from django.urls import path, reverse_lazy
from .views import CustomLoginView, CustomRegisterView, ActivateAccountView,CustomPasswordChangeView,update_avatar,profile_api,change_email,change_password,profile_page
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('accounts:login')), name='logout'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            success_url=reverse_lazy('accounts:password_reset_done')
        ),
        name='password_reset'
    ),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), 
         name='password_change_done'),
    path('update-avatar/', update_avatar, name='update_avatar'),
    path('api/profile/', profile_api, name='profile_api'),
    path('api/profile/change_email/', change_email, name='change_email'),
    path('api/profile/change_password/', change_password, name='change_password'),
    path('settings/', profile_page, name='settings'),
]