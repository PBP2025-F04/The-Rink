# Rental Gear API - Test Cases

## Test dengan curl atau Postman

### 1. Get All Gears (No Auth)
```bash
curl -X GET http://localhost:8000/rental_gear/api/flutter/gears/
```

Expected Response:
```json
[
  {
    "id": 1,
    "name": "Hockey Stick",
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

---

### 2. Get Gear Detail (No Auth)
```bash
curl -X GET http://localhost:8000/rental_gear/api/flutter/gears/1/
```

---

### 3. Get Cart (Auth Required)
```bash
curl -X GET http://localhost:8000/rental_gear/api/flutter/cart/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

---

### 4. Add to Cart (Auth Required)
```bash
curl -X POST http://localhost:8000/rental_gear/api/flutter/cart/add/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "gear_id": 1,
    "quantity": 2,
    "days": 3
  }'
```

Expected Response:
```json
{
  "success": true,
  "message": "Hockey Stick added to cart",
  "cart_item_id": 1
}
```

---

### 5. Update Cart Item (Auth Required)
```bash
curl -X POST http://localhost:8000/rental_gear/api/flutter/cart/update/1/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "quantity": 3,
    "days": 5
  }'
```

---

### 6. Remove from Cart (Auth Required)
```bash
curl -X POST http://localhost:8000/rental_gear/api/flutter/cart/remove/1/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

---

### 7. Checkout (Auth Required)
```bash
curl -X POST http://localhost:8000/rental_gear/api/flutter/checkout/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

---

### 8. Get Rental History (Auth Required)
```bash
curl -X GET http://localhost:8000/rental_gear/api/flutter/rentals/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

---

### 9. Get Seller's Gears (Seller Auth Required)
```bash
curl -X GET http://localhost:8000/rental_gear/api/flutter/seller/gears/ \
  -H "Cookie: sessionid=SELLER_SESSION_ID"
```

---

### 10. Create Gear (Seller Auth Required)
```bash
curl -X POST http://localhost:8000/rental_gear/api/flutter/seller/gears/create/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=SELLER_SESSION_ID" \
  -d '{
    "name": "Premium Hockey Stick",
    "category": "hockey",
    "price_per_day": 75000.0,
    "stock": 10,
    "description": "Top quality professional stick",
    "image_url": "https://example.com/premium-stick.jpg",
    "is_featured": true
  }'
```

---

### 11. Update Gear (Seller Auth Required)
```bash
curl -X POST http://localhost:8000/rental_gear/api/flutter/seller/gears/1/update/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=SELLER_SESSION_ID" \
  -d '{
    "price_per_day": 80000.0,
    "stock": 15
  }'
```

---

### 12. Delete Gear (Seller Auth Required)
```bash
curl -X POST http://localhost:8000/rental_gear/api/flutter/seller/gears/1/delete/ \
  -H "Cookie: sessionid=SELLER_SESSION_ID"
```

---

## Postman Collection

Import collection ini ke Postman:

```json
{
  "info": {
    "name": "Rental Gear API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get All Gears",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/rental_gear/api/flutter/gears/"
      }
    },
    {
      "name": "Get Gear Detail",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/rental_gear/api/flutter/gears/1/"
      }
    },
    {
      "name": "Get Cart",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/rental_gear/api/flutter/cart/",
        "header": [
          {
            "key": "Cookie",
            "value": "sessionid={{session_id}}"
          }
        ]
      }
    },
    {
      "name": "Add to Cart",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/rental_gear/api/flutter/cart/add/",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "Cookie",
            "value": "sessionid={{session_id}}"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"gear_id\": 1,\n  \"quantity\": 2,\n  \"days\": 3\n}"
        }
      }
    },
    {
      "name": "Checkout",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/rental_gear/api/flutter/checkout/",
        "header": [
          {
            "key": "Cookie",
            "value": "sessionid={{session_id}}"
          }
        ]
      }
    }
  ],
  "variable": [
    {
      "key": "session_id",
      "value": "your_session_id_here"
    }
  ]
}
```

---

## Test Scenarios

### Scenario 1: Customer Browse & Rent
1. ✅ Get all gears
2. ✅ Get gear detail (ID: 1)
3. ✅ Login (get session_id)
4. ✅ Add gear to cart (quantity: 2, days: 3)
5. ✅ Get cart (verify item added)
6. ✅ Update cart item (change days to 5)
7. ✅ Checkout
8. ✅ Get rental history (verify rental created)

### Scenario 2: Seller Manage Gears
1. ✅ Login as seller (get session_id)
2. ✅ Get seller's gears
3. ✅ Create new gear
4. ✅ Update gear (change price)
5. ✅ Delete gear

### Scenario 3: Error Handling
1. ❌ Add to cart without login (expect 401)
2. ❌ Add to cart with quantity > stock (expect 400)
3. ❌ Add to cart with days > 30 (expect 400)
4. ❌ Get gear detail with invalid ID (expect 404)
5. ❌ Checkout empty cart (expect 400)

---

## Python Test Script

```python
import requests
import json

BASE_URL = "http://localhost:8000/rental_gear/api/flutter"

def test_get_all_gears():
    response = requests.get(f"{BASE_URL}/gears/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_add_to_cart(session_id):
    url = f"{BASE_URL}/cart/add/"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"sessionid={session_id}"
    }
    data = {
        "gear_id": 1,
        "quantity": 2,
        "days": 3
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_checkout(session_id):
    url = f"{BASE_URL}/checkout/"
    headers = {"Cookie": f"sessionid={session_id}"}
    response = requests.post(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

if __name__ == "__main__":
    print("Testing Get All Gears...")
    test_get_all_gears()
    
    # Replace with actual session_id
    # session_id = "your_session_id_here"
    # test_add_to_cart(session_id)
    # test_checkout(session_id)
```

---

## Django Test Cases

```python
# tests/test_flutter_api.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from rental_gear.models import Gear, CartItem
from authentication.models import UserType
import json

class FlutterAPITestCase(TestCase):
    def setUp(self):
        # Create users
        self.customer = User.objects.create_user(username='customer', password='pass123')
        self.seller = User.objects.create_user(username='seller', password='pass123')
        
        # Create user types
        UserType.objects.create(user=self.customer, user_type='customer')
        UserType.objects.create(user=self.seller, user_type='seller')
        
        # Create gear
        self.gear = Gear.objects.create(
            name='Test Gear',
            category='hockey',
            price_per_day=50000,
            stock=10,
            seller=self.seller
        )
        
        self.client = Client()
    
    def test_get_all_gears(self):
        response = self.client.get('/rental_gear/api/flutter/gears/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Gear')
    
    def test_add_to_cart(self):
        self.client.login(username='customer', password='pass123')
        response = self.client.post(
            '/rental_gear/api/flutter/cart/add/',
            data=json.dumps({
                'gear_id': self.gear.id,
                'quantity': 2,
                'days': 3
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_checkout(self):
        self.client.login(username='customer', password='pass123')
        
        # Add item to cart
        CartItem.objects.create(
            user=self.customer,
            gear=self.gear,
            quantity=2,
            days=3
        )
        
        # Checkout
        response = self.client.post('/rental_gear/api/flutter/checkout/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('rental_id', data)
```

Run tests:
```bash
python manage.py test rental_gear.tests.test_flutter_api
```
