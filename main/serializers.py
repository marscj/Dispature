from rest_framework import serializers
from .models import Staff, Vehicle, TLI, DLI, PPI


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


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'phone', 'photo', 'status',
                  'is_driver', 'is_tourguide', 'is_operator']

class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = ['id', 'traffic_plate_no', 'model_name', 'model_year',
                  'num_of_pass', 'exp_date', 'policy_no', 'rate', 'status']
