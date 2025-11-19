# Rental Gear - Flutter API Documentation

## Base URL
```
http://localhost:8000/rental_gear/api/flutter/
```

## Data Types Reference
Berikut adalah data types yang digunakan dalam setiap field:

### Gear Model
- `id`: **int** - Primary key
- `name`: **String** - Nama gear
- `category`: **String** - Kategori (hockey, curling, ice_skating, apparel, accessories, protective_gear, other)
- `price_per_day`: **double** - Harga per hari (Decimal di Django → double di Flutter)
- `stock`: **int** - Jumlah stok tersedia
- `description`: **String** - Deskripsi gear
- `image_url`: **String** - URL gambar
- `seller_id`: **int** - ID seller
- `seller_username`: **String** - Username seller
- `is_featured`: **bool** - Status featured

### CartItem Model
- `id`: **int** - Primary key
- `gear_id`: **int** - ID gear
- `gear_name`: **String** - Nama gear
- `gear_image_url`: **String** - URL gambar gear
- `price_per_day`: **double** - Harga per hari
- `quantity`: **int** - Jumlah item
- `days`: **int** - Durasi rental (hari)
- `subtotal`: **double** - Total harga (price_per_day × quantity × days)
- `stock_available`: **int** - Stok tersedia

### Rental Model
- `id`: **int** - Primary key
- `customer_name`: **String** - Nama customer
- `rental_date`: **String** (ISO 8601) - Tanggal rental
- `return_date`: **String** (ISO 8601) - Tanggal pengembalian
- `total_cost`: **double** - Total biaya
- `items`: **List<RentalItem>** - List item yang dirental

### RentalItem Model
- `gear_name`: **String** - Nama gear
- `quantity`: **int** - Jumlah
- `price_per_day`: **double** - Harga per hari saat checkout
- `subtotal`: **double** - Subtotal item

---

## Endpoints

### 1. Get All Gears
**Endpoint:** `GET /gears/`

**Authentication:** Not required

**Response:**
```json
[
  {
    "id": 1,
    "name": "Hockey Stick Pro",
    "category": "hockey",
    "price_per_day": 50000.0,
    "stock": 10,
    "description": "Professional hockey stick",
    "image_url": "https://example.com/image.jpg",
    "seller_id": 2,
    "seller_username": "john_seller",
    "is_featured": true
  }
]
```

**Flutter Model:**
```dart
class Gear {
  final int id;
  final String name;
  final String category;
  final double pricePerDay;
  final int stock;
  final String description;
  final String imageUrl;
  final int sellerId;
  final String sellerUsername;
  final bool isFeatured;

  Gear({
    required this.id,
    required this.name,
    required this.category,
    required this.pricePerDay,
    required this.stock,
    required this.description,
    required this.imageUrl,
    required this.sellerId,
    required this.sellerUsername,
    required this.isFeatured,
  });

  factory Gear.fromJson(Map<String, dynamic> json) => Gear(
    id: json["id"],
    name: json["name"],
    category: json["category"],
    pricePerDay: json["price_per_day"].toDouble(),
    stock: json["stock"],
    description: json["description"],
    imageUrl: json["image_url"],
    sellerId: json["seller_id"],
    sellerUsername: json["seller_username"],
    isFeatured: json["is_featured"],
  );
}
```

---

### 2. Get Gear Detail
**Endpoint:** `GET /gears/<int:id>/`

**Authentication:** Not required

**Response:**
```json
{
  "id": 1,
  "name": "Hockey Stick Pro",
  "category": "hockey",
  "price_per_day": 50000.0,
  "stock": 10,
  "description": "Professional hockey stick",
  "image_url": "https://example.com/image.jpg",
  "seller_id": 2,
  "seller_username": "john_seller",
  "is_featured": true
}
```

---

### 3. Get Cart
**Endpoint:** `GET /cart/`

**Authentication:** Required (Login)

**Response:**
```json
{
  "cart_items": [
    {
      "id": 1,
      "gear_id": 5,
      "gear_name": "Ice Skates",
      "gear_image_url": "https://example.com/skates.jpg",
      "price_per_day": 30000.0,
      "quantity": 2,
      "days": 3,
      "subtotal": 180000.0,
      "stock_available": 15
    }
  ],
  "total_price": 180000.0,
  "total_items": 1
}
```

