from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse

from rest_framework import viewsets, generics, views
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_extensions.mixins import DetailSerializerMixin

from .permissions import *
from .serializers import *
from .models import *


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


class TaskViewSet(DetailSerializerMixin, viewsets.ModelViewSet, MixinPermissions):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    serializer_detail_class = TaskDetailSerializer


class GroupViewSet(viewsets.ModelViewSet, MixinPermissions):
    queryset = BaseGroup.objects.all()
    serializer_class = GroupSerializer

    def list(self, request):
        queryset = BaseGroup.objects.all()
        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)

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
