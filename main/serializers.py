from rest_framework import serializers

from .models import *


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'phone', 'photo', 'status', 'is_driver', 'is_tourguide', 'is_operator']


class StaffDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        exclude = ['password', 'first_name', 'last_name',
                   'email', 'create_time', 'user_permissions', 'group']


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['id', 'create_time',
                  'start_time_in',
                  'end_time_in',
                  'vehicle',
                  'driver',
                  'tourguide',
                  'start_addr',
                  'end_addr', ]


class TaskDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'
