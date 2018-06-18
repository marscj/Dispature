from django.db.models import Q

import main.models as MainModle

class OrderHelper(object):

    def _queryset(self, orderId, start_time, end_time, queryset):
        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__order_status=0) &
                ~Q(order__orderId=orderId) &
            ( Q(order__start_time__range=(start_time, end_time)) 
            | Q(order__end_time__range=(start_time, end_time))))

        return queryset 

    def order_queryset(self, orderId, orderType, start_time, end_time):

        if orderType == '0': 
            return self._queryset(orderId, start_time, end_time, MainModle.Vehicle.objects.filter(status=1))
        elif orderType == '1':
            return self._queryset(orderId, start_time, end_time, MainModle.Staff.objects.filter(status=1, is_active=True, accept=True, driver=True, model=None))
        elif orderType == '2':
            return self._queryset(orderId, start_time, end_time, MainModle.Staff.objects.filter(status=1, is_active=True, accept=True, tourguide=True, model=None))
        elif orderType == '3':
            return self._queryset(orderId, start_time, end_time, MainModle.Staff.objects.filter(status=1, is_active=True, accept=True, tourguide=True, driver=True, model=None))
        elif orderType == '4': 
            return self._queryset(orderId, start_time, end_time, MainModle.Staff.objects.filter(status=1, is_active=True, accept=True, driver=True).exclude(model=None))