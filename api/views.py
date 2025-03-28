from itertools import chain
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
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status


class IsAuthenticatedAndInProject(BasePermission):

    message = 'Vous ne faites pas partie du projet'

    def has_permission(self, request, view):
        print(view.action)

        if view.action == 'list':
            if not (isinstance(view, ContributorViewset) or isinstance(view, ProjectViewset)):
                if isinstance(view, CommentViewset):
                    self.message = 'Impossible de lister les commentaires'
                elif isinstance(view, IssueViewset):
                    self.message = 'Impossible de lister les remarques'
                return False
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(view, ContributorViewset) or isinstance(view, ProjectViewset):
            return True
        elif isinstance(view, CommentViewset):
            author = obj.issue.project.author
            project = obj.issue.project
        elif isinstance(view, IssueViewset):
            author = obj.project.author
            project = obj.project
        contibutor_list = Contributor.objects.filter(project=project)
        contibutor_list = (contributor.user for contributor in contibutor_list)
        contibutor_list = list(chain(contibutor_list, [author]))
        return request.user in contibutor_list


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
        serializer = ContributorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        product = self.get_object()
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewset(ModelViewSet):

    serializer_class = IssueSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticatedAndInProject]

    def get_queryset(self):
        return Issue.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request):
        serializer = IssueSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewset(ModelViewSet):

    serializer_class = CommentSerializer
    detail_serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticatedAndInProject]

    def get_queryset(self):
        return Comment.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request):
        issue = Issue.objects.get(pk=request.data['issue'])
        contibutor_list = Contributor.objects.filter(project=issue.project)
        contibutor_list = (contributor.user for contributor in contibutor_list)
        contibutor_list = list(chain(contibutor_list, [issue.author]))
        if request.user in contibutor_list:
            serializer = CommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': "Vous n'êtes pas affecté au projet"}, status=status.HTTP_401_UNAUTHORIZED)