**Flutter Model:**
```dart
class CartResponse {
  final List<CartItem> cartItems;
  final double totalPrice;
  final int totalItems;

  CartResponse({
    required this.cartItems,
    required this.totalPrice,
    required this.totalItems,
  });

  factory CartResponse.fromJson(Map<String, dynamic> json) => CartResponse(
    cartItems: List<CartItem>.from(
      json["cart_items"].map((x) => CartItem.fromJson(x))
    ),
    totalPrice: json["total_price"].toDouble(),
    totalItems: json["total_items"],
  );
}

class CartItem {
  final int id;
  final int gearId;
  final String gearName;
  final String gearImageUrl;
  final double pricePerDay;
  final int quantity;
  final int days;
  final double subtotal;
  final int stockAvailable;

  CartItem({
    required this.id,
    required this.gearId,
    required this.gearName,
    required this.gearImageUrl,
    required this.pricePerDay,
    required this.quantity,
    required this.days,
    required this.subtotal,
    required this.stockAvailable,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) => CartItem(
    id: json["id"],
    gearId: json["gear_id"],
    gearName: json["gear_name"],
    gearImageUrl: json["gear_image_url"],
    pricePerDay: json["price_per_day"].toDouble(),
    quantity: json["quantity"],
    days: json["days"],
    subtotal: json["subtotal"].toDouble(),
    stockAvailable: json["stock_available"],
  );
}
```

---

### 4. Add to Cart
**Endpoint:** `POST /cart/add/`

**Authentication:** Required (Login)

**Request Body:**
```json
{
  "gear_id": 5,
  "quantity": 2,
  "days": 3
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Ice Skates added to cart",
  "cart_item_id": 1
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "Stock not available. Only 5 items left"
}
```

---

### 5. Update Cart Item
**Endpoint:** `POST /cart/update/<int:item_id>/`

**Authentication:** Required (Login)

**Request Body:**
```json
{
  "quantity": 3,
  "days": 5
}
```
*Note: Anda bisa update salah satu atau keduanya*

**Response:**
```json
{
  "success": true,
  "message": "Cart updated",
  "subtotal": 450000.0
}
```

---

### 6. Remove from Cart
**Endpoint:** `POST /cart/remove/<int:item_id>/`

**Authentication:** Required (Login)

**Response:**
```json
{
  "success": true,
  "message": "Ice Skates removed from cart"
}
```

---

### 7. Checkout
**Endpoint:** `POST /checkout/`

**Authentication:** Required (Login)

**Request Body:** Empty (semua item di cart akan di-checkout)

**Response:**
```json
{
  "success": true,
  "message": "Checkout successful",
  "rental_id": 123,
  "total_cost": 450000.0,
  "return_date": "2025-11-25",
  "items": [
    {
      "gear_name": "Ice Skates",
      "quantity": 2,
      "days": 3,
      "price_per_day": 30000.0,
      "subtotal": 180000.0
    }
  ]
}
```

**Flutter Model:**
```dart
class CheckoutResponse {
  final bool success;
  final String message;
  final int rentalId;
  final double totalCost;
  final String returnDate;
  final List<CheckoutItem> items;

  CheckoutResponse({
    required this.success,
    required this.message,
    required this.rentalId,
    required this.totalCost,
    required this.returnDate,
    required this.items,
  });

  factory CheckoutResponse.fromJson(Map<String, dynamic> json) => CheckoutResponse(
    success: json["success"],
    message: json["message"],
    rentalId: json["rental_id"],
    totalCost: json["total_cost"].toDouble(),
    returnDate: json["return_date"],
    items: List<CheckoutItem>.from(
      json["items"].map((x) => CheckoutItem.fromJson(x))
    ),
  );
}

class CheckoutItem {
  final String gearName;
  final int quantity;
  final int days;
  final double pricePerDay;
  final double subtotal;

  CheckoutItem({
    required this.gearName,
    required this.quantity,
    required this.days,
    required this.pricePerDay,
    required this.subtotal,
  });

  factory CheckoutItem.fromJson(Map<String, dynamic> json) => CheckoutItem(
    gearName: json["gear_name"],
    quantity: json["quantity"],
    days: json["days"],
    pricePerDay: json["price_per_day"].toDouble(),
    subtotal: json["subtotal"].toDouble(),
  );
}
```

---

### 8. Get Rental History
**Endpoint:** `GET /rentals/`

**Authentication:** Required (Login)

**Response:**
```json
{
  "rentals": [
    {
      "id": 123,
      "customer_name": "john_doe",
      "rental_date": "2025-11-19T10:30:00Z",
      "return_date": "2025-11-25",
      "total_cost": 450000.0,
      "items": [
        {
          "gear_name": "Ice Skates",
          "quantity": 2,
          "price_per_day": 30000.0,
          "subtotal": 180000.0
        }
      ]
    }
  ]
}
```

