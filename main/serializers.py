from rest_framework import serializers
import main.models as MainModel
from phonenumber_field.serializerfields import PhoneNumberField
from django_countries.serializer_fields import CountryField

class DLISerializer(serializers.ModelSerializer):

    class Meta:
        model = MainModel.DLI
        fields = '__all__'


class TLISerializer(serializers.ModelSerializer):

    class Meta:
        model = MainModel.TLI
        fields = '__all__'


class PPISerializer(serializers.ModelSerializer):

    country = CountryField(country_dict=True)

    class Meta:
        model = MainModel.PPI
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):

    phone = PhoneNumberField()
    tel = PhoneNumberField()

    class Meta:
        model = MainModel.Store
        fields = ['id', 'phone', 'tel', 'name', 'email', 'addr', 'latitude', 'longitude', 'driver_day_pay', 'tourguide_day_pay', 'dt_day_pay', 'open_time', 'close_time', 'delivery_pay']


class VehicleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainModel.VehicleModel
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):

    model = VehicleModelSerializer(required=False, allow_null=True)

    class Meta:
        model = MainModel.Vehicle
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()
    dli = DLISerializer(required=False, allow_null=True, many=False)
    tli = TLISerializer(required=False, allow_null=True, many=False)
    ppi = PPISerializer(required=False, allow_null=True, many=False)
    name = serializers.CharField(required=False, allow_null=True)
    model = VehicleModelSerializer()

    class Meta:
        model = MainModel.Staff
        fields = ['userId', 'name', 'phone', 'photo', 'status', 'accept', 'dli', 'tli', 'ppi', 'store', 'model',
                  'driver', 'tourguide']

class ClientMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainModel.Client
        fields = ['userId', 'name']

class CompanySerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()
    tel = PhoneNumberField()
    client = ClientMiniSerializer(read_only=True, many=True)
    admin = ClientMiniSerializer(read_only=True, many=False)
    
    class Meta:
        model = MainModel.Company
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):

    company = CompanySerializer(allow_null=True)

    class Meta:
        model = MainModel.Client
        fields = ['userId', 'name', 'phone', 'company']

class OrderSerializer(serializers.ModelSerializer):

    staff = StaffSerializer(required=False, allow_null=True)
    client = ClientSerializer(required=False, allow_null=True)
    start_time = serializers.DateTimeField(required=False, allow_null=True)
    end_time = serializers.DateTimeField(required=False, allow_null=True)
    orderId = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = MainModel.Order
        fields = '__all__'

class VehicleModelSellSerializer(serializers.ModelSerializer):

    count = serializers.IntegerField(default=0)

    class Meta:
        model = MainModel.VehicleModel
        fields = ['id', 'count', 'model', 'name', 'seats', 'day_pay', 'photo', 'store', 'automatic']
