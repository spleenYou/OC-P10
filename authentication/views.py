from rest_framework.viewsets import ModelViewSet
from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer
)
from authentication.models import User
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .permissions import IsAuthenticatedForActionsExceptCreate


class UserViewset(ModelViewSet):

    permission_classes = [IsAuthenticatedForActionsExceptCreate]

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        else:
            return UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
