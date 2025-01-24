from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives, send_mail
from django.contrib import messages
from django.views import View
from .models import CustomUser, Application, Spot, Plan, Checklist, Schedule
from .forms import CustomUserCreationForm, PlanForm, Scheduleform, ChecklistForm, AssociationApplicationForm, SpotForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_str
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# ホームビュー
@login_required
def homeView(request):
    print("homeViewの実行開始")
    user_application = Application.objects.filter(applicant=request.user).first()  # ユーザーの申請を取得

    if user_application:
        print(f"ユーザーの申請が見つかりました: {user_application.id}")
        if user_application.status == 'approved':
            print("申請が承認されました。")
            print(user_application.id)
            # applicant_idをテンプレートに渡す
            return render(request, 'app/home.html', {
                'user_application': user_application,
                'applicant_id': user_application.id,
            })
        elif user_application.status == 'rejected':
            print("申請が却下されました。")
            messages.error(request, '申請が却下されました。申請内容を再確認してください。')  # 申請が却下されていればエラーメッセージを表示
    
    # 申請がない場合、または未承認の場合の処理
    print("申請がない、または未承認です。")
    return render(request, 'app/home.html', {
        'user_application': user_application,
        'applicant_id': None,  # デフォルト値としてNoneを渡す
    })

# ログインビュー
def loginView(request):
    print("loginViewの実行開始")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            print("ユーザー名またはパスワードが不足しています")
            messages.error(request, 'ユーザー名とパスワードを入力してください')
            return render(request, 'app/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"ログイン成功: {user.username}")
            login(request, user)
            return redirect('home')  # ログイン後のリダイレクト先
        else:
            print("ログイン失敗: ユーザー名またはパスワードが間違っています")
            messages.error(request, 'ユーザー名かパスワードが間違っています')
    return render(request, 'app/login.html')

def admin_loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:  # 管理者ユーザーを認証
            login(request, user)
            return redirect('dashboard')  # ダッシュボードにリダイレクト
        else:
            error_message = "管理者権限が必要です"
            return render(request, 'app/admin_login.html', {'error_message': error_message})
    return render(request, 'app/admin_login.html')


# 新規登録ビュー
def signupView(request):
    print("signupViewの実行開始")
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("アカウント作成成功")
            form.save()
            messages.success(request, 'アカウントが作成されました')
            return redirect('login')
        else:
            print(f"フォームエラー: {form.errors}")
            messages.error(request, 'アカウント作成に失敗しました。再度お試しください。')
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/signup.html', {'form': form})

# パスワード再設定ビュー
def password_resetView(request):
    print("password_resetViewの実行開始")
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = CustomUser.objects.get(email=email)
            # パスワードリセットのトークンを生成
            subject = 'パスワードリセットのリクエスト'
            email_template_name = 'app/password_reset_email.html'
            context = {
                'email': user.email,
                'site_name': 'Your Site Name',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }

            # リセットリンクの生成
            reset_link = f"{settings.SITE_URL}/password_reset_confirm/{context['uid']}/{context['token']}/"
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

            print("パスワードリセットリンク送信成功")
            messages.success(request, 'パスワードリセットリンクを送信しました')
            return redirect('password_reset_done')
        except CustomUser.DoesNotExist:
            print("そのメールアドレスは登録されていません")
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
            new_password = request.POST['new_password']  # 新しいパスワード
            new_password_confirm = request.POST['new_password_confirm']  # 確認用パスワード

            if new_password == new_password_confirm:  # パスワードが一致するか確認
                user.set_password(new_password)
                user.save()
                messages.success(request, 'パスワードがリセットされました。')
                return redirect('login')
            else:
                messages.error(request, 'パスワードが一致しません。再度入力してください。')
                return render(request, 'app/password_reset_confirm.html', {'validlink': True})
        return render(request, 'app/password_reset_confirm.html', {'validlink': True})
    else:
        messages.error(request, '無効なリンクです。')
        return render(request, 'app/password_reset_confirm.html', {'validlink': False})

# 送信完了ビュー
def password_reset_doneView(request):
    return render(request, 'app/password_reset_done.html')

# 申請ビュー
def applicationView(request):
    print("applicationViewの実行開始")
    if request.method == 'POST':
        form = AssociationApplicationForm(request.POST)
        if form.is_valid():
            print("申請フォームが有効です")
            # フォームデータを取得して保存
            application = Application(
                applicant = request.user,
                sei = form.cleaned_data['sei'],
                mei = form.cleaned_data['mei'],
                sei_kana = form.cleaned_data['sei_kana'],
                mei_kana = form.cleaned_data['mei_kana'],
                organization = form.cleaned_data['organization'],
                position = form.cleaned_data['position'],
                relationship_proof = form.cleaned_data['relationship_proof'],
                status='pending',  # 初期状態を設定
            )
            application.save()  # データベースに保存

            # 管理者に送信するメールの内容を作成
            subject = '新しい申請が届きました'
            
            html_content = render_to_string('app/application_email.html', {
                'application_id': application.id,
                'username': application.applicant.username,
                'sei': application.sei,
                'mei': application.mei,
                'sei_kana': application.sei_kana,
                'mei_kana': application.mei_kana,
                'organization': application.organization,
                'position': application.position,
                'relationship_proof': application.relationship_proof,
            })

            # EmailMultiAlternativesを使ってメールを送信
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=strip_tags(html_content),  # プレーンテキスト版
                from_email=settings.EMAIL_HOST_USER,
                to=['fko2347019@stu.o-hara.ac.jp'],  # 管理者のメールアドレス
            )
            email_message.attach_alternative(html_content, 'text/html')  # HTML版を添付
            email_message.send()

            print("申請メール送信成功")
            return redirect('application_complete')  # 申請完了画面にリダイレクト
        else:
            print(f"フォームにエラーがあります: {form.errors}")
            messages.error(request, 'フォームにエラーがあります。再度入力してください。')
    else:
        form = AssociationApplicationForm()

    return render(request, 'app/application.html', {'form': form})

