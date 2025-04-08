from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from api.models import Project, Contributor, Issue, Comment
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
        contributor_list = (contributor.user for contributor in queryset)
        serializer = UserSerializer(contributor_list, many=True)
        return serializer.data

    def get_issues(self, instance):
        queryset = Issue.objects.filter(project=instance)
        serializer = IssueWithoutProjectSerializer(queryset, many=True)
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
            'project',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = UserSerializer(instance.user).data
        ret['project'] = ProjectSerializer(instance.project).data
        return ret

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
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
    comments = serializers.SerializerMethodField()

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

    def get_comments(self, instance):
        comment_list = Comment.objects.filter(issue=instance)
        serializer = CommentSerializer(comment_list, many=True)
        return serializer.data


class CommentSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            'id',
            'description',
            'date_created',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data
        return ret

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['issue'] = Issue.objects.get(pk=self.context['request'].POST['issue'])
        return super().create(validated_data)


class CommentDetailSerializer(ModelSerializer):

    author = UserSerializer()
    issue = IssueSerializer()

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'description',
            'date_created',
            'issue'
        ]
