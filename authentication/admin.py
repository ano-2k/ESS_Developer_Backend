from django.contrib import admin
from .models import Admin

@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ['username', 'user_id', 'email']
    list_filter = ['username']
    search_fields = ['username', 'email', 'user_id']
    readonly_fields = ['password']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'user_id', 'email')
        }),
        ('Security', {
            'fields': ('password',),
            'classes': ('collapse',),
            'description': 'Password is automatically hashed'
        }),
        ('Features & Reset Token', {
            'fields': ('features', 'reset_token', 'token_expiration'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser