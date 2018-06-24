from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from django.urls import path

from main.admin import site
import main.views as View

router = DefaultRouter()
router.register(r'staffs', View.StaffViewSet, base_name='staff')
router.register(r'companys', View.CompanyViewSet, base_name='company')
router.register(r'orders', View.OrderViewSet, base_name='order')
router.register(r'stores', View.StoreViewSet, base_name='store')
router.register(r'specials', View.SpecialViewSet, base_name='special')
router.register(r'models', View.ModelViewSet, base_name='model')

urlpatterns = [
    # url(r'staffs/regist/', StaffSigup.as_view()),
    path('admin/', site.urls),
    url(r'upload/',View.UpLoadFile.as_view()),
    url(r'^token/', View.AuthToken.as_view()),
    url(r'^bind/', View.BindCompany.as_view()),
    url(r'^unbind/', View.UnBindCompany.as_view()),
] + router.urls
