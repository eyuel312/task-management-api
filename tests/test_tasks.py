from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from apps.tasks.models import Task

User = get_user_model()

class TaskTests(TestCase):
    """Test cases for tasks app"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create user
        self.user = User.objects.create_user(
            email='user@example.com',
            name='Task User',
            password='testpass123'
        )
        
        # Create another user (for permission tests)
        self.other_user = User.objects.create_user(
            email='other@example.com',
            name='Other User',
            password='testpass123'
        )
        
        # Get token and authenticate
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # URLs
        self.tasks_url = reverse('task-list')
        
        # Create a task for tests
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            user=self.user,
            due_date=timezone.now() + timedelta(days=1)
        )
        self.task_detail_url = reverse('task-detail', args=[self.task.id])
    
    def test_create_task(self):
        """Test creating a new task"""
        future_date = timezone.now() + timedelta(days=7)
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'priority': 'high',
            'status': 'pending',
            'due_date': future_date.isoformat()
        }
        response = self.client.post(self.tasks_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        self.assertEqual(response.data['user_email'], self.user.email)
        self.assertEqual(Task.objects.count(), 2)
    
    def test_create_task_past_due_date(self):
        """Test creating task with past due date (should fail)"""
        past_date = timezone.now() - timedelta(days=1)
        data = {
            'title': 'Invalid Task',
            'due_date': past_date.isoformat()
        }
        response = self.client.post(self.tasks_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('due_date', response.data)
    
    def test_list_tasks(self):
        """Test listing tasks"""
        # Create additional task
        Task.objects.create(
            title='Another Task',
            user=self.user,
            due_date=timezone.now() + timedelta(days=2)
        )
        
        response = self.client.get(self.tasks_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 2)  # Should return both tasks
    
    def test_list_tasks_only_owns(self):
        """Test that users only see their own tasks"""
        # Create task for other user
        Task.objects.create(
            title="Other User's Task",
            user=self.other_user,
            due_date=timezone.now() + timedelta(days=2)
        )
        
        response = self.client.get(self.tasks_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 1)  # Only user's task
        self.assertEqual(data[0]['title'], 'Test Task')
    
    def test_get_single_task(self):
        """Test getting a single task"""
        response = self.client.get(self.task_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')
    
    def test_get_other_users_task(self):
        """Test trying to get another user's task (should fail)"""
        # Create task for other user
        other_task = Task.objects.create(
            title="Other's Task",
            user=self.other_user,
            due_date=timezone.now() + timedelta(days=2)
        )
        
        url = reverse('task-detail', args=[other_task.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_task(self):
        """Test updating a task"""
        data = {
            'title': 'Updated Title',
            'status': 'in_progress'
        }
        response = self.client.patch(self.task_detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.assertEqual(response.data['status'], 'in_progress')
    
    def test_delete_task(self):
        """Test deleting a task"""
        response = self.client.delete(self.task_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
    
    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status"""
        # Create completed task
        Task.objects.create(
            title='Completed Task',
            user=self.user,
            status='completed',
            due_date=timezone.now() + timedelta(days=1)
        )
        
        response = self.client.get(self.tasks_url, {'status': 'completed'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Completed Task')