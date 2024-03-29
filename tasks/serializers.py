from rest_framework import serializers

from notifications.models import new_notification
from users.models import User
from users.serializers import UserContactsSerializer
from .models import Task, Application, TaskTag, TaskSubject, Review, TaskFile


class TaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'file',)
        model = TaskFile


# informational serializersа
class TagInfoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name',)
        model = TaskTag


class SubjectInfoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name',)
        model = TaskSubject


# display/edit serializers
class TaskSerializer(serializers.ModelSerializer):
    applications_amount = serializers.SerializerMethodField(read_only=True)
    author = serializers.CharField(source='author.username', read_only=True)
    author_rating_normalized = serializers.FloatField(source='author.author_rating_normalized', read_only=True)

    class Meta:
        fields = ('id',
                  'title',
                  'price',
                  'author',
                  'author_rating_normalized',
                  'implementer',
                  'applications_amount',
                  'stage_of_study',
                  'course_of_study',
                  'tags',
                  'subject',
                  'description',
                  'status',
                  'created_at',
                  'updated_at',
                  'stop_accepting_applications_at',
                  'expires_at')
        model = Task

    def get_applications_amount(self, task):
        return task.applications.all().count()


class TaskDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    author_rating_normalized = serializers.FloatField(source='author.author_rating_normalized', read_only=True)
    implementer = serializers.CharField(source='implementer.username', read_only=True)
    applicants = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField()

    contacts = serializers.SerializerMethodField(read_only=True)
    files = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(read_only=True)
    reviews = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id',
                  'author',
                  'author_rating_normalized',
                  'implementer',
                  'applicants',
                  'title',
                  'price',
                  'stage_of_study',
                  'course_of_study',
                  'tags',
                  'subject',
                  'description',
                  'files',
                  'stop_accepting_applications_at',
                  'status',
                  'contacts',
                  'reviews',
                  'created_at',
                  'updated_at',
                  'expires_at',)
        model = Task

    def get_files(self, task):
        return [TaskFileSerializer(file).data for file in task.files.all()]

    def get_applicants(self, task):
        applications = task.applications.all().order_by('-applicant__implementer_rating_normalized')
        applicants = [application.applicant.username for application in applications]
        return applicants

    def get_contacts(self, task):
        user = self.context['request'].user
        if task.implementer is None:
            return None
        elif user == task.implementer:
            return {'author': UserContactsSerializer(task.author).data}
        elif user == task.author:
            return {'implementer': UserContactsSerializer(task.implementer).data}
        else:
            return None

    def get_reviews(self, task):
        reviews = Review.objects.filter(task=task)
        return [ReviewSerializer(review).data for review in reviews]


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.CharField(source='applicant.username', read_only=True)
    implementer_rating_normalized = serializers.FloatField(source='applicant.implementer_rating_normalized',
                                                           read_only=True)
    task = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)

    class Meta:
        fields = ('id',
                  'applicant',
                  'implementer_rating_normalized',
                  'task',
                  'status',
                  'message',
                  'created_at',
                  'updated_at',)
        model = Application

    def get_task(self, application):
        return TaskSerializer(application.task).data


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.CharField(read_only=True)
    task = serializers.CharField(source='task.id', read_only=True)
    review_type = serializers.CharField(read_only=True)

    class Meta:
        fields = ('reviewer',
                  'task',
                  'review_type',
                  'message',
                  'rating',
                  'created_at',
                  'updated_at')
        model = Review


# task interact serializers
class TaskApplySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('message',)
        model = Application


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('title',
                  'price',
                  'stage_of_study',
                  'course_of_study',
                  'tags',
                  'subject',
                  'description',
                  'stop_accepting_applications_at')
        model = Task


class SetTaskImplementerSerializer(serializers.ModelSerializer):
    task = serializers.SerializerMethodField(read_only=True)
    applications = serializers.SerializerMethodField(read_only=True)
    implementer = serializers.SerializerMethodField(method_name='set_implementer')

    class Meta:
        fields = ('id',
                  'implementer',
                  'task',
                  'applications',)
        model = Task

    def set_implementer(self, task):
        implementer_username = self.context['request'].data.get('implementer')
        if implementer_username is None or self.context['request'].method != 'PUT':
            if task.implementer is not None:
                return task.implementer.username
            return task.implementer

        # если еще нет implementer; если accepting applications
        if not (task.implementer is None):
            raise serializers.ValidationError(f'This task (id = {task.id}) already have implementer')
        if not (task.status == 'A'):
            raise serializers.ValidationError(f'This task (id = {task.id}) status is {task.status}. '
                                              f'It is not Acception Applications')
        if not (implementer_username in [application.applicant.username for application in task.applications.all()]):
            raise serializers.ValidationError(
                f'This user (id={implementer_username}) haven\'t send application for this task (id={task.id})')

        # если юзер у задания еще не задан,
        # если задание принимает заявки,
        # если юзер подавал заявку на исполнение, то
        # иными словами "если все норм"
        task.status = 'P'  # задание переходит в режим IN PROGRESS
        task.implementer = User.objects.get(username=implementer_username)  # задать юзера как исполнителя
        task.save()

        # если ошибок не вылезло, то отправить уведомление создателю задачи
        new_notification(user=task.author,
                         type='set_task_implementer_notification',
                         affected_object_id=task.id,
                         message=f"Вы успешно назначили исполнителя на задание",
                         checked=0)
        # и новому исполнителю тоже уведомление
        new_notification(user=task.implementer,
                         type='application_accepted_notification',
                         affected_object_id=task.id,
                         message=f"Вас назначили исполнителем на задание",
                         checked=0)

        applications = task.applications.all()
        for application in applications:
            if application.applicant.username == implementer_username:
                application.status = 'A'  # статус ACCEPTED
            else:
                application.status = 'R'  # статус REJECTED
                # и всем, чья заявка отклонена тоже уведомления
                new_notification(user=application.applicant,
                                 type='application_rejected_notification',
                                 affected_object_id=task.id,
                                 message=f"Ваша заявка на задание отклонена",
                                 checked=0)
            application.save()

        return implementer_username

    def get_applications(self, task):
        applications = task.applications.all().order_by('-applicant__implementer_rating_normalized')
        applications_info = [ApplicationSerializer(application).data for application in applications]
        return applications_info

    def get_task(self, task):
        return TaskDetailSerializer(task, context=self.context).data


class CloseTaskSerializer(serializers.ModelSerializer):
    confirm = serializers.CharField(max_length=300, write_only=True)

    class Meta:
        fields = ('confirm',)
        model = Task

    def update(self, task, validated_data):
        if task.status == 'C':
            raise serializers.ValidationError(f'Задача уже была закрыта ранее')
        elif not task.implementer:
            raise serializers.ValidationError(f'Нельзя закрыть задачу без исполнителя, вы можете удалить ее')
        elif validated_data['confirm'] == 'Я подтверждаю, что хочу закрыть задачу':
            task.status = 'C'
            task.save()
            return task
        else:
            raise serializers.ValidationError(f'Задача не была закрыта')


class AddFileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('file',)
        model = TaskFile

    def create(self, validated_data):
        task_id = self.context['request'].parser_context['kwargs'].get('pk', None)
        task = Task.objects.get(id=task_id)
        validated_data['task'] = task
        return super().create(validated_data)
