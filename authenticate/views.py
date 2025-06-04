from django.shortcuts import render,redirect
from django.views.generic import CreateView
from quiz.models import CustomUser
from django.contrib.auth.views import LoginView,LogoutView,PasswordChangeView
from .forms import CustomUserCreationForm,AvatarUpdateForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password, ValidationError

class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('quiz:index')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
    def form_invalid(self, form):
        messages.error(self.request,"The entered data is incorrect, please check.")
        return super().form_invalid(form)
    

class CustomRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('quiz:index')  

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request,"You have successfully registered!")
        return response
    def form_invalid(self, form):
        messages.error(self.request, "Please fill out the form correctly!")
        return super().form_invalid(form)
    

from django.views import View

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_email_verified = True
            user.save()
            messages.success(request, "Email tasdiqlandi, endi login qilishingiz mumkin.")
            return redirect('accounts:login')
        else:
            return HttpResponse('Aktivatsiya havolasi noto‘g‘ri yoki eskirgan.', status=400)
        

def custom_logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('accounts:login')


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')

@login_required
def update_avatar(request):
    if request.method == 'POST':
        form = AvatarUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('quiz:kabinet')  # profile sahifangiz yo‘nalishini yozing
    else:
        form = AvatarUpdateForm(instance=request.user)
    return render(request, 'accounts/update_avatar.html', {'form': form})



@login_required
def profile_page(request):
    return render(request, 'settings.html', {"user": request.user})

@login_required
def profile_api(request):
    user = request.user
    return JsonResponse({
        "username": user.username,
        "email": user.email,
    })

@login_required
@require_POST
def change_email(request):
    import json
    data = json.loads(request.body)
    new_email = data.get('email', '').strip()
    if not new_email:
        return JsonResponse({'success': False, 'error': 'Email cannot be blank.'}, status=400)
    if request.user.email == new_email:
        return JsonResponse({'success': False, 'error': 'This is already your email.'}, status=400)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
        return JsonResponse({'success': False, 'error': 'This email is already taken.'}, status=400)
    request.user.email = new_email
    request.user.save()
    return JsonResponse({'success': True, 'email': new_email})

@login_required
@require_POST
def change_password(request):
    import json
    data = json.loads(request.body)
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    if not old_password or not new_password or not confirm_password:
        return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)
    if new_password != confirm_password:
        return JsonResponse({'success': False, 'error': 'New password and confirm password do not match.'}, status=400)
    if not request.user.check_password(old_password):
        return JsonResponse({'success': False, 'error': 'Old password is incorrect.'}, status=400)
    try:
        validate_password(new_password, user=request.user)
    except ValidationError as ve:
        return JsonResponse({'success': False, 'error': '; '.join(ve.messages)}, status=400)
    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)  # So user doesn't get logged out
    return JsonResponse({'success': True})