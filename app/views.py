from django.shortcuts import render, redirect, get_object_or_404
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
from .models import Plan
from django.contrib.auth.decorators import login_required
from django.utils import timezone

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
            return redirect('login')
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

# プラン作成
@login_required
def create_plan(request):
    if request.method == 'POST':
        title = request.POST.get('trip-title')
        estimated_cost = request.POST.get('estimated-cost')
        departure_date = request.POST.get('departure-date')
        return_date = request.POST.get('return-date')
        image = request.FILES.get('image-upload')

        # Planモデルのインスタンスを作成して保存
        plan = Plan(
            title=title,
            start_dt=departure_date,
            end_dt=return_date,
            budget=estimated_cost,
            image=image,
        )
        plan.save()

        return redirect('home')
    return render(request, 'app/bookmark_create.html')

# ホーム画面
@login_required
def home(request):
    current_date = timezone.now().date()  # 現在の日付を取得
    # プランを現在の日付を基準に分けて取得
    upcoming_plans = Plan.objects.filter(start_dt__gte=current_date).order_by('start_dt')  # これからの予定
    past_plans = Plan.objects.filter(start_dt__lt=current_date).order_by('start_dt')  # 過去の予定

    context = {
        'upcoming_plans': upcoming_plans,
        'past_plans': past_plans
    }
    return render(request, 'app/home.html', context)

# プラン編集
@login_required
def edit_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    if request.method == 'POST':
        plan.title = request.POST.get('trip-title')
        plan.start_dt = request.POST.get('departure-date')
        plan.end_dt = request.POST.get('return-date')
        plan.budget = request.POST.get('estimated-cost')
        if request.FILES.get('image-upload'):
            plan.image = request.FILES.get('image-upload')

        plan.save()
        return redirect('home')

    context = {
        'plan': plan
    }
    return render(request, 'app/bookmark_edit.html', context)

# プラン削除
@login_required
def delete_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        plan.delete()
        return redirect('home')

    context = {
        'plan': plan
    }
    return render(request, 'app/bookmark_delete.html', context)

@login_required
def plan_detail(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)  # 特定のプランを取得
    context = {
        'plan': plan  # プランの情報をコンテキストに渡す
    }
    return render(request, 'app/plan_detail.html', context)


def get_events(request):
    return render(request, 'app/calendar.html')
