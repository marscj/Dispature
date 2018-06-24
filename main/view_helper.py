from django.db.models import Q
from django.db.models import Count

import main.models as MainModel

class ViewHelper(object):

    def get_staff_queryset(self, start_time, end_time):
        queryset = MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, model=None)
                   
        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__order_status=0) &
            ( Q(order__start_time__range=(start_time, end_time)) 
            | Q(order__end_time__range=(start_time, end_time))))
        
        return queryset

    def get_special_queryset(self, start_time, end_time):
        queryset = MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, driver=True).exclude(model=None)
        
        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__order_status=0) &
            ( Q(order__start_time__range=(start_time, end_time)) 
            | Q(order__end_time__range=(start_time, end_time))))

        return queryset
    
    def get_vehiclemodel_queryset(self, start_time, end_time, model, store):
        queryset = MainModel.VehicleModel.objects.filter(model=model, store=store)

        if start_time is not None and end_time is not None:
            for vehicle_model in queryset:
                vehicle_model.count = self.get_vehicle_queryset(start_time, end_time, vehicle_model).count()

        return queryset

    def get_vehicle_queryset(self, start_time, end_time, vehicle_model):
        queryset = MainModel.Vehicle.objects.filter(model=vehicle_model).exclude(
                Q(order__order_status=0) &
            ( Q(order__start_time__range=(start_time, end_time)) 
            | Q(order__end_time__range=(start_time, end_time))))

        return queryset
