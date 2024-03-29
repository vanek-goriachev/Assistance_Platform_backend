"""assistance_platform_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.conf import settings
from django.conf.urls.static import static

from tasks.views import informational_endpoint_view

urlpatterns = [
    path('admin/', admin.site.urls),  # админка джанго
    # users app
    path('api/v1/users/', include('users.urls')),  # ссылка на другой файл urls.py
    # tasks app
    path('api/v1/tasks/', include('tasks.urls')),  # ссылка на другой файл urls.py
    # notifications app
    path('api/v1/notifications/', include('notifications.urls')),  # ссылка на другой файл urls.py

    # auth
    path('api/v1/api-auth', include('rest_framework.urls')),  # сюда тебе не надо, это для веб версии апи
    path('api/v1/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # получение токенов
    path('api/v1/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),  # обновление токенов по рефрешу
    path('api/v1/token/verify', TokenVerifyView.as_view(), name='token_verify'),  # верификация токена
    path('api/v1/informational_endpoint', informational_endpoint_view, name='informational_endpoint'),
    # информационный эндпоинт
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
