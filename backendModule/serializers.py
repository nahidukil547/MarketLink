from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, VendorProfile, CustomerProfile, Location, Service,\
    ServiceVariant, RepairOrder, VendorProfile, PaymentEvent, ServiceType, Company, Brand, VehicleType, FuelType, Vehicle,\
    Division, District, Upazila
from django.utils import timezone


get_user_model = User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class VendorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = VendorProfile
        fields = ['id', 'user', 'business_name', 'address', 'is_active']


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'phone_number', 'address', 'date_of_birth', 'is_active']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                data['user'] = user
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include username and password.')
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Passwords do not match.')
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return super().create(validated_data)


class VendorRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    business_name = serializers.CharField()
    address = serializers.CharField(required=False)
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), required=False)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Passwords do not match.')
        return data

    def create(self, validated_data):
        profile_data = {
            'business_name': validated_data.pop('business_name'),
            'address': validated_data.pop('address', None),
            'location': validated_data.pop('location', None),
        }
        validated_data.pop('password_confirm')
        validated_data['role'] = 'vendor'
        user = User.objects.create_user(**validated_data)
        VendorProfile.objects.create(user=user, **profile_data)
        return user


class CustomerRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Passwords do not match.')
        return data

    def create(self, validated_data):
        profile_data = {
            'phone_number': validated_data.pop('phone_number', None),
            'address': validated_data.pop('address', None),
            'date_of_birth': validated_data.pop('date_of_birth', None),
        }
        validated_data.pop('password_confirm')
        validated_data['role'] = 'customer'
        user = User.objects.create_user(**validated_data)
        CustomerProfile.objects.create(user=user, **profile_data)
        return user




class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ['name']

class DistrictSerializer(serializers.ModelSerializer):
    division = DivisionSerializer()
    class Meta:
        model = District
        fields = ['name', 'division']

class UpazilaSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()
    class Meta:
        model = Upazila
        fields = ['name', 'district']

class LocationSerializer(serializers.ModelSerializer):
    division = serializers.CharField(write_only=True)
    district = serializers.CharField(write_only=True)
    upazila = serializers.CharField(write_only=True)

    division_name = serializers.CharField(source='division.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    upazila_name = serializers.CharField(source='upazila.name', read_only=True)

    class Meta:
        model = Location
        fields = [
            'id',
            'division',
            'district',
            'upazila',
            'division_name',
            'district_name',
            'upazila_name',
            'area',
            'address_line',
            'postal_code',
            'latitude',
            'longitude',
            'is_active'
        ]
    def validate(self, data):
        if not data['division'] or not data['district'] or not data['upazila']:
            raise serializers.ValidationError("Division, District, and Upazila are required")
        return data

    def create(self, validated_data):
        division_name = validated_data.pop('division')
        district_name = validated_data.pop('district')
        upazila_name = validated_data.pop('upazila')

        division, _ = Division.objects.get_or_create(
            name=division_name
        )

        district, _ = District.objects.get_or_create(
            name=district_name,
            division=division
        )

        upazila, _ = Upazila.objects.get_or_create(
            name=upazila_name,
            district=district
        )

        return Location.objects.create(
            division=division,
            district=district,
            Upazila=upazila,
            **validated_data
        )
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == 'division':
                division_name = value
                division, _ = Division.objects.get_or_create(
                    name=division_name
                )
                instance.division = division
            elif key == 'district':
                district_name = value
                district, _ = District.objects.get_or_create(
                    name=district_name,
                    division=instance.division
                )
                instance.district = district
            elif key == 'upazila':
                upazila_name = value
                upazila, _ = Upazila.objects.get_or_create(
                    name=upazila_name,
                    district=instance.district
                )
                instance.upazila = upazila
            else:
                setattr(instance, key, value)
        instance.save()
        return instance

class CompanySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Company
        fields = ["id", "name", "nationality"]


class BrandSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    company = CompanySerializer()

    class Meta:
        model = Brand
        fields = ["id", "name", "company"]


class VehicleTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = VehicleType
        fields = ["id", "name"]


class FuelTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = FuelType
        fields = ["id", "name"]

class VehicleSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    vehicle_type = VehicleTypeSerializer()
    fuel_type = FuelTypeSerializer()
    company = CompanySerializer(required=False)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "name",
            "brand",
            "company",
            "model",
            "serial_number",
            "engine_number",
            "chassis_number",
            "vehicle_number",
            "vehicle_type",
            "fuel_type",
            "capacity",
            "color",
            "status",
        ]

    def _get_or_create_company(self, data):
        if not data:
            return None
        if "id" in data:
            return Company.objects.get(pk=data["id"])
        else:
            obj, _ = Company.objects.get_or_create(
                name=data.get("name"),
                defaults={"nationality": data.get("nationality")},
            )
        return obj

    def _get_or_create_brand(self, data, company):
        if "id" in data:
            return Brand.objects.get(pk=data["id"])
        else:
            name = data.get("name")
            obj, _ = Brand.objects.get_or_create(name=name, company=company)
        return obj

    def _get_or_create_by_name(self, model, data):
        if "id" in data:
            return model.objects.get(pk=data["id"])
        
        name = data.get("name")

        obj, _ = model.objects.get_or_create(name=name)
        return obj

    def create(self, validated_data):
        brand_data = validated_data.pop("brand")
        vehicle_type_data = validated_data.pop("vehicle_type")
        fuel_type_data = validated_data.pop("fuel_type")
        company_data = validated_data.pop("company", None)

        top_company = self._get_or_create_company(company_data) if company_data else None
        brand_company_data = brand_data.get("company")

        if brand_company_data:

            brand_company = self._get_or_create_company(brand_company_data)


        else:
            if top_company:
                brand_company = top_company
            else:
                raise serializers.ValidationError(
                    {"brand": "brand.company must be provided (or vehicle.company at top level)."}
                )

        brand = self._get_or_create_brand(brand_data, brand_company)
        vehicle_type = self._get_or_create_by_name(VehicleType, vehicle_type_data)
        
        fuel_type = self._get_or_create_by_name(FuelType, fuel_type_data)

        vehicle_company = top_company or brand_company

        vehicle = Vehicle.objects.create(
            brand=brand,
            company=vehicle_company,
            vehicle_type=vehicle_type,
            fuel_type=fuel_type,
            **validated_data,
        )
        return vehicle

    def update(self, instance, validated_data):
        brand_data = validated_data.pop("brand", None)
        vehicle_type_data = validated_data.pop("vehicle_type", None)
        fuel_type_data = validated_data.pop("fuel_type", None)
        company_data = validated_data.pop("company", None)

        if company_data:
            company = self._get_or_create_company(company_data)
            instance.company = company

        if brand_data:
            brand_company_data = brand_data.get("company")
            if brand_company_data:
                brand_company = self._get_or_create_company(brand_company_data)
            else:
                brand_company = instance.brand.company
            brand = self._get_or_create_brand(brand_data, brand_company)
            instance.brand = brand
            instance.company = brand_company 

        if vehicle_type_data:
            instance.vehicle_type = self._get_or_create_by_name(VehicleType, vehicle_type_data)

        if fuel_type_data:
            instance.fuel_type = self._get_or_create_by_name(FuelType, fuel_type_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class ServiceVariantSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), write_only=True)

    class Meta:
        model = ServiceVariant
        fields = [
            "id",
            "service",
            "name",
            "price",
            "estimated_minutes",
            "stock",
        ]

    def get_service_detail(self, obj):
        if not obj or not getattr(obj, "service", None):
            return None
        return {"id": obj.service.id, "name": obj.service.name}

    def validate(self, data):
        service = data.get("service") or getattr(self.instance, "service", None)
        name = data.get("name") or getattr(self.instance, "name", None)

        if not service:
            raise serializers.ValidationError({"service": "Service must be provided."})

        if not name:
            raise serializers.ValidationError({"name": "Variant name must be provided."})

        qs = ServiceVariant.objects.filter(service=service, name__iexact=name)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"name": "A variant with this name already exists for the given service."}
            )

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class ServiceTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ServiceType
        fields = ["id", "name", "description"]


