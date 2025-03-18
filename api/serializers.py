from rest_framework.serializers import ModelSerializer

from api.models import Project
from authentication.models import User


class AuthorSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class ProjectSerializer(ModelSerializer):

    author = AuthorSerializer()

    class Meta:
        model = Project
        fields = ['id', 'title', 'author', 'date_created']
