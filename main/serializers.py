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
        fields = ['id', 'phone', 'tel', 'name', 'email', 'addr', 'latitude', 'longitude', 'driver_daily_charge', 'tourguide_daily_charge', 'dt_daily_charge', 'open_time', 'close_time', 'home_service_charge']


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
    admin = ClientMiniSerializer(read_only=True, many=False)
    
    class Meta:
        model = MainModel.Company
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainModel.Client
        fields = ['userId', 'name', 'phone', 'company']

class OrderSerializer(serializers.ModelSerializer):

    staff = StaffSerializer(required=False, allow_null=True)
    client = ClientSerializer(required=False, allow_null=True)
    company = CompanySerializer(required=True, allow_null=False)
    store = StoreSerializer(required=False, allow_null=False)

    class Meta:
        model = MainModel.Order
        fields = '__all__'

class VehicleModelSellSerializer(serializers.ModelSerializer):

    count = serializers.IntegerField()

    class Meta:
        model = MainModel.VehicleModel
        fields = ['id', 'count', 'model', 'name', 'seats', 'daily_charge', 'photo', 'store', 'automatic']

class AccountDetailSerializer(serializers.ModelSerializer):

    order = serializers.StringRelatedField(allow_null=True)
    company = serializers.StringRelatedField()
    # balance = serializers.SerializerMethodField()

    class Meta:
        model = MainModel.AccountDetail
        fields = ['id', 'amount', 'detail_type', 'explanation', 'create_time', 'order', 'company', 'balance']
    # def get_balance(self, obj):
    #     return obj.company.balance