class ServiceSerializer(serializers.ModelSerializer):
    service_type = ServiceTypeSerializer(required=False, allow_null=True)
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "vendor",
            "name",
            "description",
            "service_type",
            "service_level",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["id", "vendor", "created_at", "modified_at"]

    def _get_or_create_service_type(self, data):
        if data is None:
            return None
        if "id" in data:
            try:
                return ServiceType.objects.get(pk=data["id"])
            except ServiceType.DoesNotExist:
                raise serializers.ValidationError({"service_type": f"ServiceType with id={data['id']} does not exist."})

        name = data.get("name")
        if not name:

            raise serializers.ValidationError({"service_type": "Provide either id or name for service_type."})
        else:
            obj, _ = ServiceType.objects.get_or_create(name=name, defaults={"description": data.get("description")})
        return obj

    def create(self, validated_data):
        service_type_data = validated_data.pop("service_type", None)
        service_type = self._get_or_create_service_type(service_type_data)
        service = Service.objects.create(service_type=service_type, **validated_data)
        return service

    def update(self, instance, validated_data):
        service_type_data = validated_data.pop("service_type", serializers.empty)
        if service_type_data is not serializers.empty:

            if service_type_data is None:
                instance.service_type = None
            else:
                instance.service_type = self._get_or_create_service_type(service_type_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RepairOrderSerializer(serializers.ModelSerializer):
    variant = ServiceVariantSerializer(read_only=True)
    customer = serializers.StringRelatedField(read_only=True)
    vendor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = RepairOrder
        fields = ['id', 'order_id', 'customer', 'vendor', 'variant', 'status', 'total_amount', 'payment_reference', 'created_at', 'modified_at']
        read_only_fields = ['order_id', 'status', 'total_amount', 'payment_reference', 'created_at', 'modified_at']


class OrderCreateSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()

    def validate_variant_id(self, value):
        try:
            variant = ServiceVariant.objects.select_related('service__vendor').get(pk=value)
        except ServiceVariant.DoesNotExist:
            raise serializers.ValidationError("ServiceVariant not found.")
        if not variant.service.vendor.is_active:
            raise serializers.ValidationError("Vendor is not active.")
        return value

    def create(self, validated_data):
        raise NotImplementedError("Order creation is handled inside the view.")