from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate
from rest_framework import viewsets
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import User, Service, ServiceVariant, RepairOrder, Location, Company, Brand, VehicleType, FuelType, Vehicle, ServiceType
from .serializers import (
    LoginSerializer, RegisterSerializer, UserSerializer, 
    VendorRegisterSerializer, CustomerRegisterSerializer, 
    ServiceSerializer, ServiceVariantSerializer, RepairOrderSerializer, OrderCreateSerializer,
    LocationSerializer, CompanySerializer, BrandSerializer, VehicleTypeSerializer, FuelTypeSerializer, VehicleSerializer, ServiceTypeSerializer
)

get_user_model = User   

def TokenGenerate(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = TokenGenerate(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(token['refresh']),
                'access': str(token['access']),
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorRegisterView(generics.CreateAPIView):
    serializer_class = VendorRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = TokenGenerate(user)
            return Response({
                'user': UserSerializer(user).data,
                'profile': user.vendor_profile.business_name,
                'refresh': str(token['refresh']),
                'access': str(token['access']),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerRegisterView(generics.CreateAPIView):
    serializer_class = CustomerRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = TokenGenerate(user)
            return Response({
                'user': UserSerializer(user).data,
                'profile': user.customer_profile.phone_number or 'Profile created',
                'refresh': str(token['refresh']),
                'access': str(token['access']),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = TokenGenerate(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(token['refresh']),
                'access': str(token['access']),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
            except (TokenError, InvalidToken, Exception):
                return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            tokens = OutstandingToken.objects.filter(user_id=user.id)
            for t in tokens:
                try:
                    BlacklistedToken.objects.get_or_create(token=t)
                except Exception:
                    pass
            return Response({"message": "Successfully logged out (all sessions)."}, status=status.HTTP_205_RESET_CONTENT)

        return Response({"error": "Refresh token required or authenticated user required."}, status=status.HTTP_400_BAD_REQUEST)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [AllowAny]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()   # ✅ REQUIRED
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'vendor':
            return Service.objects.filter(vendor=user.vendor_profile)
        return Service.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'vendor':
            raise serializers.ValidationError("Only vendors can create services.")
        serializer.save(vendor=user.vendor_profile)


class ServiceVariantViewSet(viewsets.ModelViewSet):
    queryset = ServiceVariant.objects.all()
    serializer_class = ServiceVariantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'vendor':
            return ServiceVariant.objects.filter(service__vendor=self.request.user.vendor_profile)
        return ServiceVariant.objects.none()

    def perform_create(self, serializer):
        service_id = self.request.data.get('service')
        service = get_object_or_404(Service, id=service_id, vendor=self.request.user.vendor_profile)
        serializer.save(service=service)


class RepairOrderViewSet(viewsets.ModelViewSet):
    queryset = RepairOrder.objects.all()
    serializer_class = RepairOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return RepairOrder.objects.filter(customer=user)
        elif user.role == 'vendor':
            return RepairOrder.objects.filter(vendor=user.vendor_profile)
        return RepairOrder.objects.none()
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        variant_id = serializer.validated_data['variant_id']
        try:
            variant = ServiceVariant.objects.select_related('service__vendor').get(pk=variant_id)
        except ServiceVariant.DoesNotExist:
            return Response({'detail': 'Service variant not found.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            variant.reserve_stock()
        except ServiceVariant.OutOfStock:
            return Response({'detail': 'Service variant out of stock.'}, status=status.HTTP_400_BAD_REQUEST)

        order = RepairOrder.objects.create(
            customer=user,
            vendor=variant.service.vendor,
            variant=variant,
            total_amount=variant.price,
        )

        data = RepairOrderSerializer(order).data
        return Response(data, status=status.HTTP_201_CREATED)