# 申請完了ビュー
def application_completeView(request):
    print("申請完了ビューが呼ばれました")
    return render(request, 'app/application_complete.html')  # 申請完了テンプレートを表示

# ダッシュボードビュー
def dashboardView(request):
    if not request.user.is_staff:
        return redirect('home')  # 管理者以外はホームにリダイレクト
    
    spots = Spot.objects.all()  # 全てのスポットを取得
    status_filter = request.GET.get('status', 'pending')  # URLのクエリパラメータから状態を取得
    tab = request.GET.get('tab', 'requests')  # タブの状態を取得
    
    # 状態に基づいてフィルタリング
    if status_filter == 'approved':
        applications = Application.objects.filter(status=Application.APPROVED)
    elif status_filter == 'rejected':
        applications = Application.objects.filter(status=Application.REJECTED)
    else:
        applications = Application.objects.filter(status=Application.PENDING)
    
    return render(request, 'app/dashboard.html', {'applications': applications, 'spots': spots, 'status_filter': status_filter, 'tab': tab})

def approve_application(request, application_id):
    application = Application.objects.get(id=application_id)
    # 承認処理
    if application:
        application.status = 'approved'
        application.save()
        messages.success(request, '申請が承認されました。')  # 承認メッセージ
    else:
        messages.error(request, '操作できません。すでに承認または却下されています。')
    return redirect('dashboard')  # ダッシュボードにリダイレクト

def reject_application(request, application_id):
    application = Application.objects.get(id=application_id)
    # 却下処理
    if application:
        application.status = 'rejected'
        application.save()
        messages.error(request, '申請が却下されました。')  # 却下メッセージ
    else:
        messages.error(request, '操作できません。すでに承認または却下されています。')
    return redirect('dashboard')  # ダッシュボードにリダイレクト

def delete_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    # 削除処理
    application.delete()
    messages.success(request, '申請が削除されました。')
    # 削除後にリダイレクト
    return redirect('dashboard')




