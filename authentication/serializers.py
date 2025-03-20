from rest_framework import serializers
from authentication.models import User
from django.contrib.auth.password_validation import validate_password
import datetime


class UserSerializer(serializers.ModelSerializer):

    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    can_be_contacted = serializers.BooleanField(default=None)
    can_data_be_shared = serializers.BooleanField(default=None)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'birthday', 'can_be_contacted', 'can_data_be_shared']
        extra_kwargs = {
            'birthday': {'required': True},
        }

    def validate(self, attrs):
        # print(attrs)
        if (datetime.datetime.now().year - attrs['birthday'].year <= 15 and
                attrs['birthday'].month <= datetime.datetime.now().month and
                attrs['birthday'].day <= datetime.datetime.now().day):
            raise serializers.ValidationError({'age': 'You are too young'})
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Password fields didn't match"})
        return attrs

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


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'can_be_contacted', 'can_data_be_shared']


class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'birthday', 'can_be_contacted', 'can_data_be_shared']
