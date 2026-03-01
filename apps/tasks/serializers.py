from rest_framework import serializers
from django.utils import timezone
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    project_name = serializers.ReadOnlyField(source='project.name')
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'completed_at', 'user_email', 'project_name')
    
    def validate(self, data):
        instance = getattr(self, 'instance', None)
        
        # Always allow status updates - users can mark tasks as complete or incomplete
        if 'status' in data:
            # Validate status value
            valid_statuses = [choice[0] for choice in self.Meta.model.STATUS_CHOICES]
            if data['status'] not in valid_statuses:
                raise serializers.ValidationError(
                    f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )
        
        # Check if task is completed and trying to edit other fields (not status)
        if instance and instance.status == 'completed':
            # Allow status changes
            if 'status' in data and data['status'] != 'completed':
                # This is fine - allow changing from completed to incomplete/in_progress/pending
                pass
            elif any(field in data for field in ['title', 'description', 'priority', 'due_date']):
                # Trying to edit other fields while completed
                raise serializers.ValidationError(
                    "Completed tasks cannot be edited. Change status first to edit other fields."
                )
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)