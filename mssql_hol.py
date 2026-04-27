#!/usr/bin/env python3
"""SQL Server demo: seed customers and generate orders."""

import argparse
import random
import sys
import time
from datetime import datetime

import pymssql

# ── Connection defaults (edit these) ─────────────────────────────────────────
HOST = "ali-sql-svr.c50usmosavrd.eu-central-1.rds.amazonaws.com"
DATABASE = "hol"
USER = "admin"
PASSWORD = "insert-password-here"
# ─────────────────────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen", "Charles",
    "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret",
    "Mark", "Sandra", "Donald", "Ashley", "Steven", "Dorothy", "Paul", "Emily",
    "Andrew", "Donna", "Joshua", "Carol", "Kenneth", "Amanda", "Kevin",
    "Melissa", "Brian", "Deborah", "George", "Stephanie", "Timothy", "Rebecca",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts",
]

CITIES = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"),
    ("Houston", "TX"), ("Phoenix", "AZ"), ("Philadelphia", "PA"),
    ("San Antonio", "TX"), ("San Diego", "CA"), ("Dallas", "TX"),
    ("Austin", "TX"), ("Denver", "CO"), ("Seattle", "WA"),
    ("Boston", "MA"), ("Nashville", "TN"), ("Portland", "OR"),
]

PRODUCTS = [
    ("Laptop", 899.99), ("Wireless Mouse", 29.99), ("Keyboard", 59.99),
    ("Monitor 27in", 349.99), ("USB-C Hub", 44.99), ("Webcam HD", 79.99),
    ("Headphones", 149.99), ("Desk Lamp", 34.99), ("Notebook Pack", 12.99),
    ("External SSD 1TB", 109.99), ("Phone Charger", 19.99),
    ("Bluetooth Speaker", 64.99), ("Mouse Pad XL", 24.99),
    ("Cable Organizer", 14.99), ("Laptop Stand", 49.99),
]


def get_connection(args):
    return pymssql.connect(
        server=args.host,
        user=args.user,
        password=args.password,
        database=args.database,
    )


def setup(args):
    """Create tables and seed 50 customers."""
    conn = get_connection(args)
    cursor = conn.cursor()

    print("Dropping existing tables...")
    cursor.execute("""
        IF OBJECT_ID('dbo.orders', 'U') IS NOT NULL DROP TABLE dbo.orders;
        IF OBJECT_ID('dbo.customers', 'U') IS NOT NULL DROP TABLE dbo.customers;
    """)

    print("Creating customers table...")
    cursor.execute("""
        CREATE TABLE dbo.customers (
            customer_id INT IDENTITY(1,1) PRIMARY KEY,
            first_name  VARCHAR(50)  NOT NULL,
            last_name   VARCHAR(50)  NOT NULL,
            email       VARCHAR(120) NOT NULL,
            phone       VARCHAR(20)  NOT NULL,
            city        VARCHAR(50)  NOT NULL,
            state       VARCHAR(2)   NOT NULL,
            created_at  DATETIME     NOT NULL DEFAULT GETDATE()
        );
    """)

    print("Creating orders table...")
    cursor.execute("""
        CREATE TABLE dbo.orders (
            order_id    INT IDENTITY(1,1) PRIMARY KEY,
            customer_id INT          NOT NULL,
            product     VARCHAR(100) NOT NULL,
            quantity    INT          NOT NULL,
            unit_price  DECIMAL(10,2) NOT NULL,
            order_date  DATETIME     NOT NULL DEFAULT GETDATE(),
            CONSTRAINT fk_orders_customer
                FOREIGN KEY (customer_id) REFERENCES dbo.customers(customer_id)
        );
    """)

    print("Inserting 50 customers...")
    used = set()
    for i in range(50):
        fn = FIRST_NAMES[i]
        ln = random.choice(LAST_NAMES)
        email = f"{fn.lower()}.{ln.lower()}@example.com"
        while email in used:
            ln = random.choice(LAST_NAMES)
            email = f"{fn.lower()}.{ln.lower()}@example.com"
        used.add(email)
        phone = f"({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}"
        city, state = random.choice(CITIES)
        cursor.execute(
            "INSERT INTO dbo.customers (first_name, last_name, email, phone, city, state) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (fn, ln, email, phone, city, state),
        )

    conn.commit()
    print("Setup complete: 50 customers inserted, orders table ready.")
    conn.close()


def generate_orders(args):
    """Insert a random order every 5 seconds."""
    conn = get_connection(args)
    cursor = conn.cursor()

    # Get customer IDs
    cursor.execute("SELECT customer_id, first_name, last_name FROM dbo.customers")
    customers = cursor.fetchall()
    if not customers:
        print("No customers found. Run with --setup first.")
        conn.close()
        sys.exit(1)

    print("Generating orders every 5 seconds (Ctrl+C to stop)...\n")
    count = 0
    try:
        while True:
            cust_id, first, last = random.choice(customers)
            product, price = random.choice(PRODUCTS)
            qty = random.randint(1, 5)
            total = qty * price

            cursor.execute(
                "INSERT INTO dbo.orders (customer_id, product, quantity, unit_price) "
                "VALUES (%s, %s, %s, %s)",
                (cust_id, product, qty, price),
            )
            conn.commit()

            count += 1
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] Order #{count}: {first} {last} — {qty}x {product} @ ${price:.2f} = ${total:.2f}")

            time.sleep(5)
    except KeyboardInterrupt:
        print(f"\nStopped. {count} orders created.")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="SQL Server demo tool")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--database", default=DATABASE)
    parser.add_argument("--user", default=USER)
    parser.add_argument("--password", default=PASSWORD)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--setup", action="store_true", help="Create tables and seed 50 customers")
    group.add_argument("--orders", action="store_true", help="Generate a new order every 5 seconds")

    args = parser.parse_args()

    if args.setup:
        setup(args)
    elif args.orders:
        generate_orders(args)


if __name__ == "__main__":
    main()
