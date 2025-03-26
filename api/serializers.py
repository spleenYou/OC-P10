from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from api.models import Project
from authentication.models import User


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class ProjectSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
            'project_type',
            'date_created'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data
        return ret

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ProjectDetailSerializer(ModelSerializer):

    author = UserSerializer()
    contributors = serializers.SerializerMethodField()

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
            'contributors',
        ]

    def get_contributors(self, instance):
        queryset = instance.contributors.all()
        serializer = UserSerializer(queryset, many=True)
        return serializer.data


class ProjectSerializerForUserDetail(ModelSerializer):

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'project_type',
            'date_created'
        ]
