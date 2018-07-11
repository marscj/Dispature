from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404 

from rest_framework import views, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework import authentication, permissions
from rest_framework import serializers
import rest_framework.filters as filters

from django_filters.rest_framework import DjangoFilterBackend

from main.view_helper import ViewHelper
import main.models as MainModel
import main.serializers as MainSerializers
import main.forms as MainForm
from main.order_helper import OrderHelper
from .utils import Tools
from datetime import datetime

import json

class Utf8JSONRenderer(JSONRenderer):
    charset = 'utf-8'

class SignInView(ObtainAuthToken):
    renderer_classes = (Utf8JSONRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})

        try:
            serializer.is_valid(raise_exception=True) #
        except serializers.ValidationError:
            return Response(_('Unable to log in with provided credentials.'), status=400)

        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)

        try:
            client = MainSerializers.ClientSerializer(user.client)
            return Response({
                    'token': token.key,
                    'username': user.username,
                    'userId': client.data['userId'],
                    'name': client.data['name'],
                    'phone': client.data['phone'],
                    'company': client.data['company'],
                })
        except Exception:
            pass

        try:
            staff = MainSerializers.StaffSerializer(user.staff)
            return Response({
                    'token': token.key,
                    'username': user.username,
                    'userId': staff.data['userId'],
                    'name': staff.data['name'],
                    'phone': staff.data['phone'],
                    'store': staff.data['store'],
                })
        except Exception:
            pass
        
        return Response({'token': token.key})


class ClientSignUp(views.APIView):
    permission_classes = [permissions.AllowAny,]
    renderer_classes = (Utf8JSONRenderer,)
    
    def post(self, request):
        client = MainForm.ClientCreateForm(request.data)

        if client.is_valid():
            client.save()
            return Response('ok')
        
        return Response(client.errors, status=400)

