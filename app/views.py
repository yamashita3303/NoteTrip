from django.shortcuts import render, redirect
from .models import Cost, Payment
from .forms import CostForm, PaymentForm
from django.views import View

def cost_home(request):
    return render(request, "app/cost_home.html")

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
        print(request.POST)
        print(request.FILES)
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

            return redirect('app:cost_home')

        # フォームが無効なら再表示
        context = {
            'cost_form': cost_form,
        }
        return render(request, 'app/cost_form.html', context)

cost_create = CostCreateView.as_view()
