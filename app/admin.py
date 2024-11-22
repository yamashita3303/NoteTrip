from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from .models import CustomUser, Application, Spot
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Plan
from .models import Schedule
from .models import Checklist

class MyAdminSite(AdminSite):
    site_header = 'My Custom Admin'  # 管理者ページのヘッダーをカスタマイズ
    site_title = 'Admin Dashboard'

    # 管理者ログインページをカスタマイズするためにURLを設定
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('login/', self.admin_view(self.custom_admin_login), name='custom_admin_login'),
        ]
        return custom_urls + urls

    def custom_admin_login(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/admin/')  # ログインしていれば管理者ダッシュボードにリダイレクト
        # ここでカスタムのログインフォームを表示
        return render(request, 'admin/login.html', {})

# MyAdminSite をインスタンス化
admin_site = MyAdminSite(name='myadmin')

# Applicationモデルを管理画面でカスタマイズ
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('sei', 'mei', 'status', 'created_at', 'applicant')
    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        """選択した申請を承認する"""
        updated_count = queryset.update(status='approved')
        self.message_user(request, f"{updated_count} 件の申請が承認されました。", level=messages.SUCCESS)

    def reject_applications(self, request, queryset):
        """選択した申請を却下する"""
        updated_count = queryset.update(status='rejected')
        self.message_user(request, f"{updated_count} 件の申請が却下されました。", level=messages.WARNING)

    approve_applications.short_description = "選択した申請を承認"
    reject_applications.short_description = "選択した申請を却下"

# 管理画面にApplicationモデルを登録
admin.site.register(Application, ApplicationAdmin)

# モデルの登録
admin_site.register(CustomUser)
admin_site.register(Spot)
admin.site.register(CustomUser)
admin.site.register(Plan)
admin.site.register(Schedule)
admin.site.register(Checklist)
