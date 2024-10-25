from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser, Cost, Payment, Budget
from .forms import CustomUserCreationForm, CostForm, PaymentForm, BudgetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_str
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
import json


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

def cost_home(request, payer_name):
    payments_by_payers = Payment.objects.values('payment_payers').annotate(total_money=Sum('payment_money'))
    payments_json = json.dumps(list(payments_by_payers), cls=DjangoJSONEncoder)
    
    # 指定した支払者のジャンル別支出の合計を取得
    payments_by_genre = Payment.objects.filter(payment_payers=payer_name)\
        .values('cost__cost_genre')\
        .annotate(total_money=Sum('payment_money'))
    # JSON形式に変換
    alone_payments_json = json.dumps(list(payments_by_genre), cls=DjangoJSONEncoder)
    
    context = {
        'payments_json': payments_json,
        'alone_payments_json': alone_payments_json,
        'payer_name': payer_name,  # 支払者名もコンテキストに渡す
    }

    return render(request, "app/cost_home.html", context)

def cost_list(request):
    all_costs = Cost.objects.all()
    all_payments = Payment.objects.all()
    context = {
        'all_costs': all_costs,
        'all_payments': all_payments,
    }
    return render(request, "app/cost_list.html", context)

class CostCreateView(View):
    # GETリクエストの処理
    def get(self, request):
        # インスタンスの作成
        cost_form = CostForm()
        payment_form = PaymentForm()

        context = {
            'cost_form': cost_form,
            'payment_form': payment_form,
        }
        return render(request, 'app/cost_form.html', context)
    
    # POSTリクエストの処理
    def post(self, request):
        # インスタンスの作成
        cost_form = CostForm(request.POST, request.FILES)

        # フォームが有効かチェック
        if cost_form.is_valid():
            # 支払い情報を保存
            cost = cost_form.save(commit=False)
            cost.user = request.user  # ログインしているユーザーを設定
            cost.save()

            # 支払者と費用を取得
            payers = request.POST.getlist('payment_payers')  # 'payers'のリストを取得
            print(payers)
            money = request.POST.getlist('payment_money')    # 'money'のリストを取得
            print(money)

             # 支払い情報を保存
            for payers, money in zip(payers, money):
                payment = Payment(
                    cost=cost,
                    payment_payers=payers,
                    payment_money=money
                )
                payment.save()

            return redirect('cost_home', payer_name='みわ')
        
        # フォームが無効なら再表示
        context = {
            'cost_form': cost_form,
        }
        return render(request, 'app/cost_form.html', context)

cost_create = CostCreateView.as_view()

def cost_budget(request):
    print("---")
    if request.method == 'POST':
        budget_form = BudgetForm(request.POST)
        print("0")
        if budget_form.is_valid():
            print("1")
            try:
                print("2")
                budget_form.save()
                messages.success(request, "予算が追加されました。")
                return redirect('app:cost_home', payer_name='みわ')  # 一覧ページなどにリダイレクト
            except Exception as e:
                messages.error(request, f"エラーが発生しました: {e}")
        else:
            messages.error(request, "フォームにエラーがあります。")
            print(budget_form.errors)  # エラー内容をコンソールに出力
    else:
        budget_form = BudgetForm()

    context = {
        'budget_form': budget_form,
    }

    return render(request, 'app/cost_budget.html', context)


# class BudgetCreateView(View):
#     # GETリクエストの処理
#     def get(self, request):
#         # インスタンスの作成
#         budget_form = BudgetForm()

#         context = {
#             'budget_form': budget_form,
#         }
#         return render(request, 'app/cost_budget.html', context)
    
#     # POSTリクエストの処理
#     def post(self, request):
#         # インスタンスの作成
#         cost_form = CostForm(request.POST, request.FILES)

#         # フォームが有効かチェック
#         if cost_form.is_valid():
#             # 支払い情報を保存
#             cost = cost_form.save(commit=False)
#             cost.save()

# cost_budget = BudgetCreateView.as_view()
