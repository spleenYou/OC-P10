from rest_framework.viewsets import ModelViewSet
from authentication.serializers import (
    UserCreateSerializer,
    UserSerializer,
)
from authentication.models import User
from rest_framework.permissions import BasePermission


class IsAuthenticatedForActionsExceptCreate(BasePermission):

    def has_permission(self, request, view):
        # Anyone can create an user but not other actions
        if request.method == 'POST':
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        'Check if the user is the request user except for retrieve action'
        if view.action != 'retrieve':
            return obj == request.user
        return True


class UserViewset(ModelViewSet):

    permission_classes = [IsAuthenticatedForActionsExceptCreate]

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        else:
            return UserSerializer
