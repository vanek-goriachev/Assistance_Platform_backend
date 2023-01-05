from django.contrib.auth.forms import UserCreationForm as DefaultUserCreationForm
from django.contrib.auth.forms import UserChangeForm as DefaultUserChangeForm
from .models import User


class UserCreationForm(DefaultUserCreationForm):
    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'profile_image',
                  'biography',
                  'stage_of_study',
                  'course_of_study',
                  'contact_phone',
                  'contact_email',
                  'contact_tg',
                  'contact_vk',)


class UserChangeForm(DefaultUserChangeForm):
    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'profile_image',
                  'biography',
                  'stage_of_study',
                  'course_of_study',
                  'contact_phone',
                  'contact_email',
                  'contact_tg',
                  'contact_vk',)

