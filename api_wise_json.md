
---

Operation name: Register (generic user)
url: /register/
method: POST
Json
{
  "username": "alice",
  "email": "alice@example.com",
  "first_name": "Alice",
  "last_name": "Smith",
  "role": "customer",
  "password": "Str0ngP@ssw0rd",
  "password_confirm": "Str0ngP@ssw0rd"
}


---

Operation name: Register Vendor
url: /register/vendor/
method: POST
Json
{
  "username": "vendorjoe",
  "email": "joe@vendor.example",
  "first_name": "Joe",
  "last_name": "Vendor",       
  "password": "VendorPass123!",
  "password_confirm": "VendorPass123!",
  "business_name": "Joe's Garage",
  "address": "123 Market St",   
  "location": 1       
}

---

Operation name: Register Customer
url: /register/customer/
method: POST
Json
{
  "username": "cust01",
  "email": "cust01@example.com",
  "first_name": "Cathy",
  "last_name": "Buyer", 
  "password": "CustPass2026$",
  "password_confirm": "CustPass2026$",
  "phone_number": "+15551234567",
  "address": "45 Elm St",
  "date_of_birth": "1990-05-12"
}

---

Operation name: Login
url: /login/
method: POST
Json
{
  "username": "alice",
  "password": "Str0ngP@ssw0rd"
}


---

Operation name: Logout
url: /logout/
method: POST
Json
{
  "refresh": "<refresh_token>"
}


---

Operation name: Create Location
url: /locations/
method: POST
Json
{
  "division": "Dhaka",
  "district": "Dhaka",
  "upazila": "Dhanmondi",
  "area": "Dhanmondi",
  "address_line": "House 1, Road 2",
  "postal_code": "1209",
  "latitude": 23.75,
  "longitude": 90.38,
  "is_active": true
}

---
Operation name: Create Vehicle
url: /vehicles/
method: POST
Json
{
  "name": "My Car",
  "brand": { "id": 1 }, 
  "company": { "id": 1 },
  "model": "2021",
  "serial_number": "SN123",
  "engine_number": "EN123",
  "chassis_number": "CH123",
  "vehicle_number": "V-100",
  "vehicle_type": { "id": 1 },
  "fuel_type": { "id": 1 },
  "capacity": "2000cc",
  "color": "White",
  "status": "active"
}

---

Operation name: Create Service (vendors only)
url: /services/
method: POST
Json
{
  "name": "Basic Oil Change",
  "description": "Engine oil change + filter",
  "service_type": 1,
  "service_level": "basic"
}

---

Operation name: List Service Variants
url: /service-variants/
method: GET
Auth: vendor for creation; listing may be public/Authenticated
Json Response (200)
[ { "id": 1, "service": 6, "name":"Standard", "price":"29.99", "estimated_minutes":60, "stock":5 } ]

Operation name: Create Service Variant (vendor owns service)
url: /service-variants/
method: POST
Json
{
  "service": 5,
  "name": "Standard Package",
  "price": 1500,
  "estimated_minutes": 60,
  "stock": 10
}

---

Operation name: List Orders
url: /orders/
method: GET
Auth: Bearer access_token
Json Response (200)
[ { "id": 1, "order_id": "uuid", "customer":"alice", "vendor":"Joe's Garage", "variant": { "id":1, "name":"Standard" }, "status":"pending", "total_amount":"29.99", "created_at":"2026-01-13T..." } ]

Operation name: Create Order (customers only)
url: /orders/
method: POST
Auth: Bearer access_token (customer)
Json
{
  "id": 25,
  "order_id": "ORD-2026-00025",
  "customer": "nahid@example.com",
  "vendor": "FastFix Services",
  "variant": 1,
  "status": "pending",
  "total_amount": 2500,
  "payment_reference": null,
  "created_at": "2026-01-13T14:20:10Z",
  "modified_at": "2026-01-13T14:20:10Z"
}
---

Notes:
- Authentication: include header `Authorization: Bearer <access>` for protected endpoints.
- Vendor-only actions: creating `services` and `service-variants` require the authenticated user to have `role: "vendor"`.
- Stock: creating an order calls `ServiceVariant.reserve_stock()` and will fail with 400 if out of stock.
- For nested objects (brand/company/vehicle types/fuel types), you can pass an existing `id` or a nested object; serializers will create or fetch as needed.

---

Resources quick list:
- `/locations/`
- `/services/`
- `/service-variants/`
- `/orders/`
