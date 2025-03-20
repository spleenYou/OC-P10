from rest_framework.viewsets import ModelViewSet
from authentication.serializers import UserSerializer, UserListSerializer, UserDetailsSerializer
from authentication.models import User


class UserViewset(ModelViewSet):

    create_serializer_class = UserSerializer
    list_serializer_class = UserListSerializer
    details_serializer_class = UserDetailsSerializer

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        print(self.action)
        match self.action:
            case 'list':
                return self.list_serializer_class
            case 'create':
                return self.create_serializer_class
            case 'retrieve':
                return self.details_serializer_class
            case _:
                return None
