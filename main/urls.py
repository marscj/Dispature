from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from django.urls import path

from main.admin import site
import main.views as View

router = DefaultRouter()
router.register(r'staffs', View.StaffViewSet, base_name='staff')
router.register(r'orders', View.OrderViewSet, base_name='order')
router.register(r'stores', View.StoreViewSet, base_name='store')
router.register(r'specials', View.SpecialViewSet, base_name='special')
router.register(r'models', View.ModelViewSet, base_name='model')
router.register(r'account-detail', View.AccountDetailViewSet, base_name='model')

urlpatterns = [
    path('admin/', site.urls),
    url(r'upload/',View.UpLoadFile.as_view()),
    url(r'^signin/', View.SignInView.as_view()),
    url(r'^signup', View.ClientSignUp.as_view()),
    url(r'^reset-password/', View.ResetPassword.as_view()),
    url(r'^bind/', View.BindCompany.as_view()),
    url(r'^unbind/', View.UnBindCompany.as_view()),
    url(r'^company/', View.CompanyView.as_view()),
    url(r'^company-client/', View.CompanyClientView.as_view()),
    url(r'^settle/', View.SettlementView.as_view()),
] + router.urls
