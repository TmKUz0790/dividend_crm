from rest_framework import serializers
from .model_sales_funnel import (
    Varonka, VaronkaStage, VaronkaTask, Application,
    ApplicationTaskCompletion, VaronkaTemplate,
    VaronkaTemplateStage, VaronkaTemplateTask
)


class VaronkaStageSerializer(serializers.ModelSerializer):
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = VaronkaStage
        fields = [
            'id', 'varonka', 'name', 'slug', 'order',
            'is_initial', 'is_final', 'color', 'applications_count'
        ]
        read_only_fields = ['id']

    def get_applications_count(self, obj):
        return obj.application_set.count()


class VaronkaTaskSerializer(serializers.ModelSerializer):
    required_for_stage_name = serializers.CharField(
        source='required_for_stage.name', read_only=True
    )

    class Meta:
        model = VaronkaTask
        fields = [
            'id', 'varonka', 'name', 'order', 'description',
            'is_required', 'required_for_stage', 'required_for_stage_name'
        ]
        read_only_fields = ['id']


class VaronkaSerializer(serializers.ModelSerializer):
    stages = VaronkaStageSerializer(many=True, read_only=True)
    tasks = VaronkaTaskSerializer(many=True, read_only=True)
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Varonka
        fields = [
            'id', 'name', 'description', 'created_at', 'updated_at',
            'stages', 'tasks', 'applications_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_applications_count(self, obj):
        return obj.application_set.count()


class VaronkaListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing varonkas"""
    applications_count = serializers.SerializerMethodField()
    stages_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Varonka
        fields = [
            'id', 'name', 'description', 'created_at',
            'applications_count', 'stages_count', 'tasks_count'
        ]
        read_only_fields = ['id', 'created_at']

    def get_applications_count(self, obj):
        return obj.application_set.count()

    def get_stages_count(self, obj):
        return obj.stages.count()

    def get_tasks_count(self, obj):
        return obj.tasks.count()


class ApplicationTaskCompletionSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='varonka_task.name', read_only=True)

    class Meta:
        model = ApplicationTaskCompletion
        fields = [
            'id', 'application', 'varonka_task', 'task_name',
            'completed_at', 'notes', 'completed_by'
        ]
        read_only_fields = ['id', 'completed_at']


class ApplicationSerializer(serializers.ModelSerializer):
    current_stage_name = serializers.CharField(source='current_stage.name', read_only=True)
    current_stage_color = serializers.CharField(source='current_stage.color', read_only=True)
    varonka_name = serializers.CharField(source='varonka.name', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_done = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()  # Backward compatibility
    task_completions = ApplicationTaskCompletionSerializer(many=True, read_only=True)
    next_task = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'name', 'contact', 'varonka', 'varonka_name',
            'current_stage', 'current_stage_name', 'current_stage_color',
            'current_task', 'status', 'is_done', 'progress_percentage',
            'created_at', 'updated_at', 'task_completions', 'next_task'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_next_task(self, obj):
        next_task = obj.get_next_task()
        if next_task:
            return VaronkaTaskSerializer(next_task).data
        return None

    def validate(self, data):
        # Ensure current_stage belongs to the same varonka
        if 'current_stage' in data and 'varonka' in data:
            if data['current_stage'].varonka != data['varonka']:
                raise serializers.ValidationError(
                    "Current stage must belong to the selected varonka"
                )
        return data


class ApplicationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing applications"""
    current_stage_name = serializers.CharField(source='current_stage.name', read_only=True)
    current_stage_color = serializers.CharField(source='current_stage.color', read_only=True)
    varonka_name = serializers.CharField(source='varonka.name', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_done = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()  # Backward compatibility

    class Meta:
        model = Application
        fields = [
            'id', 'name', 'contact', 'varonka', 'varonka_name',
            'current_stage', 'current_stage_name', 'current_stage_color',
            'status', 'is_done', 'progress_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VaronkaBoardSerializer(serializers.ModelSerializer):
    """Serializer for Kanban board view"""
    stages = serializers.SerializerMethodField()

    class Meta:
        model = Varonka
        fields = ['id', 'name', 'description', 'stages']

    def get_stages(self, obj):
        stages_data = []
        for stage in obj.stages.all().order_by('order'):
            applications = Application.objects.filter(
                varonka=obj,
                current_stage=stage
            ).order_by('-created_at')

            stage_data = {
                'id': stage.id,
                'name': stage.name,
                'slug': stage.slug,
                'color': stage.color,
                'order': stage.order,
                'is_final': stage.is_final,
                'applications': ApplicationListSerializer(applications, many=True).data
            }
            stages_data.append(stage_data)
        return stages_data


# Template Serializers
class VaronkaTemplateStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaronkaTemplateStage
        fields = [
            'id', 'template', 'name', 'slug', 'order',
            'is_initial', 'is_final', 'color'
        ]
        read_only_fields = ['id']


class VaronkaTemplateTaskSerializer(serializers.ModelSerializer):
    required_for_stage_name = serializers.CharField(
        source='required_for_stage.name', read_only=True
    )

    class Meta:
        model = VaronkaTemplateTask
        fields = [
            'id', 'template', 'name', 'order', 'description',
            'is_required', 'required_for_stage', 'required_for_stage_name'
        ]
        read_only_fields = ['id']


class VaronkaTemplateSerializer(serializers.ModelSerializer):
    template_stages = VaronkaTemplateStageSerializer(many=True, read_only=True)
    template_tasks = VaronkaTemplateTaskSerializer(many=True, read_only=True)

    class Meta:
        model = VaronkaTemplate
        fields = [
            'id', 'name', 'description', 'created_at',
            'template_stages', 'template_tasks'
        ]
        read_only_fields = ['id', 'created_at']


class VaronkaTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing templates"""
    stages_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = VaronkaTemplate
        fields = ['id', 'name', 'description', 'created_at', 'stages_count', 'tasks_count']
        read_only_fields = ['id', 'created_at']

    def get_stages_count(self, obj):
        return obj.template_stages.count()

    def get_tasks_count(self, obj):
        return obj.template_tasks.count()