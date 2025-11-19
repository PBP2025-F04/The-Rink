# 🏒 Rental Gear - Flutter API Integration

Django REST API untuk aplikasi rental gear skating equipment dengan full support untuk Flutter mobile app.

## 📱 Flutter Integration Ready!

Aplikasi ini sudah dilengkapi dengan **12 JSON endpoints** yang siap digunakan dengan Flutter, dengan **data types yang sudah disesuaikan** untuk menghindari error saat integrasi.

---

## 📚 Dokumentasi Lengkap

### 🎯 Start Here!

1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick cheat sheet untuk semua endpoints
2. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Summary lengkap apa yang sudah dibuat

### 📖 Detailed Documentation

3. **[FLUTTER_API.md](FLUTTER_API.md)** - Complete API documentation dengan examples
4. **[FLUTTER_INTEGRATION.md](FLUTTER_INTEGRATION.md)** - Step-by-step integration guide
5. **[API_TEST_CASES.md](API_TEST_CASES.md)** - Test cases dan examples

### 💻 Flutter Code Examples

6. **[flutter_models_example.dart](flutter_models_example.dart)** - Flutter model classes
7. **[flutter_service_example.dart](flutter_service_example.dart)** - Flutter service class

---

## 🚀 Quick Start

### Django Backend

```bash
# Jalankan server
python manage.py runserver

# Test endpoint
curl http://localhost:8000/rental_gear/api/flutter/gears/
```

### Flutter Integration

```dart
// 1. Copy flutter_models_example.dart ke lib/models/
// 2. Copy flutter_service_example.dart ke lib/services/
// 3. Update baseUrl di service

final service = RentalGearService();
final gears = await service.getAllGears();
```

---

## 🎯 Fitur Utama

### Public Features (No Login)
- ✅ Lihat semua gear
- ✅ Lihat detail gear

### Customer Features (Login Required)
- ✅ Kelola keranjang (add, update, remove)
- ✅ Checkout
- ✅ Lihat riwayat rental

### Seller Features (Seller Login)
- ✅ CRUD gear (create, read, update, delete)
- ✅ Kelola inventory

---

## 📊 Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/flutter/gears/` | GET | ❌ | Get all gears |
| `/api/flutter/gears/<id>/` | GET | ❌ | Get gear detail |
| `/api/flutter/cart/` | GET | ✅ | Get cart |
| `/api/flutter/cart/add/` | POST | ✅ | Add to cart |
| `/api/flutter/cart/update/<id>/` | POST | ✅ | Update cart |
| `/api/flutter/cart/remove/<id>/` | POST | ✅ | Remove from cart |
| `/api/flutter/checkout/` | POST | ✅ | Checkout |
| `/api/flutter/rentals/` | GET | ✅ | Rental history |
| `/api/flutter/seller/gears/` | GET | 👤 | Seller's gears |
| `/api/flutter/seller/gears/create/` | POST | 👤 | Create gear |
| `/api/flutter/seller/gears/<id>/update/` | POST | 👤 | Update gear |
| `/api/flutter/seller/gears/<id>/delete/` | POST | 👤 | Delete gear |

**Legend:** ❌ No Auth | ✅ Login Required | 👤 Seller Only

---

## ⚠️ Data Types - PENTING!

Semua endpoints sudah menggunakan **data types yang benar** untuk Flutter:

```dart
// ✅ BENAR - Decimal fields di-convert ke double
pricePerDay: json["price_per_day"].toDouble()
totalCost: json["total_cost"].toDouble()

// ✅ BENAR - Date fields di-parse
rentalDate: DateTime.parse(json["rental_date"])

// ✅ BENAR - Nullable fields dengan default
description: json["description"] ?? ""
imageUrl: json["image_url"] ?? ""
```

**Lihat [FLUTTER_INTEGRATION.md](FLUTTER_INTEGRATION.md) untuk detail lengkap!**

---

## 🔧 Technology Stack

- **Backend:** Django 4.x
- **API Format:** JSON REST
- **Authentication:** Cookie-based (Django sessions)
- **CSRF:** Exempt untuk Flutter endpoints
- **Database:** SQLite (development) / PostgreSQL (production)

