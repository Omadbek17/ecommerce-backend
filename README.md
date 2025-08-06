# 🛒 E-commerce Backend API

Django REST API for E-commerce platform with location support.

## 🚀 Features

✅ **Authentication System:**
- User registration with phone number (+998 format)
- Token-based authentication  
- Location support (latitude/longitude)
- Profile management

✅ **Models Ready:**
- Categories (hierarchical structure)
- Products (with images, specifications)
- Orders (Cash, Payme, Click payments)
- Users with location data

✅ **API Documentation:**
- Swagger UI available
- OpenAPI 3.0 schema
- Interactive testing interface

## 🔗 API Endpoints

### Authentication:
- `POST /api/auth/register/` - User registration with location
- `POST /api/auth/login/` - User login
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update profile  
- `POST /api/auth/logout/` - Logout user

## 🧪 Testing

**Swagger Documentation:** `/api/docs/`

**Example Registration Request:**
```json
{
  "phone_number": "+998901234567",
  "first_name": "Test",
  "last_name": "User",
  "password": "test123456",
  "password_confirm": "test123456",
  "location": "Tashkent, Uzbekistan",
  "latitude": 41.2995,
  "longitude": 69.2401
}
```

**Example Login Request:**
```json
{
  "phone_number": "+998901234567",
  "password": "test123456"
}
```

## 🛠️ Local Setup

```bash
git clone https://github.com/Omadbek17/ecommerce-backend.git
cd ecommerce-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Admin Panel:** `http://127.0.0.1:8000/admin/`  
**API Docs:** `http://127.0.0.1:8000/api/docs/`

## 📱 Location Features

- HTML5 Geolocation API support
- Manual location selection on map
- Coordinate storage (latitude/longitude)  
- Address reverse geocoding
- OpenStreetMap integration

## 📊 Current Status

- ✅ **V1.0 - Authentication API** (Complete)
- 🚧 **V2.0 - Categories & Products API** (In Progress)
- ⏳ **V3.0 - Orders & Payment Integration** (Planned)

## 🗂️ Models Structure

### User
- Phone number (unique, UZ format)
- Name, location with coordinates
- Verification status

### Category  
- Hierarchical categories
- Image support, active status
- Product count tracking

### Product
- Title, seller code, price
- Stock management
- Multiple images and specifications
- Category association

### Order
- Payment methods (Cash, Payme, Click)
- Delivery information
- Order status tracking
- Items with pricing history

## 🛡️ Security Features

- Token-based authentication
- Phone number validation
- Password validation
- CORS configuration
- Admin panel protection

## 🌐 Tech Stack

- **Backend:** Django 4.2.7
- **API:** Django REST Framework 3.14.0
- **Documentation:** drf-spectacular (Swagger/OpenAPI)
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Authentication:** Token-based
- **Location:** HTML5 Geolocation + OpenStreetMap

---

**Created for E-commerce Platform** 🚀  
**Ready for frontend integration** ✨