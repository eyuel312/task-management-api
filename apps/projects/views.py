from rest_framework import generics, permissions
from .models import Project
from .serializers import ProjectSerializer, ProjectDetailSerializer
from apps.accounts.permissions import IsOwner

class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectDetailSerializer
        return ProjectSerializer
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)