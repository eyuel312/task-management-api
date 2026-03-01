from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from apps.tasks.models import Task
from apps.projects.models import Project

@login_required
def dashboard(request):
    """Simple user dashboard for task management"""
    tasks = Task.objects.filter(user=request.user)
    projects = Project.objects.filter(user=request.user)
    
    context = {
        'tasks': tasks,
        'projects': projects,
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='completed').count(),
        'pending_tasks': tasks.filter(status='pending').count(),
    }
    return render(request, 'dashboard/home.html', context)

@csrf_exempt
@login_required
def quick_update_task(request, task_id):
    """AJAX endpoint for quick task updates"""
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id, user=request.user)
            data = json.loads(request.body)
            
            if 'status' in data:
                task.status = data['status']
                if task.status == 'completed':
                    task.completed_at = timezone.now()
                else:
                    task.completed_at = None
            
            task.save()
            
            return JsonResponse({
                'success': True,
                'status': task.status,
                'completed_at': task.completed_at
            })
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})