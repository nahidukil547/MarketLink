# MarketLink Project Documentation

## What This Project Does

Basically, it's a marketplace where:
- Vendors (like mechanics) can register and offer services (e.g., oil change, tire repair).
- Customers can sign up, browse services, and book orders.
- Everything is location-based, using divisions, districts, upazilas in Bangladesh.
- Vehicles are linked to brands, companies, etc.
- Orders reserve stock and handle payments later.

We use SQLite for DB

## Project Structure

- backendModule/: Main app with models, views, serializers, URLs.
- manage.py: Django's command runner.
- db.sqlite3: The database file.
- requirements.txt: Python packages needed.
- env/: Virtual environment folder.

Inside backendModule:
- models.py: All the data models (User, Service, Order, etc.).
- views.py: API views for handling requests.
- serializers.py: For converting data to/from JSON.
- urls.py: URL routing.
- migrations/: DB migration files.

## Key Models (Data Structures)

### User
- Basic user with username, email, role (admin/vendor/customer).
- Has profiles: VendorProfile or CustomerProfile.

### Location
- Bangladesh locations: Division -> District -> Upazila -> Area.
- Used for vendors' addresses.

### Company & Brand
- Companies like Toyota, brands like Corolla.

### Vehicle
- Cars with brand, model, etc. Company is optional now.

### Service & ServiceVariant
- Vendors create services (e.g., Oil Change), with variants (e.g., Basic, Premium) having price and stock.

### RepairOrder
- When customer books a variant, creates an order, reserves stock.

## APIs (Views)

All APIs are RESTful, using DRF ViewSets mostly.

### Auth APIs
- Register: POST /register/ - General user.
- Vendor Register: POST /register/vendor/ - For vendors.
- Customer Register: POST /register/customer/ - For customers.
- Login: POST /login/ - Get tokens.
- Logout: POST /logout/ - Blacklist refresh token.

### Data APIs
- Locations: GET/POST /locations/ - List/create locations.
- Vehicle : GET/POST /vehicles/ - Sedan, SUV, etc.
- Services: GET/POST /services/ - Vendors' services (filtered by vendor).
- Service Variants: GET/POST /service-variants/ - Variants under services.
- Vehicles: GET/POST /vehicles/ - Vehicle info.
- Orders: GET/POST /orders/ - Customers create orders, vendors/customers see theirs.

Permissions: Most need auth, vendors can only see/edit their stuff.

## Serializers

These handle JSON input/output:
- UserSerializer: User data.
- LocationSerializer: Nested division/district/upazila.
- VehicleSerializer: Nested brand/company, creates if needed.
- ServiceSerializer: With variants.
- RepairOrderSerializer: Order details.
- OrderCreateSerializer: Just variant_id for creating orders.

## URLs

In urls.py, we have router for ViewSets, plus custom auth paths.

## How to Run

1. Install Python 3.8+.
2. Create virtual env: `python -m venv env`
3. Activate: `env\Scripts\activate` (Windows) or `source env/bin/activate` (Linux/Mac).
4. Install deps: `pip install django djangorestframework djangorestframework-simplejwt`
5. Migrate DB: `python manage.py makemigrations` then `python manage.py migrate`
6. Run server: `python manage.py runserver`
7. API at http://127.0.0.1:8000/

## Notes

- JWT tokens: Access for auth, refresh for new access.
- Stock management: Orders reserve stock, if out, error.
- Bangladesh locations: Hardcoded divisions like Dhaka, etc.


## Candidates Thinks 
- Focus on core features: user auth, service management, order booking.
- My Strong part is Model Structure and Relationships.
- I am Not clear About the Payments System Or Vendor system That's why i can't implement integrations like (SSLCommerce, GooglePay, PathaoPa or Bkash).  

## Can Improvements in Future 
- Add payment integration.
- More detailed vendor profiles.
- Better error handling and validations.
- Location wise service.

## Contact
For questions, reach out 
to
- Email: nahidukil547@gmail.com
- Phone: +8801646695565
- GitHub: nahidukil547
