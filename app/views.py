from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan
from django.contrib.auth.decorators import login_required
from django.utils import timezone

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
    return render(request, 'bookmark_create.html')

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
    return render(request, 'home.html', context)

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
    return render(request, 'bookmark_edit.html', context)

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
    return render(request, 'bookmark_delete.html', context)

@login_required
def plan_detail(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)  # 特定のプランを取得
    context = {
        'plan': plan  # プランの情報をコンテキストに渡す
    }
    return render(request, 'plan_detail.html', context)
