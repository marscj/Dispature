from django.db.models import Q
from django.db.models import Count

import main.models as MainModel
from datetime import datetime

class OrderHelper(object):

    def _queryset(self, orderId, start_time, end_time, queryset):
        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__order_status=0) &
                ~Q(order__orderId=orderId) &
            ( Q(order__start_time__range=(start_time, end_time)) 
            | Q(order__end_time__range=(start_time, end_time))))

        return queryset

    def order_queryset(self, orderType, start_time, end_time, orderId=None, model=None):

        if orderType == 0: 
            return self._queryset(orderId, start_time, end_time, MainModel.Vehicle.objects.filter(status=1, model__model=model))
        elif orderType == 1:
            return self._queryset(orderId, start_time, end_time, MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, driver=True, model=None))
        elif orderType == 2:
            return self._queryset(orderId, start_time, end_time, MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, tourguide=True, model=None))
        elif orderType == 3:
            return self._queryset(orderId, start_time, end_time, MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, tourguide=True, driver=True, model=None))
        elif orderType == 4: 
            return self._queryset(orderId, start_time, end_time, MainModel.Staff.objects.filter(status=1, is_active=True, accept=True, driver=True).exclude(model=None))
    
    def order_staff_exsit(self, start_time, end_time, staff, orderId=None):
        count = MainModel.Order.objects.exclude(orderId=orderId).filter(order_status=0, staff=staff).filter(
            Q(start_time__range=(start_time, end_time)) 
            | Q(end_time__range=(start_time, end_time))
            ).aggregate(count=Count('staff'))
        return count['count'] > 0

    
    def order_vehicle_exsit(self, start_time, end_time, vehicle, orderId=None):
        count = MainModel.Order.objects.exclude(orderId=orderId).filter(order_status=0, vehicle=vehicle).filter(
            Q(start_time__range=(start_time, end_time)) 
            | Q(end_time__range=(start_time, end_time))
            ).aggregate(count=Count('vehicle'))
        return count['count'] > 0

    def get_refund_amount(self, order):
        query_set = MainModel.AccountDetail.objects.filter(order=order, status=True).filter(Q(detail_type=1) | Q(detail_type=3))

        amount = 0

        for query in query_set:
            amount = amount + query.amount
            query.status = False
            query.save()

        return amount

    def get_amount(self, order_type, store, model=None):
        
        if order_type == 0:
            return round(model.daily_charge, 2), round(model.premium_charge, 2), round(store.service_charge, 2), round(store.home_service_charge, 2)

        elif order_type == 4:
            return round(model.special_daily_charge, 2)
        
        elif order_type == 1:
            return round(store.driver_daily_charge, 2)

        elif order_type == 2:
            return round(store.tourguide_daily_charge, 2)
        
        elif order_type == 3:
            return round(store.dt_daily_charge, 2)

    def create_account_detail(self, amount, detail_type, order, company):
        
        if detail_type == 0 or detail_type ==2:
            company.balance = round(company.balance + amount, 2)
        else:
            company.balance = round(company.balance - amount, 2)

        company.save()
        MainModel.AccountDetail.objects.create(amount=amount, detail_type=detail_type, order=order, company=company, balance=company.balance)

    def create_order_id(self):
        return datetime.now().strftime("%Y%m%d-%H%M%S-%f")

    def get_order_charge(self, order_type, days, store, model, discount, service_type=None):
        if order_type == 0:
            amount, premium_charge, service_charge, home_service_charge = self.get_amount(order_type, store, model)
            return round(((amount + premium_charge) * days + service_charge + home_service_charge) * (1 - discount), 2), amount * days, premium_charge, service_charge, home_service_charge
        else:
            amount= self.get_amount(order_type, store, model)
            return round(amount * days * (1 - discount), 2), amount * days

        