# おすすめスポット追加ビュー
def add_spot(request, applicant_id):
    print(f"おすすめスポット追加ビューが呼ばれました (Applicant ID: {applicant_id})")
    if request.method == 'POST':
        form = SpotForm(request.POST)
        if form.is_valid():
            # データを一時的にセッションに保存し、確認画面へ
            print("フォームデータが有効です。セッションに保存します。")
            request.session['spot_data'] = form.cleaned_data
            return redirect('add_spot_confirmation', applicant_id=applicant_id)
        else:
            print("フォームにエラーがあります。")
    else:
        form = SpotForm()
    return render(request, 'app/application_form.html', {'form': form, 'applicant_id': applicant_id})

# おすすめスポット登録内容確認ビュー
def add_spot_confirmation(request, applicant_id):
    print("スポット登録確認ビューが呼ばれました")
    spot_data = request.session.get('spot_data')
    if not spot_data:
        print("セッションにスポットデータがありません。リダイレクトします。")
        return redirect('add_spot')

    form = SpotForm(initial=spot_data)
    if request.method == 'POST':
        form = SpotForm(spot_data)
        if form.is_valid():
            print("スポットデータが有効です。保存します。")
            form.save()
            messages.success(request, 'スポットが登録されました！')
            return redirect('add_spot_success', applicant_id=applicant_id)
        else:
            print("フォームにエラーがあります。")
    return render(request, 'app/application_form_confirmation.html', {'form': form, 'applicant_id': applicant_id})

# おすすめスポット登録完了ビュー
def add_spot_success(request, applicant_id=None):
    print("おすすめスポット登録完了ビューが呼ばれました")
    context = {'applicant_id': applicant_id}
    return render(request, 'app/application_form_success.html', context)

# おすすめスポット削除ビュー
def delete_spot(request, spot_id):
    spot = get_object_or_404(Spot, id=spot_id)
    # 削除処理
    spot.delete()
    # 削除後にリダイレクト
    return redirect('dashboard')

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
    print("homeViewの実行開始")
    user = request.user  # ログイン中のユーザーを取得
    current_date = timezone.now().date()  # 現在の日付を取得

    # ユーザーの申請情報を取得
    user_application = Application.objects.filter(applicant=user).first()  

    if user_application:
        print(f"ユーザーの申請が見つかりました: {user_application.id}")
        if user_application.status == 'approved':
            print("申請が承認されました。")
            applicant_id = user_application.id
        elif user_application.status == 'rejected':
            print("申請が却下されました。")
            messages.error(request, '申請が却下されました。申請内容を再確認してください。')
            applicant_id = None
        else:
            print("申請が未承認です。")
            applicant_id = None
    else:
        print("申請が見つかりませんでした。")
        applicant_id = None

    # `user`または`members`に現在のユーザーが含まれているプランを取得
    upcoming_plans = Plan.objects.filter(
        Q(start_dt__gte=current_date) & (Q(user=user) | Q(members=user))
    ).order_by('start_dt')  # これからの予定

    past_plans = Plan.objects.filter(
        Q(start_dt__lt=current_date) & (Q(user=user) | Q(members=user))
    ).order_by('start_dt')  # 過去の予定

    context = {
        'upcoming_plans': upcoming_plans,
        'past_plans': past_plans,
        'user_application': user_application,
        'applicant_id': applicant_id,  # 申請IDを渡す
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
    return render(request, 'app/schedule_edit.html',  {'form': form, 'plan': plan, 'schedule': schedule})

#スケジュール削除確認画面
def schedule_kakunin(request, plan_id, schedule_id):
    # スケジュールを取得
    schedule = get_object_or_404(Schedule, id=schedule_id, plan_id=plan_id)
    
    # テンプレートにスケジュールを渡してレンダリング
    return render(request, 'app/schedule_kakunin.html', {'schedule': schedule})

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

class LogoutView(View):

    # ログアウトビュー
    def get(self, request):
        return render(request, 'app/logout.html')

    def post(self, request):
        logout(request)
        return redirect('login')
    
logout_view = LogoutView.as_view() 

