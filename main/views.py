from django.shortcuts import render
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.response import Response

from .permissions import IsAuthenticated, IsAdmin, IsStaff
from .serializers import StaffSerializer
from .models import *


class StaffViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Staff.objects.all()
        serializer = StaffSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Staff.objects.all()
        staff = get_object_or_404(queryset, pk=pk)
        serializer = StaffSerializer(staff)
        return Response(serializer.data)

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
