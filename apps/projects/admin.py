from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model"""
    
    list_display = ('name', 'user_email', 'task_count', 'completed_tasks_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'user__email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'description', 'user')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'task_count_display', 'completed_tasks_display')
    raw_id_fields = ('user',)
    list_per_page = 25
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Total Tasks'
    
    def completed_tasks_count(self, obj):
        return obj.tasks.filter(status='completed').count()
    completed_tasks_count.short_description = 'Completed'
    
    def task_count_display(self, obj):
        return f"{obj.tasks.count()} total tasks"
    task_count_display.short_description = 'Task Count'
    
    def completed_tasks_display(self, obj):
        completed = obj.tasks.filter(status='completed').count()
        total = obj.tasks.count()
        if total > 0:
            percentage = (completed / total) * 100
            return f"{completed}/{total} tasks completed ({percentage:.1f}%)"
        return "No tasks yet"
    completed_tasks_display.short_description = 'Progress'