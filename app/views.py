from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives, send_mail
from django.contrib import messages
from .models import CustomUser, Application, Spot
from .forms import CustomUserCreationForm, AssociationApplicationForm, SpotForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_str
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
            return redirect('home')
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



# ログアウトビュー
def logoutView(request):
    logout(request)
    return redirect('login')

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