---

## Seller Endpoints (Authentication Required - Seller Only)

### 9. Get Seller's Gears
**Endpoint:** `GET /seller/gears/`

**Authentication:** Required (Seller)

**Response:**
```json
{
  "gears": [
    {
      "id": 1,
      "name": "Hockey Stick Pro",
      "category": "hockey",
      "price_per_day": 50000.0,
      "stock": 10,
      "description": "Professional hockey stick",
      "image_url": "https://example.com/image.jpg",
      "is_featured": true
    }
  ]
}
```

---

### 10. Create Gear (Seller)
**Endpoint:** `POST /seller/gears/create/`

**Authentication:** Required (Seller)

**Request Body:**
```json
{
  "name": "New Hockey Stick",
  "category": "hockey",
  "price_per_day": 60000.0,
  "stock": 15,
  "description": "Brand new professional hockey stick",
  "image_url": "https://example.com/new-stick.jpg",
  "is_featured": false
}
```

**Valid Categories:**
- `hockey`
- `curling`
- `ice_skating`
- `apparel`
- `accessories`
- `protective_gear`
- `other`

**Response:**
```json
{
  "success": true,
  "message": "Gear created successfully",
  "gear_id": 42
}
```

---

### 11. Update Gear (Seller)
**Endpoint:** `POST /seller/gears/<int:id>/update/`

**Authentication:** Required (Seller - must own the gear)

**Request Body:** (semua field optional)
```json
{
  "name": "Updated Hockey Stick",
  "price_per_day": 65000.0,
  "stock": 20
}
```

**Response:**
```json
{
  "success": true,
  "message": "Gear updated successfully"
}
```

---

### 12. Delete Gear (Seller)
**Endpoint:** `POST /seller/gears/<int:id>/delete/`

**Authentication:** Required (Seller - must own the gear)

**Response:**
```json
{
  "success": true,
  "message": "Hockey Stick Pro deleted successfully"
}
```

---

## Error Responses

### Authentication Error (401)
```json
{
  "success": false,
  "message": "Authentication required"
}
```

### Not Found (404)
```json
{
  "error": "Gear not found"
}
```

### Validation Error (400)
```json
{
  "success": false,
  "message": "Days must be between 1-30"
}
```

### Server Error (500)
```json
{
  "success": false,
  "message": "Internal server error"
}
```

---

## Example Flutter Integration

### Service Class
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class RentalGearService {
  static const String baseUrl = 'http://localhost:8000/rental_gear/api/flutter';
  
  Future<List<Gear>> getAllGears() async {
    final response = await http.get(Uri.parse('$baseUrl/gears/'));
    
    if (response.statusCode == 200) {
      List<dynamic> body = jsonDecode(response.body);
      return body.map((dynamic item) => Gear.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load gears');
    }
  }
  
  Future<CartResponse> getCart(String cookie) async {
    final response = await http.get(
      Uri.parse('$baseUrl/cart/'),
      headers: {'Cookie': cookie},
    );
    
    if (response.statusCode == 200) {
      return CartResponse.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load cart');
    }
  }
  
  Future<Map<String, dynamic>> addToCart({
    required int gearId,
    required int quantity,
    required int days,
    required String cookie,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/cart/add/'),
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookie,
      },
      body: jsonEncode({
        'gear_id': gearId,
        'quantity': quantity,
        'days': days,
      }),
    );
    
    return jsonDecode(response.body);
  }
  
  Future<CheckoutResponse> checkout(String cookie) async {
    final response = await http.post(
      Uri.parse('$baseUrl/checkout/'),
      headers: {'Cookie': cookie},
    );
    
    if (response.statusCode == 200) {
      return CheckoutResponse.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Checkout failed');
    }
  }
}
```

---

## Notes

1. **Authentication**: Gunakan cookie-based authentication dari Django
2. **Data Types**: Pastikan konversi `.toDouble()` untuk semua decimal fields dari Django
3. **Error Handling**: Selalu check `success` field di response untuk menentukan sukses/gagal
4. **Stock Management**: Stock akan otomatis berkurang saat checkout berhasil
5. **Date Format**: Semua date menggunakan ISO 8601 format
6. **CSRF**: Endpoints Flutter menggunakan `@csrf_exempt` untuk kemudahan integrasi

## Testing

Gunakan Postman atau tools sejenis untuk testing endpoints sebelum integrasi dengan Flutter.
