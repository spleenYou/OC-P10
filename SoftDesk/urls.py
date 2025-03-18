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
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import ProjectViewset


router = routers.SimpleRouter()
router.register('project', ProjectViewset, basename='project')
# router.register('product', ProductViewset, basename='product')
# router.register('article', ArticleViewset, basename='article')
# router.register('admin/category', AdminCategoryViewset, basename='admin-category')
# router.register('admin/article', AdminArticleViewset, basename='admin-article')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls')),
    # path('api/token/', TokenObtainPairView.as_view(), name='tokain_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='tokain_refresh'),
    path('api/', include(router.urls)),
]
