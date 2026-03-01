from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.accounts.authentication import StrictTokenAuthentication
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwner

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [StrictTokenAuthentication]  # Force strict token authentication only
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at', 'priority']
    
    @swagger_auto_schema(
        operation_description="List all tasks for the authenticated user or create a new task",
        security=[{'Token': []}],
        responses={
            200: TaskSerializer(many=True),
            201: TaskSerializer,
            401: 'Unauthorized - Invalid or missing token'
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new task",
        security=[{'Token': []}],
        request_body=TaskSerializer,
        responses={
            201: TaskSerializer,
            400: 'Bad request - Invalid data',
            401: 'Unauthorized - Invalid or missing token'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        # Only return tasks belonging to the current user
        return Task.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]  # Add IsOwner permission
    authentication_classes = [StrictTokenAuthentication]  # Force strict token authentication only
    
    @swagger_auto_schema(
        operation_description="Get task details",
        security=[{'Token': []}],
        responses={
            200: TaskSerializer,
            404: 'Task not found',
            401: 'Unauthorized - Invalid or missing token'
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update task (PATCH allows partial updates, PUT requires all fields). Status can be updated to 'pending', 'in_progress', or 'completed'.",
        security=[{'Token': []}],
        request_body=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: 'Bad request - Invalid data or cannot edit completed task',
            404: 'Task not found',
            401: 'Unauthorized - Invalid or missing token'
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update task (requires all fields). Status can be updated to 'pending', 'in_progress', or 'completed'.",
        security=[{'Token': []}],
        request_body=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: 'Bad request - Invalid data or cannot edit completed task',
            404: 'Task not found',
            401: 'Unauthorized - Invalid or missing token'
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a task",
        security=[{'Token': []}],
        responses={
            204: 'Task deleted successfully',
            404: 'Task not found',
            401: 'Unauthorized - Invalid or missing token'
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_queryset(self):
        # Only return tasks belonging to the current user
        return Task.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        task = self.get_object()
        
        # Allow status updates regardless of current status
        # Users can mark tasks as complete or incomplete
        if 'status' in request.data:
            new_status = request.data['status']
            # Validate status value
            valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return Response(
                    {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check if task is completed and trying to edit other fields (not status)
        if task.status == 'completed':
            # Allow status change to incomplete or other statuses
            if 'status' in request.data and request.data['status'] != 'completed':
                # This is fine - allow changing from completed to incomplete/in_progress/pending
                pass
            elif len([k for k in request.data.keys() if k != 'status']) > 0:
                # Trying to edit other fields while completed
                return Response(
                    {"error": "Completed tasks cannot be edited. Change status first to edit other fields."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().update(request, *args, **kwargs)

# New endpoint for toggling task completion
class TaskCompleteToggleView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    authentication_classes = [StrictTokenAuthentication]  # Force strict token authentication only
    
    @swagger_auto_schema(
        operation_description="Toggle task completion status (complete <-> incomplete)",
        security=[{'Token': []}],
        responses={
            200: openapi.Response(
                description="Task status toggled",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'task': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            404: 'Task not found',
            401: 'Unauthorized - Invalid or missing token'
        }
    )
    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, user=request.user)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Toggle status
        if task.status == 'completed':
            task.status = 'pending'
            task.completed_at = None
            message = "Task marked as incomplete"
        else:
            task.status = 'completed'
            task.completed_at = timezone.now()
            message = "Task marked as complete"
        
        task.save()
        
        serializer = TaskSerializer(task, context={'request': request})
        return Response({
            "message": message,
            "task": serializer.data
        })