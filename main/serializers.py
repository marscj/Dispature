from rest_framework import serializers

from .models import *


class DLISerializer(serializers.ModelSerializer):
    class Meta:
        model = DLI
        fields = '__all__'


class TLISerializer(serializers.ModelSerializer):
    class Meta:
        model = TLI
        fields = '__all__'


class PPISerializer(serializers.ModelSerializer):
    class Meta:
        model = PPI
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseGroup
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'phone', 'photo', 'status', 'is_driver', 'is_tourguide', 'is_operator']


class StaffDetailSerializer(serializers.ModelSerializer):
    group = GroupSerializer(many=True, read_only=True)
    DLI = PPISerializer(many=False, read_only=False)
    TLI = PPISerializer(many=False, read_only=False)
    PPI = PPISerializer(many=False, read_only=False)

    class Meta:
        model = Staff
        exclude = ['password', 'first_name', 'last_name',
                   'email', 'create_time', 'user_permissions']


class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = ['id', 'traffic_plate_no', 'model_name', 'model_year',
                  'num_of_pass', 'exp_date', 'policy_no', 'rate', 'status']


class VehicleDetailSerializer(serializers.ModelSerializer):
    group = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['id', 'create_time', 'start_time_in', 'end_time_in',
                  'vehicle', 'driver', 'tourguide', 'start_addr', 'end_addr', ]


class TaskDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'
