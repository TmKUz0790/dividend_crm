from rest_framework import serializers
from .models_kanban import Stage, Client, KanbanTask

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'name', 'order']

class ClientSerializer(serializers.ModelSerializer):
    stage = StageSerializer(read_only=True)
    stage_id = serializers.PrimaryKeyRelatedField(queryset=Stage.objects.all(), source='stage', write_only=True)
    class Meta:
        model = Client
        fields = ['id', 'name', 'stage', 'stage_id']

class KanbanTaskSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), source='client', write_only=True)
    class Meta:
        model = KanbanTask
        fields = ['id', 'title', 'description', 'status', 'client', 'client_id', 'created_at']
