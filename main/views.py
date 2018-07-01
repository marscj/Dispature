from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate

from rest_framework import views, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework import authentication, permissions
import rest_framework.filters as filters

from django_filters.rest_framework import DjangoFilterBackend

from main.view_helper import ViewHelper
import main.models as MainModel
import main.serializers as MainSerializers

class Utf8JSONRenderer(JSONRenderer):
    charset = 'utf-8'

class LogInView(ObtainAuthToken):
    renderer_classes = (Utf8JSONRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})

        serializer.is_valid(raise_exception=True)
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
                user.set_password(newPassword)
                user.save()
                return Response({'code': 0, 'result':'ok'})
            
        return Response({'code': 1, 'result':'error'})

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
                    return Response({'code': 2, 'result':'verify error'})
            except Exception:
                return Response({'code': 1, 'result':'name error'})

            client = MainSerializers.CompanySerializer(company)
            return Response({'code': 0, 'result': client.data})
        else:
            return Response({'code': 3, 'result':'parameter error'})

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
                    return Response({'code': 0, 'result': company.data})
                else :
                    return Response({'code': 1, 'result': 'can not delete admin'})
            else :
                return Response({'code': 2, 'result': 'Authentication credentials were not provided.'})
        else :
            return Response({'code': 3, 'result': 'you dont have company'})

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
            return Response({'result': company.data})
        else :
            return Response({'result': None})

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
            return Response({'result': client.data})
        else :
            return Response({'result': None})

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

            return Response(MainSerializers.StaffSerializer(staff).data)