from rest_framework import serializers
import main.models as MainModel
from phonenumber_field.serializerfields import PhoneNumberField

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
    phone = PhoneNumberField()
    dli = DLISerializer(required=False, allow_null=True, many=False)
    tli = TLISerializer(required=False, allow_null=True, many=False)
    name = serializers.CharField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = MainModel.Staff
        fields = ['userId', 'name', 'phone', 'photo', 'status', 'accept', 'dli', 'tli',
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

    staff = StaffSerializer(required=False, allow_null=True)
    client = ClientSerializer(required=False, allow_null=True)
    start_time = serializers.DateTimeField(required=False, allow_null=True)
    end_time = serializers.DateTimeField(required=False, allow_null=True)
    orderId = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = MainModel.OrderStaff
        fields = '__all__'
