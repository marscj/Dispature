from rest_framework import serializers

from .models import *


class StaffSerializer(serializers.ModelSerializer):

    class Meat:
        model = Staff
        fields = '__all__'
