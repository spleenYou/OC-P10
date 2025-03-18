from rest_framework.viewsets import ReadOnlyModelViewSet
# from rest_framework.response import Response

from api.models import Project
from api.serializers import ProjectSerializer


class ProjectAPIView(ReadOnlyModelViewSet):

    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.all()
