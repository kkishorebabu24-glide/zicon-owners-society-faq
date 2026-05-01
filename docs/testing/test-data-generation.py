# Test Data Generation Script

This script generates realistic test data for the Home Food Sellers Platform.

## Usage

```bash
# Install dependencies
pip install faker sqlalchemy psycopg2-binary

# Run the script
python generate_test_data.py
```

## Generated Data

### Residents (50 total)
- 20 sellers, 30 buyers
- Realistic Indian names
- Valid flat numbers (1-3500)
- Contact information

### Menu Items (200+ items)
- Variety of Indian dishes
- Different categories (Veg/Non-Veg/Snacks)
- Realistic prices (INR 50-300)
- Various quantities and pickup times

### Orders (100 orders)
- Mix of completed and pending orders
- Realistic timestamps
- Various order statuses

```python
#!/usr/bin/env python3
"""
Test Data Generation Script for Home Food Sellers Platform
Generates realistic test data for development and testing
"""

import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database setup
DATABASE_URL = "postgresql://user:password@localhost:5432/food_platform_test"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Models (simplified versions for data generation)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    flat_number = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    is_seller = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text)
    price = Column(Float)
    quantity = Column(Integer)
    category = Column(String)  # veg, non-veg, snacks
    pickup_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    total_price = Column(Float)
    status = Column(String, default="ordered")  # ordered, ready, completed, cancelled
    ordered_at = Column(DateTime, default=datetime.utcnow)
    pickup_confirmed_at = Column(DateTime, nullable=True)

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def generate_test_data():
    """Generate comprehensive test data"""
    fake = Faker('en_IN')  # Indian locale
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(Rating).delete()
        db.query(Order).delete()
        db.query(MenuItem).delete()
        db.query(User).delete()
        db.commit()

        print("Generating test users...")

        # Generate 50 residents
        users = []
        flat_numbers = random.sample(range(1, 3501), 50)  # 3500 flats total

        for i, flat in enumerate(flat_numbers):
            is_seller = i < 20  # First 20 are sellers
            user = User(
                flat_number=f"A-{flat:04d}",  # Format: A-0001
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                is_seller=is_seller,
                is_approved=True  # All test users approved
            )
            users.append(user)
            db.add(user)

        db.commit()
        print(f"Created {len(users)} users")

        # Separate buyers and sellers
        sellers = [u for u in users if u.is_seller]
        buyers = [u for u in users if not u.is_seller]

        print("Generating menu items...")

        # Indian food data
        veg_dishes = [
            "Paneer Butter Masala", "Chana Masala", "Aloo Gobi", "Palak Paneer",
            "Rajma", "Dal Makhani", "Vegetable Biryani", "Pav Bhaji",
            "Veg Kolhapuri", "Malabar Veg Curry", "Paneer Tikka Masala"
        ]

        non_veg_dishes = [
            "Chicken Biryani", "Mutton Curry", "Fish Curry", "Chicken Masala",
            "Egg Curry", "Prawn Malabar", "Chicken Tikka", "Mutton Biryani",
            "Fish Fry", "Chicken 65", "Butter Chicken"
        ]

        snacks = [
            "Samosa", "Pakora", "Bhelpuri", "Pani Puri", "Dhokla",
            "Khakra", "Khichdi", "Upma", "Poha", "Sev Puri", "Dahi Vada"
        ]

        menu_items = []

        for seller in sellers:
            # Each seller creates 8-12 items
            num_items = random.randint(8, 12)

            for _ in range(num_items):
                # Random category and dish
                category = random.choice(['veg', 'non-veg', 'snacks'])
                if category == 'veg':
                    dish_name = random.choice(veg_dishes)
                elif category == 'non-veg':
                    dish_name = random.choice(non_veg_dishes)
                else:
                    dish_name = random.choice(snacks)

                # Generate pickup time (today or tomorrow, various times)
                days_ahead = random.randint(0, 1)
                base_date = datetime.now() + timedelta(days=days_ahead)
                hour = random.choice([12, 13, 19, 20, 21])  # Lunch and dinner times
                minute = random.choice([0, 30])
                pickup_time = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # Skip if pickup time is in the past
                if pickup_time < datetime.now():
                    continue

                menu_item = MenuItem(
                    seller_id=seller.id,
                    name=dish_name,
                    description=fake.sentence(),
                    price=round(random.uniform(50, 300), 2),
                    quantity=random.randint(5, 20),
                    category=category,
                    pickup_time=pickup_time,
                    is_active=True
                )
                menu_items.append(menu_item)
                db.add(menu_item)

        db.commit()
        print(f"Created {len(menu_items)} menu items")

        print("Generating orders...")

        # Generate 100 orders
        orders = []
        completed_orders = []

        for _ in range(100):
            # Random buyer and menu item
            buyer = random.choice(buyers)
            menu_item = random.choice(menu_items)

            # Ensure buyer doesn't order from themselves
            if menu_item.seller_id == buyer.id:
                continue

            # Random quantity (1 to available)
            quantity = random.randint(1, min(3, menu_item.quantity))

            # Calculate total price
            total_price = menu_item.price * quantity

            # Random order date (last 30 days)
            days_ago = random.randint(0, 30)
            ordered_at = datetime.now() - timedelta(days=days_ago)

            # Random status
            status_weights = [('completed', 70), ('ordered', 20), ('ready', 8), ('cancelled', 2)]
            status = random.choices([s[0] for s in status_weights], weights=[s[1] for s in status_weights])[0]

            order = Order(
                buyer_id=buyer.id,
                menu_item_id=menu_item.id,
                quantity=quantity,
                total_price=total_price,
                status=status,
                ordered_at=ordered_at
            )

            # Set pickup confirmation time for completed orders
            if status == 'completed':
                order.pickup_confirmed_at = ordered_at + timedelta(hours=random.randint(1, 24))
                completed_orders.append(order)

            orders.append(order)
            db.add(order)

        db.commit()
        print(f"Created {len(orders)} orders")

        print("Generating ratings...")

        # Generate ratings for completed orders (80% have ratings)
        ratings = []
        rated_orders = random.sample(completed_orders, int(len(completed_orders) * 0.8))

        for order in rated_orders:
            menu_item = next(item for item in menu_items if item.id == order.menu_item_id)
            seller = next(user for user in sellers if user.id == menu_item.seller_id)

            rating_value = random.choices([5, 4, 3, 2, 1], weights=[40, 35, 15, 7, 3])[0]

            rating = Rating(
                order_id=order.id,
                buyer_id=order.buyer_id,
                seller_id=seller.id,
                rating=rating_value,
                comment=fake.sentence() if random.random() > 0.3 else None,
                created_at=order.pickup_confirmed_at + timedelta(minutes=random.randint(5, 60))
            )
            ratings.append(rating)
            db.add(rating)

        db.commit()
        print(f"Created {len(ratings)} ratings")

        print("\nTest data generation completed successfully!")
        print("Summary:")
        print(f"- Users: {len(users)} ({len(sellers)} sellers, {len(buyers)} buyers)")
        print(f"- Menu Items: {len(menu_items)}")
        print(f"- Orders: {len(orders)}")
        print(f"- Ratings: {len(ratings)}")

    except Exception as e:
        print(f"Error generating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_test_data()
```

