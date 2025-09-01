#
# # from django.db import models
#
#
#
# from django.db import models
#
# class Varonka(models.Model):
# 	name = models.CharField(max_length=100)
# 	description = models.TextField(blank=True)
# 	created_at = models.DateTimeField(auto_now_add=True)
#
# 	def __str__(self):
# 		return self.name
#
# class VaronkaTask(models.Model):
# 	varonka = models.ForeignKey(Varonka, related_name='tasks', on_delete=models.CASCADE)
# 	name = models.CharField(max_length=100)
# 	order = models.PositiveIntegerField(default=0)
# 	description = models.TextField(blank=True, help_text="Detailed description of what this task involves")
# 	is_required = models.BooleanField(default=True, help_text="Is this task mandatory?")
#
# 	class Meta:
# 		ordering = ['order']
# 		unique_together = ['varonka', 'order']  # Ensure unique ordering within each varonka
#
# 	def __str__(self):
# 		return f"{self.varonka.name} - {self.name}"
#
# class Application(models.Model):
# 	STAGE_CHOICES = [
# 		("new", "Новая"),
# 		("in_progress", "В работе"),
# 		("done", "Завершена"),
# 	]
#
# 	name = models.CharField(max_length=100)
# 	contact = models.CharField(max_length=100, blank=True)
# 	status = models.CharField(max_length=32, choices=STAGE_CHOICES, default="new", verbose_name='Статус')
# 	is_done = models.BooleanField(default=False)
#
# 	varonka = models.ForeignKey(Varonka, on_delete=models.CASCADE, null=True, blank=True)
# 	current_task = models.ForeignKey(VaronkaTask, on_delete=models.SET_NULL, null=True, blank=True)
#
# 	created_at = models.DateTimeField(auto_now_add=True)
# 	updated_at = models.DateTimeField(auto_now=True)
#
# 	def __str__(self):
# 		return self.name
#
# 	def get_next_task(self):
# 		"""Get the next task in the varonka sequence"""
# 		if not self.varonka:
# 			return None
#
# 		completed_tasks = self.task_completions.values_list('task_id', flat=True)
# 		next_task = self.varonka.tasks.exclude(id__in=completed_tasks).order_by('order').first()
# 		return next_task
#
# 	def progress_percentage(self):
# 		"""Calculate completion percentage based on completed tasks"""
# 		if not self.varonka:
# 			return 0
#
# 		total_tasks = self.varonka.tasks.count()
# 		if total_tasks == 0:
# 			return 0
#
# 		completed_tasks = self.task_completions.count()
# 		return int((completed_tasks / total_tasks) * 100)
#
# class ApplicationTaskCompletion(models.Model):
# 	application = models.ForeignKey(Application, related_name='task_completions', on_delete=models.CASCADE)
# 	task = models.ForeignKey(VaronkaTask, on_delete=models.CASCADE)
# 	completed_at = models.DateTimeField(auto_now_add=True)
# 	notes = models.TextField(blank=True, help_text="Notes about task completion")
# 	completed_by = models.CharField(max_length=100, blank=True)  # Could be ForeignKey to User model
#
# 	class Meta:
# 		unique_together = ['application', 'task']  # Prevent duplicate completions
#
# 	def __str__(self):
# 		return f"{self.application.name} - {self.task.name} (Completed)"
#
# class VaronkaTemplate(models.Model):
# 	name = models.CharField(max_length=100)
# 	description = models.TextField(blank=True)
#
# 	def __str__(self):
# 		return f"Template: {self.name}"
#
# 	def create_varonka(self, varonka_name):
# 		"""Create a new varonka from this template"""
# 		varonka = Varonka.objects.create(
# 			name=varonka_name,
# 			description=self.description
# 		)
#
# 		# Copy tasks from template
# 		for template_task in self.template_tasks.all():
# 			VaronkaTask.objects.create(
# 				varonka=varonka,
# 				name=template_task.name,
# 				order=template_task.order,
# 				description=template_task.description,
# 				is_required=template_task.is_required
# 			)
#
# 		return varonka
#
# class VaronkaTemplateTask(models.Model):
# 	template = models.ForeignKey(VaronkaTemplate, related_name='template_tasks', on_delete=models.CASCADE)
# 	name = models.CharField(max_length=100)
# 	order = models.PositiveIntegerField(default=0)
# 	description = models.TextField(blank=True)
# 	is_required = models.BooleanField(default=True)
#
# 	class Meta:
# 		ordering = ['order']
#
# 	def __str__(self):
# 		return f"{self.template.name} - {self.name}"


