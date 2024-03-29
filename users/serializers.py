from rest_framework import serializers

from tasks.models import Task, Application
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name',
            'last_name',
            'biography',
            'profile_image',
            'stage_of_study',
            'course_of_study',
        )
        model = User


class UserContactsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name',
            'email',
            'phone',
            'telegram',
            'vk',
        )
        model = User


class UserStatisticsSerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField(read_only=True)
    tasks = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('ratings', 'tasks')
        model = User

    def get_ratings(self, user):
        return {'author': {'sum': user.author_rating, 'amount': user.author_review_counter,
                           'normalized': user.author_rating_normalized},
                'implementer': {'sum': user.implementer_rating, 'amount': user.implementer_review_counter,
                                'normalized': user.implementer_rating_normalized}}

    def get_tasks(self, user):
        authored_tasks = Task.objects.filter(author=user)
        implementered_tasks = Task.objects.filter(implementer=user)
        applications = Application.objects.filter(applicant=user)

        return {'authored': {'active': authored_tasks.filter(status__in=['A', 'P']).count(),
                             'total': authored_tasks.count()},
                'implementered': {'active': implementered_tasks.filter(status='P').count(),
                                  'total': implementered_tasks.count()},
                'applications': {'active': applications.filter(status='S').count(),
                                 'total': applications.count()}}


class UserSerializer(serializers.ModelSerializer):
    statistics = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'statistics')
        model = User

    def get_statistics(self, user):
        return UserStatisticsSerializer(user).data


class UserDetailSerializer(serializers.ModelSerializer):
    statistics = serializers.SerializerMethodField(read_only=True)
    contacts = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id',
                  'username',
                  'profile',
                  'contacts',
                  'statistics')
        model = User

    def get_statistics(self, user):
        return UserStatisticsSerializer(user).data

    def get_contacts(self, user):
        if user.show_contacts or self.context['request'].user == user:
            # контакты возвращаются только если юзер пытается просмотреть сам себя
            return UserContactsSerializer(user).data
        else:
            # TODO это захардкожено и это плохо
            return {"first_name": "",
                    "email": "скрыто",
                    "phone": "скрыто",
                    "telegram": "скрыто",
                    "vk": "скрыто"
                    }

    def get_profile(self, user):
        return UserProfileSerializer(user).data


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('show_contacts',
                  'send_email_notifications',)
        model = User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=128, write_only=True)

    class Meta:
        fields = ('username',
                  'password',
                  'email',)
        model = User

    def create(self, validated_data):
        # TODO добавить подтверждение по email
        return User.objects.create_user(**validated_data)
