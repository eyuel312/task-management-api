from django.contrib import admin
from django.utils.html import format_html
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model"""
    
    list_display = ('title', 'user_email', 'status', 'priority', 'due_date', 'project_name', 'created_at')
    list_filter = ('status', 'priority', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'user__email', 'project__name')
    ordering = ('-created_at',)
    
    # Organize fields into sections
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'user', 'project')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at')
        }),
    )
    
    # Read-only fields
    readonly_fields = ('created_at', 'updated_at', 'formatted_description')
    
    # Raw ID fields for foreign keys (better for performance)
    raw_id_fields = ('user', 'project')
    
    # List per page
    list_per_page = 25
    
    # Custom methods for list display
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def project_name(self, obj):
        return obj.project.name if obj.project else '-'
    project_name.short_description = 'Project'
    
    def formatted_description(self, obj):
        """Display description with line breaks preserved"""
        if obj.description:
            return format_html('<pre>{}</pre>', obj.description[:200])
        return '-'
    formatted_description.short_description = 'Description Preview'
    
    # Actions
    actions = ['mark_as_completed', 'mark_as_in_progress', 'mark_as_pending']
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} tasks marked as completed.')
    mark_as_completed.short_description = "Mark selected tasks as completed"
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} tasks marked as in progress.')
    mark_as_in_progress.short_description = "Mark selected tasks as in progress"
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} tasks marked as pending.')
    mark_as_pending.short_description = "Mark selected tasks as pending"