---

## 📁 File Structure

```
rental_gear/
├── views.py                        # 12 Flutter JSON endpoints
├── urls.py                         # URL routing
├── models.py                       # Database models
├── forms.py                        # Django forms
├── FLUTTER_API.md                  # API documentation
├── FLUTTER_INTEGRATION.md          # Integration guide
├── IMPLEMENTATION_SUMMARY.md       # Summary
├── QUICK_REFERENCE.md             # Quick cheat sheet
├── API_TEST_CASES.md              # Test cases
├── flutter_models_example.dart    # Flutter models
└── flutter_service_example.dart   # Flutter service
```

---

## 🧪 Testing

### Manual Testing dengan curl
```bash
# Get all gears
curl http://localhost:8000/rental_gear/api/flutter/gears/

# Add to cart (need session_id)
curl -X POST http://localhost:8000/rental_gear/api/flutter/cart/add/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{"gear_id":1,"quantity":2,"days":3}'
```

### Testing dengan Postman
Import collection dari [API_TEST_CASES.md](API_TEST_CASES.md)

### Testing dengan Flutter
```dart
void testGetGears() async {
  final service = RentalGearService();
  try {
    final gears = await service.getAllGears();
    print('✅ Success: Found ${gears.length} gears');
  } catch (e) {
    print('❌ Error: $e');
  }
}
```

---

## 📋 Models

### Gear
- name, category, description, image_url
- price_per_day (Decimal → double)
- stock, seller
- is_featured

### CartItem
- user, gear
- quantity, days
- Calculated: subtotal

### Rental
- customer_name, user
- rental_date, return_date
- total_cost

### RentalItem
- rental, gear_name
- quantity, price_per_day_at_checkout
- Calculated: subtotal

---

## 🔐 Authentication

Gunakan cookie-based authentication dari Django:

```dart
// Setelah login, simpan cookie
String cookie = 'sessionid=your_session_id';

// Gunakan untuk request yang butuh auth
final result = await service.addToCart(
  gearId: 1,
  quantity: 2,
  days: 3,
  cookie: cookie,
);
```

---

## ✅ Validation Rules

- **quantity:** >= 1, <= stock available
- **days:** 1-30 hari
- **category:** hockey, curling, ice_skating, apparel, accessories, protective_gear, other
- **price_per_day:** > 0
- **stock:** >= 0

---

## 🎨 Features

### Implemented
- ✅ Full CRUD untuk gear (seller)
- ✅ Cart management
- ✅ Checkout dengan stock reduction
- ✅ Rental history
- ✅ Authentication & authorization
- ✅ Input validation
- ✅ Error handling
- ✅ Proper data types untuk Flutter

### Security
- ✅ User authentication
- ✅ Seller authorization
- ✅ Stock validation
- ✅ Input sanitization
- ✅ CSRF protection (exempt for Flutter endpoints)

---

## 🐛 Troubleshooting

Lihat [FLUTTER_INTEGRATION.md](FLUTTER_INTEGRATION.md) section "Common Issues & Solutions" untuk:
- Type conversion errors
- Null value errors
- Date parsing errors
- Authentication errors

---

## 📞 Support

Untuk bantuan lengkap, baca dokumentasi sesuai kebutuhan:

1. Mau cepat? → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. Mau overview? → [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
3. Mau detail API? → [FLUTTER_API.md](FLUTTER_API.md)
4. Mau integrate? → [FLUTTER_INTEGRATION.md](FLUTTER_INTEGRATION.md)
5. Mau test? → [API_TEST_CASES.md](API_TEST_CASES.md)

---

## 🎯 Next Steps

1. ✅ Jalankan Django server
2. ✅ Test endpoints dengan curl/Postman
3. ✅ Copy Flutter models & service ke project
4. ✅ Implement authentication
5. ✅ Build Flutter UI
6. ✅ Test end-to-end

---

## 📄 License

Part of The-Rink project.

---

**Ready untuk integrasi dengan Flutter! 🚀**

Baca [FLUTTER_INTEGRATION.md](FLUTTER_INTEGRATION.md) untuk memulai.
