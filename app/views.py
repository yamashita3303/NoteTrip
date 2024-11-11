from django.shortcuts import render, get_object_or_404, redirect
from .models import Schedule
from .forms import Scheduleform  # Schedule作成フォーム
from django.http import HttpResponse

def index(request):
    day_count = 5  # 表示したい日数の上限
    # 日ごとのスケジュールを格納する辞書
    schedules_by_day = {day: [] for day in range(1, day_count + 1)}
    
    # 各スケジュールを日ごとに分類して辞書に格納
    for schedule in Schedule.objects.all():
        if schedule.day in schedules_by_day:
            schedules_by_day[schedule.day].append(schedule)

    return render(request, 'app/index.html', {'schedules_by_day': schedules_by_day})

# スケジュール詳細表示
def schedule_detail(request, pk):
    schedule = get_object_or_404(Schedule, id=pk)
    return render(request, 'app/schedule_detail.html', {'schedule': schedule})

# スケジュール作成
def schedule_create(request, day):
    if request.method == 'POST':
        form = Scheduleform(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.day = day  # タブの情報に基づき日数を設定
            schedule.save()
            return redirect('app:index')
    else:
        form = Scheduleform()
    return render(request, 'app/schedule_form.html', {'form': form})

# スケジュール編集
def schedule_edit(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == 'POST':
        form = Scheduleform(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect('app:index')
    else:
        form = Scheduleform(instance=schedule)
    return render(request, 'app/schedule_edit.html', {'form': form, 'schedule': schedule})

# スケジュール削除
def schedule_delete(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == "POST":
        schedule.delete()  # スケジュールを削除
        return redirect('app:index')  # インデックスページにリダイレクト
    return render(request, 'app/schedule_delete.html', {'schedule': schedule})
