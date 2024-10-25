from django.shortcuts import render, redirect
from .models import Cost, Payment, Budget
from .forms import CostForm, PaymentForm, BudgetForm
from django.views import View
from django.contrib import messages
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
import json

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

            return redirect('app:cost_home', payer_name='みわ')
        
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
