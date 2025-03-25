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
        fields = [
            'id',
            'title',
            'author',
            'project_type',
            'date_created'
        ]


class ProjectDetailSerializer(ModelSerializer):

    author = AuthorSerializer()

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'author',
            'date_created',
            'description',
            'project_type',
            'issues',
        ]


class ProjectSerializerForUserDetail(ModelSerializer):

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'project_type',
            'date_created'
        ]
