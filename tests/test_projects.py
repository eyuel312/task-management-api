from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()

class ProjectTests(TestCase):
    """Test cases for projects app"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create user
        self.user = User.objects.create_user(
            email='projectuser@example.com',
            name='Project User',
            password='testpass123'
        )
        
        # Create another user
        self.other_user = User.objects.create_user(
            email='otherproject@example.com',
            name='Other Project User',
            password='testpass123'
        )
        
        # Authenticate
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # URLs
        self.projects_url = reverse('project-list')
        
        # Create a project
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            user=self.user
        )
        self.project_detail_url = reverse('project-detail', args=[self.project.id])
    
    def test_create_project(self):
        """Test creating a new project"""
        data = {
            'name': 'New Project',
            'description': 'New Project Description'
        }
        response = self.client.post(self.projects_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Project')
        self.assertEqual(Project.objects.count(), 2)
    
    def test_list_projects(self):
        """Test listing projects"""
        # Create additional project
        Project.objects.create(
            name='Another Project',
            user=self.user
        )
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 2)
    
    def test_list_projects_only_owns(self):
        """Test that users only see their own projects"""
        # Create project for other user
        Project.objects.create(
            name="Other User's Project",
            user=self.other_user
        )
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 1)  # Only user's project
        self.assertEqual(data[0]['name'], 'Test Project')
    
    def test_project_detail_with_tasks(self):
        """Test getting project details with associated tasks"""
        # Create tasks for this project
        future_date = timezone.now() + timedelta(days=1)
        task1 = Task.objects.create(
            title='Task 1',
            user=self.user,
            project=self.project,
            due_date=future_date
        )
        task2 = Task.objects.create(
            title='Task 2',
            user=self.user,
            project=self.project,
            status='completed',
            due_date=future_date
        )
        
        response = self.client.get(self.project_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Project')
        self.assertEqual(response.data['task_count'], 2)
        self.assertEqual(response.data['completed_tasks'], 1)
        self.assertEqual(len(response.data['tasks']), 2)
    
    def test_update_project(self):
        """Test updating a project"""
        data = {'name': 'Updated Project Name'}
        response = self.client.patch(self.project_detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Project Name')
    
    def test_delete_project(self):
        """Test deleting a project"""
        response = self.client.delete(self.project_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)
    
    def test_cannot_access_other_users_project(self):
        """Test trying to access another user's project"""
        other_project = Project.objects.create(
            name="Other's Project",
            user=self.other_user
        )
        
        url = reverse('project-detail', args=[other_project.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)