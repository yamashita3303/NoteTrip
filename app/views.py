from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from .models import CustomUser, Plan, Checklist, Schedule
from .forms import CustomUserCreationForm, PlanForm, Scheduleform, ChecklistForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_str
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

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
        user = request.user
        title = request.POST.get('trip-title')
        estimated_cost = request.POST.get('estimated-cost')
        departure_date = request.POST.get('departure-date')
        return_date = request.POST.get('return-date')
        image = request.FILES.get('image-upload')

        # Planモデルのインスタンスを作成して保存
        plan = Plan(
            user=user,
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
    user = request.user  # ログイン中のユーザーを取得
    print("--------", user, "--------")
    current_date = timezone.now().date()  # 現在の日付を取得

    # `user`または`members`に現在のユーザーが含まれているプランを取得
    upcoming_plans = Plan.objects.filter(
        Q(start_dt__gte=current_date) & (Q(user=user) | Q(members=user))
    ).order_by('start_dt')  # これからの予定

    past_plans = Plan.objects.filter(
        Q(start_dt__lt=current_date) & (Q(user=user) | Q(members=user))
    ).order_by('start_dt')  # 過去の予定

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
        user = request.user
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

def member(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)  # 特定のプランを取得
    context = {
        'plan': plan  # プランの情報をコンテキストに渡す
    }
    return render(request, 'app/member.html', context)

class ShareView(View):
    def get(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)  # 特定のプランを取得
        context = {
            'plan': plan  # プランの情報をコンテキストに渡す
        }
        return render(request, 'app/share.html', context)

    def post(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            subject = 'NoteTrip プラン共有のお知らせ'
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # 承認リンクの生成
            approval_link = request.build_absolute_uri(f'/approve/{plan_id}/{uid}/{token}/')
            context = {
                'plan': plan,
                'user': user,
                'approval_link': approval_link,
            }

            # メールコンテンツを生成して送信
            html_content = render_to_string('app/share_email.html', context)
            text_content = strip_tags(html_content)
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='from@example.com',
                to=[user.email],
            )
            email_message.attach_alternative(html_content, 'text/html')
            email_message.send()
            
            messages.success(request, 'プラン共有メールが送信されました')
            return redirect('plan_detail', plan_id=plan_id)

        except CustomUser.DoesNotExist:
            messages.error(request, 'そのメールアドレスは登録されていません')
            return redirect('share', plan_id=plan_id)

share = ShareView.as_view()

def approve_view(request, plan_id, uid, token):
    try:
        uid = urlsafe_base64_decode(uid).decode()
        user = CustomUser.objects.get(pk=uid)
        plan = get_object_or_404(Plan, id=plan_id)

        # Tokenの確認
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                if 'accept' in request.POST:
                    plan.members.add(user)  # メンバーとして登録
                    login(request, user)
                    messages.success(request, 'プランに参加しました。')
                else:
                    messages.info(request, 'プラン参加を拒否しました。')
                return redirect('home')
            return render(request, 'app/approve.html', {'plan': plan, 'user': user})

        else:
            messages.error(request, 'このリンクは無効です。')
            return redirect('home')
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        messages.error(request, '無効なリンクです。')
        return redirect('home')
    
def schedule(request, plan_id):
    # デフォルトで1日目を取得
    day = request.GET.get('day', 1)
    if request.method == 'POST':
        day = request.POST.get('day')

    try:
        day = int(day)
    except ValueError:
        day = 1  # dayの取得に失敗した場合は1日目にリセット

    print(f"Selected day: {day}")  # デバッグ用

    # Planインスタンスの取得
    plan = get_object_or_404(Plan, id=plan_id)
    plan_days = (plan.end_dt - plan.start_dt).days + 1  # 総日数の計算
    plan_days_range = range(1, plan_days + 1)  # 範囲を生成

    # 特定の日に紐づくスケジュールの取得
    schedules = Schedule.objects.filter(plan=plan, day=day)
    print(f"Schedules for day {day}: {schedules}")  # デバッグ用

    context = {
        'plan': plan,
        'plan_days_range': plan_days_range,
        'schedules': schedules,
        'select_day': day,  # テンプレートに渡す選択日
    }

    return render(request, 'app/schedule.html', context)

# スケジュール詳細表示
def schedule_detail(request, plan_id, schedule_id):
    plan = get_object_or_404(Plan, id=plan_id)
    schedule = get_object_or_404(Schedule, id=schedule_id)
    return render(request, 'app/schedule_detail.html', {'plan': plan, 'schedule': schedule})

# スケジュール作成
def schedule_create(request, plan_id, day):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        form = Scheduleform(request.POST)
        print(request.POST)  # デバッグ用
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.plan = plan
            schedule.day = day  # dayが適切に保存されるか確認
            schedule.save()
            print(f"Schedule saved with day: {schedule.day}")  # デバッグ用
            return redirect('schedule', plan_id=plan_id)
    else:
        form = Scheduleform()
    return render(request, 'app/schedule_form.html', {'form': form})

# スケジュール編集
def schedule_edit(request, plan_id, schedule_id):
    plan = get_object_or_404(Plan, id=plan_id)
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == 'POST':
        form = Scheduleform(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect('schedule', plan_id=plan_id)
    else:
        form = Scheduleform(instance=schedule)
    return render(request, 'app/schedule_edit.html', {'form': form, 'plan': plan, 'schedule': schedule})

# スケジュール削除
def schedule_delete(request, plan_id, schedule_id):
    plan = get_object_or_404(Plan, id=plan_id)
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == "POST":
        schedule.delete()  # スケジュールを削除
        return redirect('schedule', plan_id=plan_id)  # インデックスページにリダイレクト
    return render(request, 'app/schedule_delete.html', {'plan': plan, 'schedule': schedule})


def checklist_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    items = Checklist.objects.all()
    
    context = {
        'plan': plan,
        'items': items
    }

    return render(request, 'app/checklist.html', context)

def add_item_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        form = ChecklistForm(request.POST)
        if form.is_valid():
            checklist = form.save(commit=False)
            checklist.plan = plan
            checklist.save()
            return redirect('checklist', plan_id=plan_id)
    else:
        form = ChecklistForm()
    return render(request, 'app/add_item.html', {'plan': plan, 'form': form})

def top(request):
    return render(request, 'app/top.html')