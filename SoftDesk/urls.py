"""
URL configuration for SoftDesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import ProjectViewset, ContributorViewset, IssueViewset, CommentViewset
from authentication.views import UserViewset


router_project = routers.SimpleRouter()
router_project.register(r'project', ProjectViewset, basename='project')
router_project.register(r'contributor', ContributorViewset, basename='contributor')
router_project.register(r'issue', IssueViewset, basename='issue')
router_project.register(r'comment', CommentViewset, basename='comment')
router_auth = routers.SimpleRouter()
router_auth.register('user', UserViewset, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/login/', TokenObtainPairView.as_view(), name='tokain_obtain_pair'),
    path('user/login/refresh/', TokenRefreshView.as_view(), name='tokain_refresh'),
    path('api/', include(router_project.urls)),
    path('', include(router_auth.urls)),
]
