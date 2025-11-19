# 📋 Rental Gear Flutter API - Quick Reference

## 🔗 Base URL
```
http://localhost:8000/rental_gear/api/flutter/
```

## 📌 Endpoints Cheat Sheet

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/gears/` | GET | ❌ | Get all gears |
| `/gears/<id>/` | GET | ❌ | Get gear detail |
| `/cart/` | GET | ✅ | Get cart |
| `/cart/add/` | POST | ✅ | Add to cart |
| `/cart/update/<id>/` | POST | ✅ | Update cart item |
| `/cart/remove/<id>/` | POST | ✅ | Remove from cart |
| `/checkout/` | POST | ✅ | Checkout |
| `/rentals/` | GET | ✅ | Rental history |
| `/seller/gears/` | GET | 👤 | Seller's gears |
| `/seller/gears/create/` | POST | 👤 | Create gear |
| `/seller/gears/<id>/update/` | POST | 👤 | Update gear |
| `/seller/gears/<id>/delete/` | POST | 👤 | Delete gear |

**Legend:** ❌ No Auth | ✅ Login Required | 👤 Seller Only

---

## 💾 Data Types Reference

```dart
// Gear
int id
String name, category, description, imageUrl, sellerUsername
double pricePerDay  // ⚠️ .toDouble()
int stock, sellerId
bool isFeatured

// CartItem
int id, gearId, quantity, days, stockAvailable
String gearName, gearImageUrl
double pricePerDay, subtotal  // ⚠️ .toDouble()

// Rental
int id
String customerName
DateTime rentalDate, returnDate  // ⚠️ DateTime.parse()
double totalCost  // ⚠️ .toDouble()
List<RentalItem> items
```

---

## 🎯 Common Requests

### Get All Gears
```dart
GET /gears/
No body, no auth
```

### Add to Cart
```dart
POST /cart/add/
Headers: Cookie: sessionid=xxx
Body: {
  "gear_id": 1,
  "quantity": 2,
  "days": 3
}
```

### Checkout
```dart
POST /checkout/
Headers: Cookie: sessionid=xxx
No body
```

### Create Gear (Seller)
```dart
POST /seller/gears/create/
Headers: Cookie: sessionid=xxx
Body: {
  "name": "Hockey Stick",
  "category": "hockey",
  "price_per_day": 50000.0,
  "stock": 10
}
```

---

## ⚠️ Validation Rules

| Field | Rule |
|-------|------|
| quantity | >= 1, <= stock |
| days | 1-30 |
| category | hockey, curling, ice_skating, apparel, accessories, protective_gear, other |
| price_per_day | > 0 |
| stock | >= 0 |

---

## 🔴 Error Codes

- `200` ✅ Success
- `400` ❌ Validation Error
- `401` 🔒 Auth Required
- `404` 🔍 Not Found
- `405` ⛔ Wrong Method
- `500` 💥 Server Error

---

## 🛠️ Flutter Integration

### 1. Service Call
```dart
final service = RentalGearService();
final gears = await service.getAllGears();
```

### 2. Model Conversion
```dart
List<Gear> gearList = gears
  .map((json) => Gear.fromJson(json))
  .toList();
```

### 3. Error Handling
```dart
try {
  final result = await service.checkout(cookie);
  if (result['success']) {
    // Success
  } else {
    // Show error: result['message']
  }
} catch (e) {
  // Handle exception
}
```

---

## 📝 Quick Test

```bash
# Test get gears
curl http://localhost:8000/rental_gear/api/flutter/gears/

# Test add to cart (need session_id)
curl -X POST http://localhost:8000/rental_gear/api/flutter/cart/add/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_ID" \
  -d '{"gear_id":1,"quantity":2,"days":3}'
```

---

## 📚 Documentation Files

1. **FLUTTER_API.md** - Full API docs
2. **FLUTTER_INTEGRATION.md** - Integration guide
3. **API_TEST_CASES.md** - Test examples
4. **flutter_models_example.dart** - Models
5. **flutter_service_example.dart** - Service

---

## 🚨 Common Mistakes

❌ `pricePerDay: json["price_per_day"]`
✅ `pricePerDay: json["price_per_day"].toDouble()`

❌ Forgot to send cookie for auth endpoints
✅ Always include `Cookie: sessionid=xxx` header

❌ Using GET for cart/add/
✅ Use POST for all mutations

---

**Happy Coding! 🎉**
