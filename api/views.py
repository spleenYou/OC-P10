from rest_framework.viewsets import ModelViewSet
from api.models import Project, Contributor, Issue, Comment
from api.serializers import (
    ProjectSerializer,
    ProjectDetailSerializer,
    ContributorSerializer,
    IssueSerializer,
    IssueDetailSerializer,
    CommentSerializer,
    CommentDetailSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.permissions import IsAuthor, IsContributor, IsNotAllowedToList


class ProjectViewset(ModelViewSet):

    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ('retrieve'):
            permission_classes += [IsContributor]
        elif self.action in ('update', 'partial_update', 'destroy'):
            permission_classes += [IsAuthor]
        return [permission() for permission in permission_classes]

    def create(self, request):
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContributorViewset(ModelViewSet):

    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contributor.objects.all()

    def create(self, request):
        'Check if request user is not already contributor'
        if not Contributor.objects.filter(project=request.data['project'], user=request.user.id).exists():
            serializer = self.serializer_class(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response({'detail': 'Création impossible'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Création impossible'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None):
        return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        if request.user == Contributor.objects.get(pk=pk).user:
            product = self.get_object()
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Suppression impossible'}, status=status.HTTP_403_FORBIDDEN)


class IssueViewset(ModelViewSet):

    serializer_class = IssueSerializer
    detail_serializer_class = IssueDetailSerializer

    def get_queryset(self):
        return Issue.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsNotAllowedToList]
        if self.action in ('create', 'retrieve'):
            permission_classes += [IsContributor]
        elif self.action in ('update', 'partial_update', 'destroy'):
            permission_classes += [IsAuthor]
        return [permission() for permission in permission_classes]

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({'detail': 'Création impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        issue = self.get_object()
        serializer = self.get_serializer(issue)
        return Response(serializer.data)

    def update(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        product = self.get_object()
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewset(ModelViewSet):

    serializer_class = CommentSerializer
    detail_serializer_class = CommentDetailSerializer

    def get_queryset(self):
        return Comment.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsNotAllowedToList]
        if self.action in ('create', 'retrieve'):
            permission_classes += [IsContributor]
        elif self.action in ('update', 'partial_update', 'destroy'):
            permission_classes += [IsAuthor]
        return [permission() for permission in permission_classes]

    def create(self, request):
        if Issue.objects.filter(pk=request.data['issue']).exists():
            serializer = CommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Création impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        product = self.get_object()
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
