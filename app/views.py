from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from .models import CustomUser, Application, Spot
from .forms import CustomUserCreationForm, AssociationApplicationForm, SpotForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_str
from django.conf import settings

# ホームビュー
def homeView(request):
    user_application = None
    if request.user.is_authenticated:
        # ユーザーが認証されている場合、そのユーザーの申請を取得
        user_application = Application.objects.filter(applicant=request.user).first()

    # 承認ステータスをチェック
    if user_application and user_application.is_approved == 'approved':
        return redirect('add_spot', applicant_id=request.user.id)  # 承認時にスポット登録画面へリダイレクト
    elif user_application and user_application.is_approved == 'rejected':
        messages.error(request, '申請が却下されました。申請内容を再確認してください。')
    
    return render(request, 'app/home.html', {'user_application': user_application})


# ログインビュー
def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'ユーザー名とパスワードを入力してください')
            return render(request, 'app/login.html')

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
    if request.method == 'POST':
        form = AssociationApplicationForm(request.POST)
        if form.is_valid():
            # フォームデータを取得
            sei = form.cleaned_data['sei']
            mei = form.cleaned_data['mei']
            sei_kana = form.cleaned_data['sei_kana']
            mei_kana = form.cleaned_data['mei_kana']
            organization = form.cleaned_data['organization']
            position = form.cleaned_data['position']
            relationship_proof = form.cleaned_data['relationship_proof']

            # 申請オブジェクトの作成
            application = Application(
                applicant=request.user,  # 現在のユーザーを申請者として設定
                sei=sei,
                mei=mei,
                organization=organization,
                position=position,
                relationship_proof=relationship_proof,
            )
            application.save()  # 申請をデータベースに保存
            
            # 管理者に送信するメールの内容を作成
            applicant_id = request.user.id  # 現在のユーザーのIDを使用
            subject = '新しい申請が届きました'
            approve_link = f"{settings.SITE_URL}/approve_application/{applicant_id}/"
            reject_link = f"{settings.SITE_URL}/reject_application/{applicant_id}/"

            # HTMLメールの内容をレンダリング
            html_content = render_to_string('app/application_email.html', {
                'sei': sei,
                'mei': mei,
                'sei_kana': sei_kana,
                'mei_kana': mei_kana,
                'organization': organization,
                'position': position,
                'relationship_proof': relationship_proof,
                'approve_link': approve_link,
                'reject_link': reject_link,
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

            messages.success(request, '申請が成功しました！管理者が確認します。')
            return redirect('application_complete')  # 申請完了画面にリダイレクト
        else:
            messages.error(request, 'フォームにエラーがあります。再度入力してください。')
            print(form.errors)  # フォームのエラーを表示（デバッグ用）
    else:
        form = AssociationApplicationForm()

    return render(request, 'app/application.html', {'form': form})

# 申請完了ビュー
def application_completeView(request):
    return render(request, 'app/application_complete.html')  # 申請完了テンプレートを表示

# 申請キャンセルビュー
def application_cancelView(request, application_id):
    # 指定された申請を取得
    application = get_object_or_404(Application, id=application_id)

    # 申請者が現在のユーザーであることを確認
    if application.applicant == request.user:
        application.delete()  # 申請を削除
        messages.success(request, '申請がキャンセルされました。')
    else:
        messages.error(request, 'この申請をキャンセルする権限がありません。')

    return redirect('home')  # ホーム画面にリダイレクト

# 申請を許可するビュー
def approve_applicationView(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    application.status = 'approved'
    application.save()
    messages.success(request, '申請が承認されました。')
    return redirect('home')  # ホーム画面へリダイレクト

# 申請を却下するビュー
def reject_applicationView(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    application.status = 'rejected'
    application.save()
    messages.error(request, '申請が却下されました。')
    return redirect('home')  # ホーム画面へリダイレクト


# ログアウトビュー
def logoutView(request):
    logout(request)
    return redirect('login')

# おすすめスポット追加ビュー
def add_spot(request, applicant_id):
    if request.method == 'POST':
        form = SpotForm(request.POST)
        if form.is_valid():
            # データを一時的にセッションに保存し、確認画面へ
            request.session['spot_data'] = form.cleaned_data
            return redirect('add_spot_confirmation')
    else:
        form = SpotForm()
    return render(request, 'app/application_form.html', {'form': form, 'applicant_id': applicant_id})

# おすすめスポット登録内容確認ビュー
def add_spot_confirmation(request):
    spot_data = request.session.get('spot_data')
    if not spot_data:
        return redirect('add_spot')

    form = SpotForm(initial=spot_data)
    if request.method == 'POST':
        form = SpotForm(spot_data)
        if form.is_valid():
            form.save()
            messages.success(request, 'スポットが登録されました！')
            return redirect('add_spot_success')
    return render(request, 'app/application_form_confirmation.html', {'form': form})

# おすすめスポット登録完了ビュー
def add_spot_success(request):
    return render(request, 'app/application_form_success.html')