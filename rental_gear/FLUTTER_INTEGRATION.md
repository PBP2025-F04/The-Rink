# Rental Gear - Flutter Integration Guide

## 📱 Panduan Lengkap Integrasi Flutter dengan Django Backend

### ✅ Yang Sudah Dibuat

1. **12 Flutter JSON Endpoints** dengan data types yang tepat
2. **Models Flutter** untuk semua response
3. **Service Class** untuk HTTP requests
4. **Dokumentasi API** lengkap dengan contoh

---

## 🎯 Fitur yang Tersedia

### Public Features (Tanpa Login)
- ✅ Lihat semua gear
- ✅ Lihat detail gear

### Customer Features (Login Required)
- ✅ Lihat keranjang
- ✅ Tambah item ke keranjang
- ✅ Update jumlah/durasi item di keranjang
- ✅ Hapus item dari keranjang
- ✅ Checkout
- ✅ Lihat riwayat rental

### Seller Features (Login as Seller)
- ✅ Lihat gear milik sendiri
- ✅ Buat gear baru
- ✅ Update gear
- ✅ Hapus gear

---

## 📊 Data Types Yang Digunakan

Setiap field sudah disesuaikan untuk kompatibilitas Flutter:

| Django Type | Python Type | Flutter Type | Conversion |
|-------------|-------------|--------------|------------|
| IntegerField | int | int | Direct |
| CharField | str | String | Direct |
| DecimalField | Decimal | double | `.toDouble()` |
| BooleanField | bool | bool | Direct |
| DateTimeField | datetime | DateTime | `DateTime.parse()` |
| ForeignKey | int (ID) | int | Direct |

### ⚠️ Penting untuk Decimal/Float

Django menggunakan `DecimalField` untuk harga. Di Flutter, **WAJIB** konversi ke `double`:

```dart
// ❌ SALAH - akan error
pricePerDay: json["price_per_day"],

// ✅ BENAR
pricePerDay: json["price_per_day"].toDouble(),
```

---

## 🔗 Endpoints Summary

### Base URL
```
http://localhost:8000/rental_gear/api/flutter/
```

### Endpoint List

| Method | Endpoint | Auth | Deskripsi |
|--------|----------|------|-----------|
| GET | `/gears/` | ❌ | Get all gears |
| GET | `/gears/<id>/` | ❌ | Get gear detail |
| GET | `/cart/` | ✅ | Get user cart |
| POST | `/cart/add/` | ✅ | Add to cart |
| POST | `/cart/update/<id>/` | ✅ | Update cart item |
| POST | `/cart/remove/<id>/` | ✅ | Remove from cart |
| POST | `/checkout/` | ✅ | Checkout cart |
| GET | `/rentals/` | ✅ | Get rental history |
| GET | `/seller/gears/` | ✅ (Seller) | Get seller's gears |
| POST | `/seller/gears/create/` | ✅ (Seller) | Create gear |
| POST | `/seller/gears/<id>/update/` | ✅ (Seller) | Update gear |
| POST | `/seller/gears/<id>/delete/` | ✅ (Seller) | Delete gear |

---

## 🚀 Quick Start - Flutter Integration

### 1. Setup Dependencies

Tambahkan di `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.1.0
  provider: ^6.1.0  # untuk state management (optional)
```

### 2. Copy Models

Copy file `flutter_models_example.dart` ke project Flutter Anda:
```
lib/models/rental_gear_models.dart
```

### 3. Copy Service

Copy file `flutter_service_example.dart` ke project Flutter:
```
lib/services/rental_gear_service.dart
```

### 4. Ubah Base URL

Di `rental_gear_service.dart`, ganti:
```dart
static const String baseUrl = 'http://YOUR_DJANGO_SERVER:8000/rental_gear/api/flutter';
```

---

## 💻 Contoh Penggunaan

### Get All Gears
```dart
final service = RentalGearService();
final gears = await service.getAllGears();

// Convert to model
List<Gear> gearList = gears.map((json) => Gear.fromJson(json)).toList();
```

### Add to Cart
```dart
final result = await service.addToCart(
  gearId: 5,
  quantity: 2,
  days: 3,
  cookie: userCookie,
);

if (result['success']) {
  print('Success: ${result['message']}');
} else {
  print('Error: ${result['message']}');
}
```

### Checkout
```dart
final result = await service.checkout(userCookie);

if (result['success']) {
  CheckoutResponse checkout = CheckoutResponse.fromJson(result);
  print('Total: Rp ${checkout.totalCost}');
  print('Return date: ${checkout.returnDate}');
}
```

---

## 🔐 Authentication

Endpoints yang butuh authentication menggunakan **cookie-based auth** dari Django.

### Cara Mendapat Cookie

Setelah login berhasil di Django, ambil cookie dari response header:

