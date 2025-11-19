// rental_gear_models.dart
// Model classes untuk Rental Gear Flutter Integration

import 'dart:convert';

// ==================== GEAR MODEL ====================
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
        description: json["description"] ?? "",
        imageUrl: json["image_url"] ?? "",
        sellerId: json["seller_id"],
        sellerUsername: json["seller_username"],
        isFeatured: json["is_featured"],
      );

  Map<String, dynamic> toJson() => {
        "id": id,
        "name": name,
        "category": category,
        "price_per_day": pricePerDay,
        "stock": stock,
        "description": description,
        "image_url": imageUrl,
        "seller_id": sellerId,
        "seller_username": sellerUsername,
        "is_featured": isFeatured,
      };
}

// ==================== CART MODELS ====================
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
          json["cart_items"].map((x) => CartItem.fromJson(x)),
        ),
        totalPrice: json["total_price"].toDouble(),
        totalItems: json["total_items"],
      );

  Map<String, dynamic> toJson() => {
        "cart_items": List<dynamic>.from(cartItems.map((x) => x.toJson())),
        "total_price": totalPrice,
        "total_items": totalItems,
      };
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
        gearImageUrl: json["gear_image_url"] ?? "",
        pricePerDay: json["price_per_day"].toDouble(),
        quantity: json["quantity"],
        days: json["days"],
        subtotal: json["subtotal"].toDouble(),
        stockAvailable: json["stock_available"],
      );

  Map<String, dynamic> toJson() => {
        "id": id,
        "gear_id": gearId,
        "gear_name": gearName,
        "gear_image_url": gearImageUrl,
        "price_per_day": pricePerDay,
        "quantity": quantity,
        "days": days,
        "subtotal": subtotal,
        "stock_available": stockAvailable,
      };
}

// ==================== CHECKOUT MODELS ====================
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

  factory CheckoutResponse.fromJson(Map<String, dynamic> json) =>
      CheckoutResponse(
        success: json["success"],
        message: json["message"],
        rentalId: json["rental_id"],
        totalCost: json["total_cost"].toDouble(),
        returnDate: json["return_date"],
        items: List<CheckoutItem>.from(
          json["items"].map((x) => CheckoutItem.fromJson(x)),
        ),
      );

  Map<String, dynamic> toJson() => {
        "success": success,
        "message": message,
        "rental_id": rentalId,
        "total_cost": totalCost,
        "return_date": returnDate,
        "items": List<dynamic>.from(items.map((x) => x.toJson())),
      };
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

  Map<String, dynamic> toJson() => {
        "gear_name": gearName,
        "quantity": quantity,
        "days": days,
        "price_per_day": pricePerDay,
        "subtotal": subtotal,
      };
}

// ==================== RENTAL MODELS ====================
class RentalsResponse {
  final List<Rental> rentals;

  RentalsResponse({
    required this.rentals,
  });

  factory RentalsResponse.fromJson(Map<String, dynamic> json) =>
      RentalsResponse(
        rentals: List<Rental>.from(
          json["rentals"].map((x) => Rental.fromJson(x)),
        ),
      );

  Map<String, dynamic> toJson() => {
        "rentals": List<dynamic>.from(rentals.map((x) => x.toJson())),
      };
}

class Rental {
  final int id;
  final String customerName;
  final DateTime rentalDate;
  final DateTime returnDate;
  final double totalCost;
  final List<RentalItem> items;

  Rental({
    required this.id,
    required this.customerName,
    required this.rentalDate,
    required this.returnDate,
    required this.totalCost,
    required this.items,
  });

  factory Rental.fromJson(Map<String, dynamic> json) => Rental(
        id: json["id"],
        customerName: json["customer_name"],
        rentalDate: DateTime.parse(json["rental_date"]),
        returnDate: DateTime.parse(json["return_date"]),
        totalCost: json["total_cost"].toDouble(),
        items: List<RentalItem>.from(
          json["items"].map((x) => RentalItem.fromJson(x)),
        ),
      );

  Map<String, dynamic> toJson() => {
        "id": id,
        "customer_name": customerName,
        "rental_date": rentalDate.toIso8601String(),
        "return_date": returnDate.toIso8601String(),
        "total_cost": totalCost,
        "items": List<dynamic>.from(items.map((x) => x.toJson())),
      };
}

class RentalItem {
  final String gearName;
  final int quantity;
  final double pricePerDay;
  final double subtotal;

  RentalItem({
    required this.gearName,
    required this.quantity,
    required this.pricePerDay,
    required this.subtotal,
  });

  factory RentalItem.fromJson(Map<String, dynamic> json) => RentalItem(
        gearName: json["gear_name"],
        quantity: json["quantity"],
        pricePerDay: json["price_per_day"].toDouble(),
        subtotal: json["subtotal"].toDouble(),
      );

  Map<String, dynamic> toJson() => {
        "gear_name": gearName,
        "quantity": quantity,
        "price_per_day": pricePerDay,
        "subtotal": subtotal,
      };
}

// ==================== SELLER GEAR RESPONSE ====================
class SellerGearsResponse {
  final List<SellerGear> gears;

  SellerGearsResponse({
    required this.gears,
  });

  factory SellerGearsResponse.fromJson(Map<String, dynamic> json) =>
      SellerGearsResponse(
        gears: List<SellerGear>.from(
          json["gears"].map((x) => SellerGear.fromJson(x)),
        ),
      );

  Map<String, dynamic> toJson() => {
        "gears": List<dynamic>.from(gears.map((x) => x.toJson())),
      };
}

class SellerGear {
  final int id;
  final String name;
  final String category;
  final double pricePerDay;
  final int stock;
  final String description;
  final String imageUrl;
  final bool isFeatured;

  SellerGear({
    required this.id,
    required this.name,
    required this.category,
    required this.pricePerDay,
    required this.stock,
    required this.description,
    required this.imageUrl,
    required this.isFeatured,
  });

  factory SellerGear.fromJson(Map<String, dynamic> json) => SellerGear(
        id: json["id"],
        name: json["name"],
        category: json["category"],
        pricePerDay: json["price_per_day"].toDouble(),
        stock: json["stock"],
        description: json["description"] ?? "",
        imageUrl: json["image_url"] ?? "",
        isFeatured: json["is_featured"],
      );

  Map<String, dynamic> toJson() => {
        "id": id,
        "name": name,
        "category": category,
        "price_per_day": pricePerDay,
        "stock": stock,
        "description": description,
        "image_url": imageUrl,
        "is_featured": isFeatured,
      };
}

// ==================== API RESPONSE MODELS ====================
class ApiResponse {
  final bool success;
  final String message;
  final dynamic data;

  ApiResponse({
    required this.success,
    required this.message,
    this.data,
  });

  factory ApiResponse.fromJson(Map<String, dynamic> json) => ApiResponse(
        success: json["success"],
        message: json["message"],
        data: json["data"],
      );

  Map<String, dynamic> toJson() => {
        "success": success,
        "message": message,
        "data": data,
      };
}
