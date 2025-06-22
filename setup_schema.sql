-- STEP 1: Full Database Reset
-- WARNING: This is a destructive action that will remove ALL tables and data.
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Restore default permissions for the new 'public' schema for Supabase
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;


-- STEP 2: Create the New, Final Database Structure

-- Create Category table
CREATE TABLE Category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- Create SubCategory table
CREATE TABLE SubCategory (
    subcategory_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    -- Link to the parent category
    category_id INT NOT NULL REFERENCES Category(category_id) ON DELETE CASCADE,
    -- Ensure a sub-category name is unique within its parent category
    UNIQUE (name, category_id)
);

-- Create Brand table
CREATE TABLE Brand (
    brand_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Create Supplier table
CREATE TABLE Supplier (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(100) -- This will store the phone number
);

-- Create Product table
CREATE TABLE Product (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    brand_id INT REFERENCES Brand(brand_id) ON DELETE SET NULL,
    category_id INT REFERENCES Category(category_id) ON DELETE SET NULL,
    subcategory_id INT REFERENCES SubCategory(subcategory_id) ON DELETE SET NULL,
    market_price DECIMAL(10, 2) NOT NULL CHECK (market_price >= 0),
    sale_price DECIMAL(10, 2) NOT NULL CHECK (sale_price >= 0),
    unit VARCHAR(50),
    stock_level INT NOT NULL DEFAULT 0 CHECK (stock_level >= 0),
    rating DECIMAL(3, 2) DEFAULT 0.0 CHECK (rating >= 0 AND rating <= 5)
);

-- Create Customer table
CREATE TABLE Customer (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(25)
);

-- Create OrderTable (Simplified)
CREATE TABLE OrderTable (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customer(customer_id) ON DELETE CASCADE,
    order_date TIMESTAMPTZ DEFAULT NOW(),
    total_amount DECIMAL(10, 2) NOT NULL
);

-- Create OrderItem table (Simplified)
CREATE TABLE OrderItem (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES OrderTable(order_id) ON DELETE CASCADE,
    product_id INT REFERENCES Product(product_id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0)
);

-- Create Supplies table
CREATE TABLE Supplies (
    supply_id SERIAL PRIMARY KEY,
    supplier_id INT REFERENCES Supplier(supplier_id) ON DELETE CASCADE,
    product_id INT REFERENCES Product(product_id) ON DELETE CASCADE,
    supply_date DATE NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL
);


-- STEP 3: Insert Compatible Sample Data

-- 1. Insert Categories
INSERT INTO Category (name, description) VALUES
('Beauty & Hygiene', 'Products for personal care, grooming, and wellness.'),
('Kitchen, Garden & Pets', 'Items for kitchen, home garden, and pet care.'),
('Cleaning & Household', 'Products for cleaning and maintaining a household.'),
('Gourmet & World Food', 'Specialty and international food items.');

-- 2. Insert SubCategories
INSERT INTO SubCategory (category_id, name) VALUES
((SELECT category_id FROM Category WHERE name = 'Beauty & Hygiene'), 'Hair Care'),
((SELECT category_id FROM Category WHERE name = 'Beauty & Hygiene'), 'Skin Care'),
((SELECT category_id FROM Category WHERE name = 'Kitchen, Garden & Pets'), 'Storage & Accessories'),
((SELECT category_id FROM Category WHERE name = 'Cleaning & Household'), 'Bins & Bathroom Ware'),
((SELECT category_id FROM Category WHERE name = 'Gourmet & World Food'), 'Snacks, Dry Fruits, Nuts'),
((SELECT category_id FROM Category WHERE name = 'Gourmet & World Food'), 'Dairy & Cheese');


-- 3. Insert Brands
INSERT INTO Brand (name) VALUES
('Sri Sri Ayurveda'), ('Mastercook'), ('Nakoda'), ('Oxy'), ('Bionova'),
('Aroma Treasures'), ('Graminway'), ('Murginns'), ('NUTRASHIL'), ('StBotanica');

-- 4. Insert Products
INSERT INTO Product (name, description, category_id, subcategory_id, brand_id, market_price, sale_price, unit, stock_level, rating)
VALUES
('Garlic Oil - Vegetarian Capsule 500 mg', 'This Product contains Garlic Oil that is known to help proper digestion.', (SELECT category_id FROM Category WHERE name = 'Beauty & Hygiene'), (SELECT subcategory_id FROM SubCategory WHERE name = 'Hair Care'), (SELECT brand_id FROM Brand WHERE name = 'Sri Sri Ayurveda'), 220.00, 220.00, 'ml', 100, 4.1),
('Water Bottle - Orange', 'Each product is microwave safe (without lid), refrigerator safe, dishwasher safe.', (SELECT category_id FROM Category WHERE name = 'Kitchen, Garden & Pets'), (SELECT subcategory_id FROM SubCategory WHERE name = 'Storage & Accessories'), (SELECT brand_id FROM Brand WHERE name = 'Mastercook'), 180.00, 180.00, 'pcs', 50, 2.3),
('Cereal Flip Lid Container/Storage Jar', 'Multipurpose container with an attractive design and made from food-grade plastic.', (SELECT category_id FROM Category WHERE name = 'Cleaning & Household'), (SELECT subcategory_id FROM SubCategory WHERE name = 'Bins & Bathroom Ware'), (SELECT brand_id FROM Brand WHERE name = 'Nakoda'), 176.00, 149.00, 'pcs', 200, 3.7),
('Face Wash - Oil Control, Active', 'This face wash deeply cleanses dirt and impurities. Active ingredients help remove excess oil.', (SELECT category_id FROM Category WHERE name = 'Beauty & Hygiene'), (SELECT subcategory_id FROM SubCategory WHERE name = 'Skin Care'), (SELECT brand_id FROM Brand WHERE name = 'Oxy'), 110.00, 110.00, 'ml', 80, 5.0),
('Salted Pumpkin Seeds', 'Graminway Salted Pumpkin Seeds are the perfect snack for your family.', (SELECT category_id FROM Category WHERE name = 'Gourmet & World Food'), (SELECT subcategory_id FROM SubCategory WHERE name = 'Snacks, Dry Fruits, Nuts'), (SELECT brand_id FROM Brand WHERE name = 'Graminway'), 180.00, 180.00, 'gm', 40, 4.9),
('Organic Tofu - Soy Paneer', 'Murginns’ fresh and firm Organic tofu is the perfect non-dairy substitute to paneer.', (SELECT category_id FROM Category WHERE name = 'Gourmet & World Food'), (SELECT subcategory_id FROM SubCategory WHERE name = 'Dairy & Cheese'), (SELECT brand_id FROM Brand WHERE name = 'Murginns'), 90.00, 85.14, 'gm', 90, 3.9);

-- 5. Insert Suppliers
INSERT INTO Supplier (name, contact) VALUES
('ABC Supplies', '111-222-3333'),
('FreshMart Distributors', '222-333-4444');

-- 6. Insert Customers
INSERT INTO Customer (name, email, phone) VALUES
('John Doe', 'john.doe@example.com', '123-456-7890'),
('Jane Smith', 'jane.smith@example.com', '987-654-3210');

-- 7. Insert Orders
INSERT INTO OrderTable (customer_id, total_amount) VALUES
((SELECT customer_id FROM Customer WHERE email = 'john.doe@example.com'), 259.00),
((SELECT customer_id FROM Customer WHERE email = 'jane.smith@example.com'), 265.14);

-- 8. Insert OrderItems
INSERT INTO OrderItem (order_id, product_id, quantity) VALUES
(1, (SELECT product_id FROM Product WHERE name LIKE 'Face Wash%'), 1),
(1, (SELECT product_id FROM Product WHERE name LIKE 'Cereal Flip%'), 1),
(2, (SELECT product_id FROM Product WHERE name LIKE 'Organic Tofu%'), 1),
(2, (SELECT product_id FROM Product WHERE name LIKE 'Salted Pumpkin%'), 1);

-- 9. Insert Supplies
INSERT INTO Supplies (supplier_id, product_id, supply_date, cost_price) VALUES
((SELECT supplier_id FROM Supplier WHERE name = 'ABC Supplies'), (SELECT product_id FROM Product WHERE name LIKE 'Garlic Oil%'), '2025-05-01', 180.00),
((SELECT supplier_id FROM Supplier WHERE name = 'FreshMart Distributors'), (SELECT product_id FROM Product WHERE name LIKE 'Water Bottle%'), '2025-05-02', 150.00);