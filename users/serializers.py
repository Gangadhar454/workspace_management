from rest_framework import serializers
from .models import User, Team

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'age', 'gender']

class TeamSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'members', 'member_ids']