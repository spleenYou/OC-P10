from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from api.models import Project, Contributor, Issue
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
    issues = serializers.SerializerMethodField()

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
        queryset = Contributor.objects.filter(project=instance)
        contributor_list = []
        for contributor in queryset:
            contributor_list.append(
                {
                    'id': contributor.user.id,
                    'username': contributor.user.username
                }
            )
        serializer = UserSerializer(contributor_list, many=True)
        return serializer.data

    def get_issues(self, instance):
        queryset = Issue.objects.filter(project=instance)
        issue_list = []
        for issue in queryset:
            issue_list.append(
                {
                    'id': issue.pk,
                    'title': issue.title,
                    'author': issue.author,
                    'project': issue.project,
                    'description': issue.description,
                    'status': issue.status,
                    'priority': issue.priority,
                    'tag': issue.tag,
                    'assigned_user': issue.assigned_user,
                    'date_created': issue.date_created,
                }
            )
        serializer = IssueWithoutProjectSerializer(issue_list, many=True)
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


class ContributorSerializer(ModelSerializer):

    class Meta:
        model = Contributor
        fields = [
            'user',
            'project',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = UserSerializer(instance.user).data
        ret['project'] = ProjectSerializer(instance.project).data
        return ret

    def create(self, validated_data):
        return super().create(validated_data)


class IssueWithoutProjectSerializer(ModelSerializer):

    assigned_user = UserSerializer()
    author = UserSerializer()

    class Meta:
        model = Issue
        fields = [
            'id',
            'author',
            'title',
            'description',
            'status',
            'priority',
            'tag',
            'assigned_user',
            'date_created',
        ]


class IssueSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = [
            'id',
            'project',
            'title',
            'description',
            'status',
            'priority',
            'tag',
            'assigned_user',
            'date_created',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data
        ret['assigned_user'] = UserSerializer(instance.assigned_user).data
        ret['project'] = ProjectSerializer(instance.project).data
        return ret

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        if 'assigned_user' not in validated_data:
            validated_data['assigned_user'] = self.context['request'].user
        return super().create(validated_data)


class IssueDetailSerializer(ModelSerializer):

    author = UserSerializer()
    assigned_user = UserSerializer()
    project = ProjectSerializer()

    class Meta:
        model = Issue
        fields = [
            'id',
            'author',
            'project',
            'title',
            'description',
            'status',
            'priority',
            'tag',
            'assigned_user',
            'date_created',
            'comments',
        ]
