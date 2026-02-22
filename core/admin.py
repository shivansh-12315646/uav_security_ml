from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DetectionHistory, Alert, AuditLog, MLModel


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'role', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'last_login_at')}),
    )
    readonly_fields = ('created_at', 'last_login_at', 'last_login')
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'email', 'password1', 'password2', 'role')}),
    )


@admin.register(DetectionHistory)
class DetectionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'prediction', 'confidence', 'threat_level', 'timestamp')
    list_filter = ('prediction', 'threat_level')
    search_fields = ('user__username', 'prediction')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'severity', 'status', 'created_at')
    list_filter = ('severity', 'status')
    ordering = ('-created_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action',)
    search_fields = ('user__username', 'action')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'accuracy', 'is_active', 'created_at')
    list_filter = ('is_active', 'name')
    ordering = ('-created_at',)
