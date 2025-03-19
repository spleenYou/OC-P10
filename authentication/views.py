from rest_framework.viewsets import ModelViewSet
from authentication.serializers import UserSerializer, UserListSerializer
from authentication.models import User


class UserViewset(ModelViewSet):

    create_serializer_class = UserSerializer
    list_serializer_class = UserListSerializer

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        if self.action == 'create':
            return self.create_serializer_class
