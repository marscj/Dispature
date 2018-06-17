from django.db.models import Q

import main.models as MainModle

class OrderHelper(object):

    def _staff_queryset(self, orderId, start_time, end_time):
        queryset = MainModle.Staff.objects.filter(status=1, accept=True, model=None)

        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__order_status=0) &
                ~Q(order__orderId=orderId) &
            ( Q(order__start_time__range=(start_time, end_time)) 
            | Q(order__end_time__range=(start_time, end_time))))

        return queryset 

    def _special_staff_queryset(self, orderId, start_time, end_time):
        queryset = MainModle.Staff.objects.filter(status=1, accept=True).exclude(model=None)

        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__order_status=0) &
                ~Q(order__orderId=orderId) &
            ( Q(order__start_time__range=(start_time, end_time)) 
            | Q(order__end_time__range=(start_time, end_time))))

        return queryset 

    def _vehicle_queryset(self, orderId, start_time, end_time):
        queryset = MainModle.Vehicle.objects.filter(status=1)
        
        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__order_status=0) &
                ~Q(order__orderId=orderId) &
            ( Q(order__start_time__range=(start_time, end_time)) 
            | Q(order__end_time__range=(start_time, end_time))))

        return queryset 

    def helper_queryset(self, orderId, orderType, start_time, end_time):

        if orderType == '0':
            return self._special_staff_queryset(orderId, start_time, end_time)
        elif orderType == '1':
            return self._vehicle_queryset(orderId, start_time, end_time)
        else:
            return self._staff_queryset(orderId, start_time, end_time)