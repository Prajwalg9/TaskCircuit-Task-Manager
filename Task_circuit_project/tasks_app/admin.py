from django.contrib import admin
from .models import UserProfile, Task

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'unique_key', 'age', 'dark_theme', 'date_of_register']
    list_filter = ['dark_theme', 'date_of_register']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'unique_key']
    readonly_fields = ['date_of_register']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'unique_key')
        }),
        ('Profile Details', {
            'fields': ('profile_picture', 'age', 'dark_theme')
        }),
        ('Registration', {
            'fields': ('date_of_register',)
        }),
    )

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'scheduled_date', 'completed', 'created_at']
    list_filter = ['priority', 'completed', 'scheduled_date', 'created_at']
    search_fields = ['title', 'user__username']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'title', 'priority')
        }),
        ('Schedule', {
            'fields': ('scheduled_date',)
        }),
        ('Status', {
            'fields': ('completed', 'completed_at', 'created_at')
        }),
    )
    readonly_fields = ['created_at', 'completed_at']
