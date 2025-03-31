from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from authentication.serializers import (
    UserCreateSerializer,
    UserListSerializer,
    UserDetailSerializer,
)
from authentication.models import User
from rest_framework.permissions import BasePermission


class IsAuthenticatedForActionsExceptCreate(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user.is_authenticated


class UserViewset(ModelViewSet):

    permission_classes = [IsAuthenticatedForActionsExceptCreate]

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'list':
            return UserListSerializer
        else:
            return UserDetailSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    def check_permission(self, product, user):
        if product != user:
            return Response({'detail': 'Vous ne pouvez modifier que votre profil'}, status=status.HTTP_401_UNAUTHORIZED)
        return None

    def update(self, request, pk=None):
        product = self.get_object()
        permission_error = self.check_permission(product, request.user)
        if permission_error:
            return permission_error
        serializer = self.get_serializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        product = self.get_object()
        permission_error = self.check_permission(product, request.user)
        if permission_error:
            return permission_error
        serializer = self.get_serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        product = self.get_object()
        permission_error = self.check_permission(product, request.user)
        if permission_error:
            return permission_error
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
