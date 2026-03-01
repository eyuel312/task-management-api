from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.urls import reverse

class APIRootView(APIView):
    """
    API root view showing all available endpoints
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        return Response({
            'message': 'Welcome to Task Management API',
            'version': '1.0',
            'endpoints': {
                'auth': {
                    'register': '/api/auth/register/',
                    'login': '/api/auth/login/',
                    'logout': '/api/auth/logout/',
                    'profile': '/api/auth/me/',
                },
                'tasks': {
                    'list': '/api/tasks/',
                    'create': '/api/tasks/',
                    'detail': '/api/tasks/{id}/',
                    'update': '/api/tasks/{id}/',
                    'delete': '/api/tasks/{id}/',
                },
                'projects': {
                    'list': '/api/projects/',
                    'create': '/api/projects/',
                    'detail': '/api/projects/{id}/',
                    'update': '/api/projects/{id}/',
                    'delete': '/api/projects/{id}/',
                },
                'docs': {
                    'swagger': '/swagger/',
                    'redoc': '/redoc/',
                }
            },
            'usage': 'Use the appropriate endpoints with authentication token',
            'note': 'Most endpoints require authentication. Include "Authorization: Token <your-token>" header'
        })