from rest_framework import serializers
from authentication.models import User
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
import datetime
from api.serializers import ProjectSerializerForUserDetail, ProjectSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from api.models import Contributor


class UserCreateSerializer(serializers.ModelSerializer):

    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    # Put to default=None to force them on request
    can_be_contacted = serializers.BooleanField(default=None)
    can_data_be_shared = serializers.BooleanField(default=None)

    class Meta:
        model = User
        fields = ['id', 'username', 'password1', 'password2', 'birthday', 'can_be_contacted', 'can_data_be_shared']
        extra_kwargs = {
            'birthday': {'required': True},
        }

    def validate_birthday(self, value):
        'Check if the user is at least 15 years old (365*15 + 3 for leap years)'

        if value > (datetime.datetime.now() - datetime.timedelta(days=5475)).date():
            raise serializers.ValidationError('You are too young')
        return value

    def validate(self, attrs):
        'Check if both passwords send are same'

        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError(
                {
                    'detail': "Création impossible"
                }
            )
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['date_created'] = instance.date_joined
        return ret

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            birthday=validated_data['birthday'],
            can_be_contacted=validated_data['can_be_contacted'],
            can_data_be_shared=validated_data['can_data_be_shared'],
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):

    projects_created = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'birthday', 'can_be_contacted', 'can_data_be_shared', 'projects_created']

    def get_projects_created(self, instance):
        queryset = instance.projects_created.all()
        serializer = ProjectSerializerForUserDetail(queryset, many=True)
        return serializer.data

    def contribute_to(self, user):
        queryset = Contributor.objects.filter(user=user).exclude(project__author=user)
        queryset = (contributor.project for contributor in queryset)
        serializer = ProjectSerializer(queryset, many=True)
        return serializer.data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['contribute_to'] = self.contribute_to(instance)
        if not (ret['can_data_be_shared'] or (self.context['request'].user == instance)):
            del ret['birthday']
        else:
            ret['date_created'] = instance.date_joined
        return ret


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['access_token'] = data.pop('access')
        data['refresh_token'] = data.pop('refresh')
        data['expires_in'] = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):

    def validate_empty_values(self, value):
        refresh_token = {'refresh': value['refresh_token']}
        return (False, refresh_token)

    def validate(self, attrs):
        data = super().validate(attrs)
        data['access_token'] = data.pop('access')
        data['expires_in'] = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        return data
