from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.db.models import Q

from rest_framework import viewsets, generics, views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action, api_view
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import (IsStaffSelf, IsClientAdmin, IsStaffAdmin,IsAuthenticated, AllowAny, IsAdminOrIsSelf)
from .serializers import (OrderSerializer, StaffSerializer, CompanySerializer, ClientSerializer, VehicleSerializer, TLISerializer,DLISerializer, PPISerializer, StoreSerializer, VehicleModelSellSerializer)
import main.models as MainModel

from rest_framework.renderers import JSONRenderer


class Utf8JSONRenderer(JSONRenderer):
    charset = 'utf-8'


# class BaseModelViewSet(viewsets.ModelViewSet, views.APIView):

#     def get_permissions(self):
#         if self.action == 'list':
#             permission_classes = [IsStaffAdmin]
#         else:
#             permission_classes = [IsAuthenticated]
#         return [permission() for permission in permission_classes]

class BaseModelViewSet(viewsets.ModelViewSet):
    renderer_classes = [Utf8JSONRenderer,]

class StaffViewSet(BaseModelViewSet):
    queryset = MainModel.Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = ['userId', 'driver', 'tourguide', 'status', 'accept', 'store', 'model']
    search_fields = '__all__'
    ordering_fields = '__all__' 

    def get_queryset(self):
        queryset = MainModel.Staff.objects.all().filter(status=1, accept=True, model=None)
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)
        
        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__status=0)
                &(Q(order__start_time__range=(start_time, end_time))
                | Q(order__end_time__range=(start_time, end_time))))

        return queryset

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsStaffAdmin]
        else:
            permission_classes = [IsStaffSelf]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def self(self, request, pk=None):
        try:
            user = request.user.staff
        except Exception:
            return Response(status=401)
        
        staff = StaffSerializer(user)
        return Response(staff.data)

class CompanyViewSet(BaseModelViewSet):
    queryset = MainModel.Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    # filter_fields = '__all__'
    search_fields = '__all__'
    ordering_fields = '__all__'

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def company(self, request, pk=None):
        try:
            user = request.user.client
        except Exception:
            return Response(status=401)
        
        if user.company is not None:
            company = CompanySerializer(user.company, allow_null=True)
            return Response({'result':company.data})
        else :
            return Response({'result':None})
    
    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated])
    def unbind(self, request, pk=None):
        try:
            unbindUser = MainModel.Client.objects.get(pk=pk)
        except Exception:
            return Response(status=401)
        
        try:
            user = request.user.client
        except Exception:
            return Response(status=401)

        if user.company is not None:
            if user.company.admin is not None and user.company.admin.userId == user.userId:
                if user.company.admin.userId != unbindUser.userId:
                    unbindUser.company = None
                    unbindUser.save()
                    company = CompanySerializer(user.company)
                    return Response({'code': 0, 'result': company.data})
                else :
                    return Response({'code': 1, 'result': 'can not delete admin'})
            else :
                return Response({'code': 2, 'result': 'Authentication credentials were not provided.'})
        else :
            return Response({'code': 3, 'result': 'you dont have company'})

class ClientViewSet(BaseModelViewSet):
    queryset = MainModel.Client.objects.all()
    serializer_class = ClientSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    
    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def bind(self, request, pk=None):
        try:
            user = request.user.client
        except Exception:
            return Response(status=401)
          
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
                    return Response({'code': 2, 'result':'verify error'})
            except Exception:
                return Response({'code': 1, 'result':'name error'})

            client = ClientSerializer(user)
            return Response({'code': 0, 'result':client.data})
        else:
            return Response({'code': 3, 'result':'parameter error'})

class OrderViewSet(BaseModelViewSet):
    queryset = MainModel.Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = '__all__'
    search_fields = '__all__'
    ordering_fields = '__all__'

class StoreViewSet(BaseModelViewSet):
    queryset = MainModel.Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id']
    search_fields = '__all__'
    ordering_fields = '__all__'

class VehicleModelSellViewSet(BaseModelViewSet):
    queryset = MainModel.VehicleModel.objects.all()
    serializer_class = VehicleModelSellSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = ['model', 'name', 'seats']
    search_fields = '__all__'
    ordering_fields = '__all__'

    def get_queryset(self):
        queryset = MainModel.VehicleModel.objects.all()
        store = self.request.query_params.get('store', None)
        model = self.request.query_params.get('model', None)

        if store is not None:
            queryset = queryset.filter(store=store)
        
        if model is not None:
            queryset = queryset.filter(model=model)

        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)
        for item in queryset:
            if start_time is not None and end_time is not None:
                item.count = MainModel.Vehicle.objects.filter(model=item).exclude(Q(order__status=0)
                    & (Q(order__start_time__range=(start_time, end_time))
                    | Q(order__end_time__range=(start_time, end_time)))).count
        
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = VehicleModelSellSerializer(queryset, many=True)
        return Response(serializer.data)

class StaffModelViewSet(BaseModelViewSet):
    queryset = MainModel.Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = ['userId', 'driver', 'tourguide', 'status', 'accept', 'store', 'model__model']
    search_fields = '__all__'
    ordering_fields = '__all__' 

    def get_queryset(self):
        queryset = MainModel.Staff.objects.all().filter(status=1, accept=True).exclude(model=None)
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)
        
        if start_time is not None and end_time is not None:
            queryset = queryset.exclude(
                Q(order__status=0)
                &(Q(order__start_time__range=(start_time, end_time))
                | Q(order__end_time__range=(start_time, end_time))))

        return queryset


# class StaffSigup(views.APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         staff = StaffCreationForm(request.data)
#         if staff.is_valid():
#             staff.save()
#             return Response('ok')
#         return Response(staff.errors, status=400)

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

            return Response(StaffSerializer(staff).data)