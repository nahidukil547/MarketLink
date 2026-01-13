from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    created_by = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_from = models.CharField(max_length=255, null=True, blank=True)
    modified_by = models.CharField(max_length=64, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_from = models.CharField(max_length=255, null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_by = models.CharField(max_length=64, null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_from = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username

    @property
    def is_vendor(self):
        return self.role == 'vendor'

    @property
    def is_customer(self):
        return self.role == 'customer'

class Division(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(BaseModel):
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='districts')

    def __str__(self):
        return f"{self.name} - {self.division.name}"


class Upazila(BaseModel):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='Upazilas')

    def __str__(self):
        return f"{self.name} - {self.district.name}"


class Location(BaseModel):
    division = models.ForeignKey(Division, on_delete=models.PROTECT)
    district = models.ForeignKey(District, on_delete=models.PROTECT)
    Upazila = models.ForeignKey(Upazila, on_delete=models.PROTECT)
    area = models.CharField(max_length=100)
    address_line = models.TextField()
    postal_code = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('Upazila', 'area', 'postal_code')

    def __str__(self):
        return f"{self.division.name} / {self.district.name} / {self.Upazila.name} - {self.area}"


class Company(BaseModel):
    name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Brand(BaseModel):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='brands')

    def __str__(self):
        return self.name


class VehicleType(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FuelType(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Vehicle(BaseModel):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, null=True, blank=True)
    engine_number = models.CharField(max_length=100, null=True, blank=True)
    chassis_number = models.CharField(max_length=100, null=True, blank=True)
    vehicle_number = models.CharField(max_length=100, null=True, blank=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    fuel_type = models.ForeignKey(FuelType, on_delete=models.PROTECT)
    capacity = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class VendorProfile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"


class CustomerProfile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

class ServiceType(BaseModel):   
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    


class Service(BaseModel):
    SERVICE_LEVEL_CHOICES = (
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('express', 'Express'),
    )
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, null=True, blank=True)
    service_level = models.CharField(max_length=20, choices=SERVICE_LEVEL_CHOICES, default='basic')

    def __str__(self):
        return f"{self.name} - {self.vendor.business_name}"


class ServiceVariant(BaseModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_minutes = models.PositiveIntegerField(default=60)
    stock = models.PositiveIntegerField(default=0, help_text="Number of simultaneous bookings available")

    class Meta:
        unique_together = ('service', 'name')

    def __str__(self):
        return f"{self.service.name} - {self.name} (${self.price})"

    class OutOfStock(Exception):
        pass

    def reserve_stock(self, qty: int = 1):
        if qty <= 0:
            return
        with transaction.atomic():
            updated = ServiceVariant.objects.filter(pk=self.pk, stock__gte=qty).update(stock=F('stock') - qty)
            if updated == 0:
                raise ServiceVariant.OutOfStock(f"Not enough stock for variant {self.pk}")
            self.refresh_from_db(fields=['stock'])

    def release_stock(self, qty: int = 1):
        if qty <= 0:
            return
        with transaction.atomic():
            ServiceVariant.objects.filter(pk=self.pk).update(stock=F('stock') + qty)
            self.refresh_from_db(fields=['stock'])


class RepairOrder(BaseModel):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    order_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='orders')
    variant = models.ForeignKey(ServiceVariant, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Order {self.order_id} - {self.status} - {self.total_amount}"

    def mark_paid(self, payment_reference: str = None):
        if self.status in {self.STATUS_PAID, self.STATUS_PROCESSING, self.STATUS_COMPLETED}:
            return
        self.payment_reference = payment_reference
        self.status = self.STATUS_PAID
        self.modified_at = timezone.now()
        self.save(update_fields=['payment_reference', 'status', 'modified_at'])


class PaymentEvent(BaseModel):
    event_id = models.CharField(max_length=255, unique=True)
    provider = models.CharField(max_length=50, help_text="e.g. stripe")
    payload = models.JSONField()
    related_order = models.ForeignKey(RepairOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_events')
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['event_id']),
            models.Index(fields=['provider']),
        ]

    def __str__(self):
        return f"{self.provider} evt {self.event_id} (processed={self.processed})"

    def mark_processed(self):
        if not self.processed:
            self.processed = True
            self.processed_at = timezone.now()
            self.save(update_fields=['processed', 'processed_at'])