from django.db import models
from django.utils import timezone


class Varonka(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	def get_initial_stage(self):
		"""Get the first stage for this varonka"""
		return self.stages.order_by('order').first()


class VaronkaStage(models.Model):
	"""Configurable stages for each Varonka"""
	varonka = models.ForeignKey(Varonka, related_name='stages', on_delete=models.CASCADE)
	name = models.CharField(max_length=100)  # e.g., "Новая", "В работе", "Завершена"
	slug = models.CharField(max_length=50)  # e.g., "new", "in_progress", "done"
	order = models.PositiveIntegerField(default=0)
	is_initial = models.BooleanField(default=False, help_text="Is this the initial stage for new applications?")
	is_final = models.BooleanField(default=False, help_text="Is this a final/completion stage?")
	color = models.CharField(max_length=7, default='#6B7280', help_text="Hex color code for UI")

	class Meta:
		ordering = ['varonka', 'order']
		unique_together = [
			['varonka', 'order'],
			['varonka', 'slug']
		]

	def __str__(self):
		return f"{self.varonka.name} - {self.name}"


class VaronkaTask(models.Model):
	varonka = models.ForeignKey(Varonka, related_name='tasks', on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	order = models.PositiveIntegerField(default=0)
	description = models.TextField(blank=True, help_text="Detailed description of what this task involves")
	is_required = models.BooleanField(default=True, help_text="Is this task mandatory?")
	# Optional: Link tasks to specific stages
	required_for_stage = models.ForeignKey(
		VaronkaStage,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		help_text="Completing this task allows moving to this stage"
	)

	class Meta:
		ordering = ['order']
		unique_together = ['varonka', 'order']

	def __str__(self):
		return f"{self.varonka.name} - {self.name}"


class Application(models.Model):
	name = models.CharField(max_length=100)
	contact = models.CharField(max_length=100, blank=True)

	varonka = models.ForeignKey(Varonka, on_delete=models.CASCADE)
	current_stage = models.ForeignKey(
		VaronkaStage,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		help_text="Current stage of this application"
	)
	current_task = models.ForeignKey(VaronkaTask, on_delete=models.SET_NULL, null=True, blank=True)

	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		# Auto-set initial stage if not provided
		if not self.current_stage_id and self.varonka:
			initial_stage = self.varonka.get_initial_stage()
			if initial_stage:
				self.current_stage = initial_stage
		super().save(*args, **kwargs)

	@property
	def status(self):
		"""Backward compatibility property"""
		return self.current_stage.slug if self.current_stage else 'unknown'

	@property
	def is_done(self):
		"""Check if application is in a final stage"""
		return self.current_stage.is_final if self.current_stage else False

	def get_varonka_tasks(self):
		"""Get all tasks for this application's varonka"""
		return self.varonka.tasks.all().order_by('order')

	def get_next_task(self):
		"""Get the next uncompleted task"""
		if not self.varonka:
			return None

		completed_task_ids = self.task_completions.values_list('varonka_task_id', flat=True)
		next_task = self.varonka.tasks.exclude(id__in=completed_task_ids).order_by('order').first()
		return next_task

	def progress_percentage(self):
		"""Calculate completion percentage based on completed tasks"""
		if not self.varonka:
			return 0

		total_tasks = self.varonka.tasks.count()
		if total_tasks == 0:
			return 100

		completed_tasks = self.task_completions.count()
		return int((completed_tasks / total_tasks) * 100)

	def is_completed(self):
		"""Check if all required tasks are completed"""
		required_tasks = self.varonka.tasks.filter(is_required=True)
		completed_required_tasks = self.task_completions.filter(
			varonka_task__is_required=True
		)
		return required_tasks.count() == completed_required_tasks.count()

	def can_move_to_stage(self, target_stage):
		"""Check if application can move to target stage"""
		if target_stage.varonka != self.varonka:
			return False

		# If stage has required tasks, check if they're completed
		required_tasks = self.varonka.tasks.filter(required_for_stage=target_stage)
		if required_tasks.exists():
			completed_task_ids = self.task_completions.values_list('varonka_task_id', flat=True)
			return all(task.id in completed_task_ids for task in required_tasks)

		return True

	def move_to_stage(self, target_stage):
		"""Move application to a different stage"""
		if self.can_move_to_stage(target_stage):
			self.current_stage = target_stage
			self.save()
			return True
		return False


class ApplicationTaskCompletion(models.Model):
	application = models.ForeignKey(Application, related_name='task_completions', on_delete=models.CASCADE)
	varonka_task = models.ForeignKey(VaronkaTask, on_delete=models.CASCADE)
	completed_at = models.DateTimeField(auto_now_add=True)
	notes = models.TextField(blank=True, help_text="Notes about task completion")
	completed_by = models.CharField(max_length=100, blank=True)

	class Meta:
		unique_together = ['application', 'varonka_task']

	def __str__(self):
		return f"{self.application.name} - {self.varonka_task.name} (Completed)"


class VaronkaTemplate(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"Template: {self.name}"

	def create_varonka(self, varonka_name):
		"""Create a new varonka from this template"""
		varonka = Varonka.objects.create(
			name=varonka_name,
			description=self.description
		)

		# Copy stages from template
		for template_stage in self.template_stages.all():
			VaronkaStage.objects.create(
				varonka=varonka,
				name=template_stage.name,
				slug=template_stage.slug,
				order=template_stage.order,
				is_initial=template_stage.is_initial,
				is_final=template_stage.is_final,
				color=template_stage.color
			)

		# Copy tasks from template
		for template_task in self.template_tasks.all():
			# Find the corresponding stage in the new varonka
			required_for_stage = None
			if template_task.required_for_stage:
				required_for_stage = varonka.stages.get(
					slug=template_task.required_for_stage.slug
				)

			VaronkaTask.objects.create(
				varonka=varonka,
				name=template_task.name,
				order=template_task.order,
				description=template_task.description,
				is_required=template_task.is_required,
				required_for_stage=required_for_stage
			)

		return varonka


class VaronkaTemplateStage(models.Model):
	"""Template stages that can be copied to new varonkas"""
	template = models.ForeignKey(VaronkaTemplate, related_name='template_stages', on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	slug = models.CharField(max_length=50)
	order = models.PositiveIntegerField(default=0)
	is_initial = models.BooleanField(default=False)
	is_final = models.BooleanField(default=False)
	color = models.CharField(max_length=7, default='#6B7280')

	class Meta:
		ordering = ['order']
		unique_together = [
			['template', 'order'],
			['template', 'slug']
		]

	def __str__(self):
		return f"{self.template.name} - {self.name}"


class VaronkaTemplateTask(models.Model):
	template = models.ForeignKey(VaronkaTemplate, related_name='template_tasks', on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	order = models.PositiveIntegerField(default=0)
	description = models.TextField(blank=True)
	is_required = models.BooleanField(default=True)
	required_for_stage = models.ForeignKey(
		VaronkaTemplateStage,
		on_delete=models.CASCADE,
		null=True,
		blank=True
	)

	class Meta:
		ordering = ['order']

	def __str__(self):
		return f"{self.template.name} - {self.name}"