```dart
// Contoh login request
final response = await http.post(
  Uri.parse('http://your-server/auth/login/'),
  body: {'username': username, 'password': password},
);

// Ambil cookie dari response headers
String? rawCookie = response.headers['set-cookie'];
if (rawCookie != null) {
  int index = rawCookie.indexOf(';');
  String cookie = (index == -1) ? rawCookie : rawCookie.substring(0, index);
  // Simpan cookie ini untuk request berikutnya
}
```

---

## 🧪 Testing Endpoints

### Menggunakan Django Server

1. Jalankan Django server:
```bash
python manage.py runserver
```

2. Test dengan browser atau Postman:
```
GET http://localhost:8000/rental_gear/api/flutter/gears/
```

### Menggunakan Flutter

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

## 📝 Response Format

Semua response mengikuti format standar:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description"
}
```

---

## ⚙️ Validasi & Error Handling

### Validasi Input

#### Add to Cart
- `quantity`: harus >= 1 dan <= stock
- `days`: harus 1-30

#### Create/Update Gear (Seller)
- `category`: harus salah satu dari: hockey, curling, ice_skating, apparel, accessories, protective_gear, other
- `price_per_day`: harus > 0
- `stock`: harus >= 0

### Error Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 401 | Authentication required |
| 404 | Not found |
| 405 | Method not allowed |
| 500 | Server error |

---

## 🔄 Stock Management

Stock otomatis akan berkurang saat checkout berhasil:

```python
# Di backend, saat checkout:
for item in cart_items:
    item.gear.stock -= item.quantity
    item.gear.save()
```

Pastikan check stock sebelum checkout di Flutter:
```dart
if (cartItem.quantity > cartItem.stockAvailable) {
  // Show error: "Insufficient stock"
}
```

---

## 📱 UI Recommendations

### Gear List
- Tampilkan: name, category, price_per_day, image_url
- Filter by category
- Show stock status

### Cart
- Tampilkan subtotal per item
- Allow update quantity/days
- Show total price
- Disable checkout jika cart kosong

### Checkout Success
- Show rental_id
- Show return_date
- List semua items
- Total cost

### Seller Dashboard
- List gears milik seller
- CRUD operations
- Show stock levels

---

## 🐛 Common Issues & Solutions

### Issue 1: Type Conversion Error
**Problem:** `type 'int' is not a subtype of type 'double'`

**Solution:** Gunakan `.toDouble()` untuk semua decimal fields
```dart
pricePerDay: json["price_per_day"].toDouble()
```

### Issue 2: Null Values
**Problem:** `Null check operator used on a null value`

**Solution:** Gunakan null-safe operator atau default value
```dart
description: json["description"] ?? ""
imageUrl: json["image_url"] ?? ""
```

### Issue 3: Date Parsing Error
**Problem:** Error parsing ISO date strings

**Solution:** Gunakan DateTime.parse()
```dart
rentalDate: DateTime.parse(json["rental_date"])
```

### Issue 4: Authentication Failed
**Problem:** 401 Unauthorized

**Solution:** 
- Pastikan cookie valid
- Check apakah user sudah login
- Pastikan cookie disimpan dengan benar

---

## 📚 File Structure Recommendation

```
lib/
├── models/
│   └── rental_gear_models.dart
├── services/
│   └── rental_gear_service.dart
├── screens/
│   ├── gear_list_screen.dart
│   ├── gear_detail_screen.dart
│   ├── cart_screen.dart
│   ├── checkout_screen.dart
│   └── rental_history_screen.dart
└── widgets/
    ├── gear_card.dart
    └── cart_item_card.dart
```

---

## 🔍 Debug Tips

### Enable Logging
```dart
void debugResponse(http.Response response) {
  print('Status: ${response.statusCode}');
  print('Headers: ${response.headers}');
  print('Body: ${response.body}');
}
```

### Check JSON Structure
```dart
try {
  final data = jsonDecode(response.body);
  print('Keys: ${data.keys}');
} catch (e) {
  print('Invalid JSON: ${response.body}');
}
```

---

## 📞 Support

Jika ada masalah atau pertanyaan:

1. Check dokumentasi API di `FLUTTER_API.md`
2. Review contoh models di `flutter_models_example.dart`
3. Review contoh service di `flutter_service_example.dart`
4. Test endpoints dengan Postman terlebih dahulu

---

## ✨ Next Steps

1. ✅ Baca dokumentasi API (`FLUTTER_API.md`)
2. ✅ Copy models dan service ke project Flutter
3. ✅ Test endpoints dengan Postman
4. ✅ Implement di Flutter app
5. ✅ Handle authentication
6. ✅ Build UI
7. ✅ Test end-to-end

---

**Happy Coding! 🚀**
