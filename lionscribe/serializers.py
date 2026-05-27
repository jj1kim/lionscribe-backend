from rest_framework import serializers

from .models import User, Job


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['email', 'name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class JobSerializer(serializers.ModelSerializer):
    result_file_url = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'input_text', 'status',
            'result_file_url', 'error_message',
            'created_at', 'completed_at',
        ]

    def get_result_file_url(self, obj):
        if obj.result_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.result_file.url)
            return obj.result_file.url
        return None


class JobCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    input_text = serializers.CharField()
