from rest_framework.viewsets import ModelViewSet
from api.models import Project
from api.serializers import ProjectSerializer, ProjectDetailSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class ProjectViewset(ModelViewSet):

    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.all()

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request):
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(f"Erreurs : {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
