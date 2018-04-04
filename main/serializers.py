from rest_framework import serializers
import main.models as MainModel


class DLISerializer(serializers.ModelSerializer):
    class Meta:
        model = MainModel.DLI
        fields = '__all__'


class TLISerializer(serializers.ModelSerializer):
    class Meta:
        model = MainModel.TLI
        fields = '__all__'


class PPISerializer(serializers.ModelSerializer):
    class Meta:
        model = MainModel.PPI
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainModel.Staff
        fields = ['userId', 'name', 'phone', 'photo', 'status',
                  'driver', 'tourguide']

class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainModel.Vehicle
        fields = ['id', 'traffic_plate_no', 'model_name', 'model_year',
                  'num_of_pass', 'exp_date', 'policy_no', 'rate', 'status']

class ClientCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = MainModel.ClientCompany
        fields = '__all__'                  

class ClientSerializer(serializers.ModelSerializer):

    company = ClientCompanySerializer()

    class Meta:
        model = MainModel.Client
        fields = ['userId', 'name', 'phone', 'client_type', 'company']

class OrderStaffSerializer(serializers.ModelSerializer):

    staff = StaffSerializer()
    client = ClientSerializer()

    class Meta:
        model = MainModel.OrderStaff
        fields = '__all__'
