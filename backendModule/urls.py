from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'locations', views.LocationViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'service-variants', views.ServiceVariantViewSet)
router.register(r'orders', views.RepairOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/vendor/', views.VendorRegisterView.as_view(), name='vendor_register'),
    path('register/customer/', views.CustomerRegisterView.as_view(), name='customer_register'),
    path('login/', views.LoginView.as_view(), name='login'),
]