class ResetPassword(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    def post(self, request):
        username = request.data['username']
        oldPassword = request.data['oldPassword']
        newPassword = request.data['newPassword']

        user = authenticate(username=username, password=oldPassword)
        if user is not None:
            if user.is_active:
                if newPassword:
                    try:
                        password_validation.validate_password(newPassword, user)
                        user.set_password(newPassword)
                        user.save()
                        return Response('ok')
                    except ValidationError as error:
                        return Response(error.messages[0], status=400)
                    
        return Response(_('Unable to reset password with provided credentials.'), status=400)

class BindCompany(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    def get(self, request):
        try:
            user = request.user.client
        except Exception:
            return Response(status=404)
        
        name = self.request.query_params.get('name', None)
        verify = self.request.query_params.get('verify', None)

        if name is not None and verify is not None:
            try:
                company = MainModel.Company.objects.get(name=name)

                if company.verify == verify:
                    user.company = company
                    user.save()

                    company.verify = get_random_string(length=4, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                    company.save()
                else:
                    return Response(_('Verification code erro.'), status=400)
            except Exception:
                return Response(_('Can\'t find the company.'), status=400)

            client = MainSerializers.CompanySerializer(company)
            return Response(client.data)
        else:
            return Response(_('Parameter error.'), status=400)

class UnBindCompany(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    def get(self, request):
        try:
            userId = request.query_params.get('userId', None)
            unbindUser = MainModel.Client.objects.get(userId=userId)
        except Exception:
            return Response(status=404)
        
        try:
            user = request.user.client
        except Exception:
            return Response(status=404)

        if user.company is not None:
            if user.company.admin is not None and user.company.admin.userId == user.userId:
                if user.company.admin.userId != unbindUser.userId:
                    unbindUser.company = None
                    unbindUser.save()
                    company = MainSerializers.ClientMiniSerializer(user.company.client, many=True)
                    return Response(company.data)
                else :
                    return Response(_('Can\'t delete admin.'), status=400)
            else :
                return Response(_('Permission denied.'), status=400)
        else :
            return Response(_('You are not a business user.'), status=400)

class CompanyView(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    def get(self, request):
        try:
            user = request.user.client
        except Exception:
            return Response(status=404)

        if user.company is not None:
            company = MainSerializers.CompanySerializer(user.company)
            return Response(company.data)
        else :
            return Response(status=400)

class CompanyClientView(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    def get(self, request):
        try:
            user = request.user.client
        except Exception:
            return Response(status=404)

        if user.company is not None:
            client = MainSerializers.ClientMiniSerializer(user.company.client, many=True)
            return Response(client.data)
        else :
            return Response(status=400)

class SettlementView(views.APIView, OrderHelper):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    def post(self, request):

        try:
            user = request.user.client
        except Exception:
            return Response(status=404)

        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        order_type = request.data.get('order_type')
        store = get_object_or_404(MainModel.Store, pk=request.data.get('store').get('id'))

        duration = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")  - datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

        if user.company is None:
            return Response(_('You are not a business user.'), status=400)

        if start_time > end_time:
            return Response(_('End time must be later than start time.'), status=400)
        
        if duration.days * 24 * 3600 + duration.seconds < 3600:
            return Response(_('Duration is too short.'), status=400)

        days = Tools.convert_timedelta(duration)
        settle = MainSerializers.Settlement(start_time, end_time, order_type, user.company.discount, store)
        settle.remake = request.data.get('remake')
        
        if order_type == 0:
            model = get_object_or_404(MainModel.VehicleModel, pk=request.data.get('model').get('id'))
            service_type = request.data.get('service_type')
            total, amount, premium_charge, service_charge, home_service_charge = self.get_order_charge(order_type, days, store, model, user.company.discount, service_type=service_type)
            
            settle.amount = amount
            settle.total = total
            settle.model = model
            settle.service_type = service_type
            settle.service_charge = service_charge
            settle.premium_charge = premium_charge * days

            if service_type == 1:
                settle.home_service_charge = home_service_charge
                settle.pick_up_addr = request.data.get('pick_up_addr')
                settle.drop_off_addr = request.data.get('drop_off_addr')

        else:
            staff = get_object_or_404(MainModel.Staff, pk=request.data.get('staff').get('userId'))
            total, amount = self.get_order_charge(order_type, days, store, staff.model, user.company.discount)

            settle.amount= amount
            settle.total = total
            settle.staff = staff
            
        _settle = MainSerializers.SettlementSerializer(settle)
        return Response(_settle.data)

class OrderCreateView(views.APIView, OrderHelper):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    def post(self, request):
        
        try:
            user = request.user.client
        except Exception:
            return Response(status=404)

        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        order_type = request.data.get('order_type')
        remake = request.data.get('remake')
        store = get_object_or_404(MainModel.Store, pk=request.data.get('store').get('id'))

        duration = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")  - datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

        if user.company is None:
            return Response(_('You are not a business user.'), status=400)

        if start_time > end_time:
            return Response(_('End time must be later than start time.'), status=400)
        
        if duration.days * 24 * 3600 + duration.seconds < 3600:
            return Response(_('Duration is too short.'), status=400)

        days = Tools.convert_timedelta(duration)
        
        if order_type == 0:
            service_type = request.data.get('service_type')
            model = get_object_or_404(MainModel.VehicleModel, pk=request.data.get('model').get('id'))
            order_query = self.order_queryset(order_type, start_time, end_time, model=model.model)
            
            if order_query is None or order_query.count() == 0:
                return Response(_('It is out of stock.'), status=400)
            
            total, amount, premium_charge, service_charge, home_service_charge = self.get_order_charge(order_type, days, store, model, user.company.discount, service_type=service_type)
            
            if user.company.balance - total < 0:
                    return Response(_('The company no balance'), status=400)

            if service_type == 0:
                order = MainModel.Order.objects.create(
                    orderId=self.create_order_id(),
                    start_time=start_time, 
                    end_time=end_time, 
                    duration=duration,
                    order_type=order_type, 
                    order_status=0,
                    pay_status=1,
                    remake=remake,
                    service_type=service_type,
                    client=user,
                    vehicle=order_query[0],
                    company=user.company,
                    store=store)
            else:
                order = MainModel.Order.objects.create(
                    orderId=self.create_order_id(),
                    start_time=start_time, 
                    end_time=end_time, 
                    duration=duration,
                    order_type=order_type, 
                    order_status=0,
                    pay_status=1,
                    remake=remake,
                    service_type=1,
                    pick_up_addr=request.data.get('pick_up_addr'),
                    drop_off_addr=request.data.get('drop_off_addr'),
                    client=user,
                    vehicle=order_query[0],
                    company=user.company,
                    store=store)

            self.create_account_detail(total, 1, order, user.company)

        else:
            staff = get_object_or_404(MainModel.Staff, pk=request.data.get('staff').get('userId'))

            if self.order_staff_exsit(start_time, end_time, staff):
                return Response(_('Staff is busy.'), status=400)
                
            total, amount = self.get_order_charge(order_type, days, store, staff.model, user.company.discount)
            
            if user.company.balance - total < 0:
                return Response(_('The company no balance'), status=400)
            
            order = MainModel.Order.objects.create(
                orderId=self.create_order_id(),
                start_time=start_time, 
                end_time=end_time, 
                duration=duration,
                order_type=order_type, 
                order_status=0,
                pay_status=1,
                remake=remake,
                client=user,
                staff=staff,
                staff_status=0,
                company=user.company,
                store=store)

            self.create_account_detail(total, 1, order, user.company)
        
        order.save()
        _order = MainSerializers.OrderSerializer(order)
        return Response(_order.data)

class OrderCancelView(views.APIView, OrderHelper):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    def get(self, request, pk=None):
       
        try:
            order = MainModel.Order.objects.get(pk=pk)
        except order.DoesNotExist:
            return Response(status=404)
        
        if (order.end_time - datetime.now()).days > 2:
            order.order_status = 1
            order.pay_status = 2
            order.save()
        else:
            return Response(_('Failure, need to cancel 2 days in advance'), status=400)
        
        serializer = MainSerializers.OrderSerializer(order)
        return Response(serializer.data)

class OrderRemarkView(views.APIView, OrderHelper):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    def post(self, request, pk=None):
       
        try:
            order = MainModel.Order.objects.get(pk=pk)
        except order.DoesNotExist:
            return Response(status=404)
        
        remark = request.data.get('remark')
        
        order.remake = remark
        order.save()
        
        serializer = MainSerializers.OrderSerializer(order)
        return Response(serializer.data)

class AccountDetailViewSet(viewsets.ModelViewSet):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    queryset = MainModel.AccountDetail.objects.all()
    serializer_class = MainSerializers.AccountDetailSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ['company',]
    ordering = ('-create_time',)


class StaffViewSet(viewsets.ModelViewSet, ViewHelper):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    queryset = MainModel.Staff.objects.all()
    serializer_class = MainSerializers.StaffSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['driver', 'tourguide', 'store']

    def get_queryset(self):
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)
        
        queryset = self.get_staff_queryset(start_time, end_time)
        return queryset

class SpecialViewSet(viewsets.ModelViewSet, ViewHelper):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    queryset = MainModel.Staff.objects.all()
    serializer_class = MainSerializers.StaffSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['store', 'model__model']
    

    def get_queryset(self):
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)
        
        queryset = self.get_special_queryset(start_time, end_time)
        return queryset

class StoreViewSet(viewsets.ModelViewSet):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    queryset = MainModel.Store.objects.all()
    serializer_class = MainSerializers.StoreSerializer
    pagination_class = None

class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    queryset = MainModel.Order.objects.all()
    serializer_class = MainSerializers.OrderSerializer

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ['company']
    ordering = ('order_status', 'start_time')


class ModelViewSet(viewsets.ModelViewSet, ViewHelper):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (Utf8JSONRenderer,)

    queryset = MainModel.VehicleModel.objects.all()
    serializer_class =  MainSerializers.VehicleModelSellSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['model', 'store']

    def get_queryset(self):
        store = self.request.query_params.get('store', None)
        model = self.request.query_params.get('model', None)
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)

        queryset = self.get_vehiclemodel_queryset(start_time, end_time, model, store)    
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = MainSerializers.VehicleModelSellSerializer(queryset, many=True)
        return Response(serializer.data)

class UpLoadFile(views.APIView):

    def post(self, request):
        try:
            staff = request.user.staff
        except Exception:
            return Response(status=401)

        photo=request.FILES.get('photo','')

        if photo:  
            file_content = ContentFile(photo.read()) 
            staff.photo.save(photo.name, file_content)
            staff.save()

            return Response(MainSerializers.StaffSerializer(staff).data)