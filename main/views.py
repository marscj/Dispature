from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse

from rest_framework import viewsets, generics, views
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import list_route, api_view
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import (IsStaffSelf, IsStaffAdmin, IsAuthenticated, AllowAny)
from .serializers import (
    DLISerializer, StaffSerializer, StaffDetailSerializer,
    VehicleSerializer, VehicleDetailSerializer, TaskSerializer,
    TaskDetailSerializer, GroupSerializer, TLISerializer,
    DLISerializer, PPISerializer)
from .models import Staff, Vehicle, Task, BaseGroup, TLI, DLI, PPI
from .forms import StaffCreationForm


class MixinPermissions(views.APIView):

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsStaffAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class StaffViewSet(DetailSerializerMixin, viewsets.ModelViewSet):

    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    serializer_detail_class = StaffDetailSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'full_name', 'phone', 'status',
                     'is_driver', 'is_tourguide', 'is_operator']
    search_fields = '__all__'
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsStaffAdmin]
        else:
            permission_classes = [IsStaffSelf]
        return [permission() for permission in permission_classes]


class VehicleViewSet(DetailSerializerMixin, viewsets.ModelViewSet, MixinPermissions):

    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    serializer_detail_class = VehicleDetailSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'traffic_plate_no', 'model_name', 'model_year',
                     'num_of_pass', 'exp_date', 'policy_no', 'rate', 'status']
    search_fields = '__all__'
    ordering_fields = '__all__'


class TaskViewSet(DetailSerializerMixin, viewsets.ModelViewSet, MixinPermissions):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    serializer_detail_class = TaskDetailSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'create_time', 'start_time_in', 'end_time_in',
                     'vehicle', 'driver', 'tourguide', 'start_addr', 'end_addr', ]
    search_fields = '__all__'
    ordering_fields = '__all__'


class GroupViewSet(viewsets.ModelViewSet, MixinPermissions):

    queryset = BaseGroup.objects.all()
    serializer_class = GroupSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = '__all__'
    search_fields = '__all__'
    ordering_fields = '__all__'


class DLIViewSet(viewsets.ModelViewSet, MixinPermissions):

    queryset = DLI.objects.all()
    serializer_class = DLISerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = '__all__'
    search_fields = '__all__'
    ordering_fields = '__all__'


class TLIViewSet(viewsets.ModelViewSet, MixinPermissions):

    queryset = TLI.objects.all()
    serializer_class = TLISerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = '__all__'
    search_fields = '__all__'
    ordering_fields = '__all__'


class PPIViewSet(viewsets.ModelViewSet, MixinPermissions):

    queryset = PPI.objects.all()
    serializer_class = PPISerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = '__all__'
    search_fields = '__all__'
    ordering_fields = '__all__'


class StaffSigup(views.APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        staff = StaffCreationForm(request.data)
        if staff.is_valid():
            staff.save()
            return Response('ok')

        return Response(staff.errors, status=400)


# class StaffViewSet(viewsets.ViewSet, MixinPermissions):
#
#     def list(self, request):
#         queryset = Staff.objects.all()
#         serializer = StaffSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, pk=None):
#         try:
#             staff = Staff.objects.get(pk=pk)
#         except Staff.DoesNotExist:
#             raise Http404
#
#         serializer = StaffDetailSerializer(staff)
#         return Response(serializer.data)
