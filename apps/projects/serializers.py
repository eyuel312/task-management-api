from rest_framework import serializers
from .models import Project
from apps.tasks.serializers import TaskSerializer

class ProjectSerializer(serializers.ModelSerializer):
    task_count = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'task_count', 'completed_tasks')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ProjectDetailSerializer(ProjectSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta(ProjectSerializer.Meta):
        # `ProjectSerializer.Meta.fields` may be a string ('__all__') or an
        # iterable. Can't concatenate a list to a string so handle both cases.
        base = ProjectSerializer.Meta.fields
        if isinstance(base, str):
            fields = base
        else:
            fields = list(base) + ['tasks']