from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse

from rest_framework import viewsets, generics, views
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import list_route, api_view, detail_route
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import (IsStaffSelf, IsStaffAdmin,IsAuthenticated, AllowAny, IsAdminOrIsSelf)
from .serializers import (DLISerializer, StaffSerializer,VehicleSerializer, TLISerializer,DLISerializer, PPISerializer)
from .models import Staff, Vehicle, TLI, DLI, PPI
from .forms import StaffCreationForm

from rest_framework.renderers import JSONRenderer


class Utf8JSONRenderer(JSONRenderer):
    charset = 'utf-8'


class BaseModelViewSet(viewsets.ModelViewSet, views.APIView):

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsStaffAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class StaffViewSet(viewsets.ModelViewSet):

    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
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

    @detail_route(methods=['post'], permission_classes=[IsAdminOrIsSelf])
    def upload_photo(self, request, pk=None):
        staff = request.user.staff
        return Response('ok')


class VehicleViewSet(BaseModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'traffic_plate_no', 'model_name', 'model_year',
                     'num_of_pass', 'exp_date', 'policy_no', 'rate', 'status']
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
