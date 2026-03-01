from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_future_date(value):
    """Validator ensuring a DateTimeField value is in the future."""
    if value and value < timezone.now():
        raise ValidationError("Due date must be in the future.")


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', ' In Progress'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)  # New field
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Set completed_at timestamp when task is marked as completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        # Clear completed_at if task is not completed
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)