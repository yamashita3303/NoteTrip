from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_str

# ホームビュー
def homeView(request):
    return render(request, 'app/home.html')

# ログインビュー
def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # ログイン後のリダイレクト先
        else:
            messages.error(request, 'ユーザー名かパスワードが間違っています')
    return render(request, 'app/login.html')

# 新規登録ビュー
def signupView(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'アカウントが作成されました')
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/signup.html', {'form': form})

# パスワード再設定ビュー
def password_resetView(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = CustomUser.objects.get(email=email)
            # パスワードリセットのトークンを生成
            subject = 'パスワードリセットのリクエスト'
            email_template_name = 'app/password_reset_email.html'
            context = {
                'email': user.email,
                'domain': request.get_host(),
                'site_name': 'Your Site Name',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }

            # リセットリンクの生成
            reset_link = f"{context['protocol']}://{context['domain']}/password_reset_confirm/{context['uid']}/{context['token']}/"
            context['reset_link'] = reset_link  # コンテキストに追加

            # メールのコンテンツを生成
            html_content = render_to_string(email_template_name, context)
            text_content = strip_tags(html_content)

            # EmailMultiAlternativesを使ってメールを送信
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='from@example.com',
                to=[user.email],
            )
            email_message.attach_alternative(html_content, 'text/html')
            email_message.send()

            messages.success(request, 'パスワードリセットリンクを送信しました')
            return redirect('password_reset_done')
        except CustomUser.DoesNotExist:
            messages.error(request, 'そのメールアドレスは登録されていません')
    return render(request, 'app/password_reset.html')

def password_reset_confirmView(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'パスワードがリセットされました。')
            return redirect('login')
        return render(request, 'app/password_reset_confirm.html', {'validlink': True})
    else:
        messages.error(request, '無効なリンクです。')
        return render(request, 'app/password_reset_confirm.html', {'validlink': False})
    
# 送信完了ビュー
def password_reset_doneView(request):
    return render(request, 'app/password_reset_done.html')



# ログアウトビュー
def logoutView(request):
    logout(request)
    return redirect('login')
