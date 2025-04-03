from rest_framework.viewsets import ModelViewSet
from api.models import Project, Contributor, Issue, Comment
from api.serializers import (
    ProjectSerializer,
    ProjectDetailSerializer,
    ContributorSerializer,
    IssueSerializer,
    IssueDetailSerializer,
    CommentSerializer,
    CommentDetailSerializer,
)
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class IsAuthor(BasePermission):
    message = "Vous devez être l'auteur du projet"

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author


class IsRequestUser(BasePermission):
    message = "Vous n'êtes pas concerné"

    def has_permission(self, request, view):
        # Verifier l'interet de != list
        return str(request.user.id) == request.POST['user'] and view.action != 'list'


class IsContributor(BasePermission):

    message = 'Vous ne faites pas partie du projet'

    def has_permission(self, request, view):
        if 'project' in request.data:
            project = Project.objects.get(pk=request.data['project'])
            return Contributor.objects.filter(project=project, user=request.user).exists()
        return True

    def has_object_permission(self, request, view, obj):
        return Contributor.objects.filter(project=obj.project, user=request.user).exists()


class IsNotAllowedToList(BasePermission):

    message = 'Impossible de lister'

    def has_permission(self, request, view):
        return view.action != 'list'


class ProjectViewset(ModelViewSet):

    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated, IsAuthor]

    def get_queryset(self):
        return Project.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request):
        self.permission_classes = [IsAuthenticated]
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            project = serializer.save()
            # Add author to contributor automatically
            contributor = ContributorSerializer(
                data={
                    'user': request.user.id,
                    'project': project.id
                }
            )
            if contributor.is_valid():
                contributor.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContributorViewset(ModelViewSet):

    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contributor.objects.all()

    def create(self, request):
        if str(request.user.id) == request.data['user']:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
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
    permission_classes = [IsAuthenticated, IsNotAllowedToList]

    def get_queryset(self):
        return Issue.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request):
        self.permission_classes += [IsContributor]
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Création impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes += [IsContributor]
        issue = self.get_object()
        serializer = self.get_serializer(issue)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes += [IsAuthor]
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        self.permission_classes += [IsAuthor]
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes += [IsAuthor]
        product = self.get_object()
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewset(ModelViewSet):

    serializer_class = CommentSerializer
    detail_serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticated, IsNotAllowedToList]

    def get_queryset(self):
        return Comment.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request):
        self.permission_classes += [IsContributor]
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Création impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        self.permission_classes += [IsAuthor]
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        self.permission_classes += [IsAuthor]
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'detail': 'Mise à jour impossible'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes += [IsAuthor]
        product = self.get_object()
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
