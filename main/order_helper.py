from django.db.models import Q
from django.db.models import Count

import main.models as MainModel

class OrderHelper(object):

    def _queryset(self, orderId, start_time, end_time, queryset):
        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__order_status=0) &
                ~Q(order__orderId=orderId) &
            ( Q(order__start_time__range=(start_time, end_time)) 
            | Q(order__end_time__range=(start_time, end_time))))

        return queryset

    def order_queryset(self, orderType, start_time, end_time, orderId=None):

        if orderType == '0': 
            return self._queryset(orderId, start_time, end_time, MainModel.Vehicle.objects.filter(status=1))
        elif orderType == '1':
            return self._queryset(orderId, start_time, end_time, MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, driver=True, model=None))
        elif orderType == '2':
            return self._queryset(orderId, start_time, end_time, MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, tourguide=True, model=None))
        elif orderType == '3':
            return self._queryset(orderId, start_time, end_time, MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, tourguide=True, driver=True, model=None))
        elif orderType == '4': 
            return self._queryset(orderId, start_time, end_time, MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, driver=True).exclude(model=None))
    
    def staff_queryset(self, start_time, end_time, staff, orderId=None):
        return MainModel.Order.objects.exclude(orderId=orderId).filter(order_status=0, staff=staff).filter(
            Q(start_time__range=(start_time, end_time)) 
            | Q(end_time__range=(start_time, end_time))
            ).aggregate(count=Count('staff'))
    
    def vehicle_queryset(self, start_time, end_time, vehicle, orderId=None):
        return MainModel.Order.objects.exclude(orderId=orderId).filter(order_status=0, vehicle=vehicle).filter(
            Q(start_time__range=(start_time, end_time)) 
            | Q(end_time__range=(start_time, end_time))
            ).aggregate(count=Count('vehicle'))

    def refund(self, order):
        query_set = MainModel.AccountDetail.objects.filter(order=order).filter(status=True).filter(Q(detail_type=1) | Q(detail_type=3))

        for query in query_set:
            order.company.balance = order.company.balance + query.amount
            order.company.save()
            query.status = False
            query.save()
            MainModel.AccountDetail.objects.create(amount=query.amount, detail_type=2, order=order, company=order.company)