## SQL Alternative (if preferred)

If you prefer raw SQL inserts, here's a sample script:

```sql
-- Insert test users
INSERT INTO users (flat_number, name, email, phone, is_seller, is_approved, created_at) VALUES
('A-0001', 'Rajesh Kumar', 'rajesh.kumar@email.com', '+91-9876543210', true, true, NOW()),
('A-0002', 'Priya Sharma', 'priya.sharma@email.com', '+91-9876543211', false, true, NOW()),
-- ... continue for 50 users

-- Insert menu items
INSERT INTO menu_items (seller_id, name, description, price, quantity, category, pickup_time, is_active) VALUES
(1, 'Paneer Butter Masala', 'Creamy paneer curry with butter', 120.00, 8, 'veg', '2024-01-15 20:00:00', true),
(1, 'Chicken Biryani', 'Aromatic basmati rice with tender chicken', 180.00, 6, 'non-veg', '2024-01-15 19:30:00', true),
-- ... continue for 200+ items

-- Insert orders
INSERT INTO orders (buyer_id, menu_item_id, quantity, total_price, status, ordered_at) VALUES
(2, 1, 2, 240.00, 'completed', '2024-01-10 18:00:00'),
(3, 5, 1, 180.00, 'ordered', NOW()),
-- ... continue for 100 orders

-- Insert ratings
INSERT INTO ratings (order_id, buyer_id, seller_id, rating, comment, created_at) VALUES
(1, 2, 1, 5, 'Excellent food, will order again!', '2024-01-10 20:30:00'),
(2, 3, 1, 4, 'Good taste, timely delivery', '2024-01-11 19:45:00'),
-- ... continue for ratings
```