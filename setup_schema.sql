-- Drop the database if it already exists (be careful!)
DROP DATABASE IF EXISTS grocerydb;

-- Create a fresh database
CREATE DATABASE grocerydb;
USE grocerydb;

-- Create Product table
CREATE TABLE Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10,2),
    unit VARCHAR(50),
    stock_level INT
);

-- Create Supplier table
CREATE TABLE Supplier (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    contact VARCHAR(100)
);

-- Create Customer table
CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20)
);

-- Create OrderTable (Order is a reserved word in MySQL)
CREATE TABLE OrderTable (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Create OrderItem table (Many-to-Many: Orders & Products)
CREATE TABLE OrderItem (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES OrderTable(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- Create Supplies table (Many-to-Many: Products & Suppliers)
CREATE TABLE Supplies (
    supply_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT,
    product_id INT,
    supply_date DATE,
    cost_price DECIMAL(10,2),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- Insert 10 sample rows for each table
INSERT INTO Product (name, category, sub_category, brand, price, unit, stock_level)
VALUES
('Garlic Oil', 'Beauty & Hygiene', 'Hair Care', 'Sri Sri Ayurveda', 220.00, 'ml', 100),
('Water Bottle', 'Kitchen, Garden & Pets', 'Storage', 'Mastercook', 180.00, 'pcs', 50),
('Cereal Jar', 'Cleaning & Household', 'Storage', 'Nakoda', 149.00, 'pcs', 200),
('Face Wash', 'Beauty & Hygiene', 'Skin Care', 'Oxy', 110.00, 'ml', 80),
('Hand Sanitizer', 'Beauty & Hygiene', 'Bath', 'Bionova', 250.00, 'ml', 150),
('Smooth Skin Oil', 'Beauty & Hygiene', 'Skin Care', 'Aroma Treasures', 324.00, 'ml', 70),
('Salted Pumpkin', 'Gourmet & World Food', 'Snacks', 'Graminway', 180.00, 'gm', 40),
('Organic Tofu', 'Gourmet & World Food', 'Dairy & Cheese', 'Murginns', 85.14, 'gm', 90),
('Wheat Grass Powder', 'Gourmet & World Food', 'Health Food', 'NUTRASHIL', 261.00, 'gm', 60),
('Biotin Shampoo', 'Beauty & Hygiene', 'Hair Care', 'StBotanica', 1098.00, 'ml', 30);

-- Similarly insert into Supplier
INSERT INTO Supplier (name, contact)
VALUES
('ABC Supplies', 'abc@example.com'),
('XYZ Traders', 'xyz@example.com'),
('Global Products', 'global@example.com'),
('FreshMart', 'fresh@example.com'),
('Beauty Essentials', 'beauty@example.com'),
('Daily Needs', 'daily@example.com'),
('Wellness Co', 'wellness@example.com'),
('Eco Store', 'eco@example.com'),
('Nature Hub', 'nature@example.com'),
('Organic World', 'organic@example.com');

-- Insert into Customer
INSERT INTO Customer (name, email, phone)
VALUES
('John Doe', 'john@example.com', '1234567890'),
('Jane Smith', 'jane@example.com', '9876543210'),
('Alice Johnson', 'alice@example.com', '1112223333'),
('Bob Brown', 'bob@example.com', '4445556666'),
('Charlie White', 'charlie@example.com', '7778889999'),
('Eva Green', 'eva@example.com', '2223334444'),
('Tom Blue', 'tom@example.com', '5556667777'),
('Sam Red', 'sam@example.com', '8889990000'),
('Lisa Pink', 'lisa@example.com', '6667778888'),
('Nick Black', 'nick@example.com', '9990001111');

-- Insert sample Orders
INSERT INTO OrderTable (customer_id, order_date, total_amount)
VALUES
(1, '2025-06-01', 500.00),
(2, '2025-06-02', 300.00),
(3, '2025-06-03', 450.00),
(4, '2025-06-04', 700.00),
(5, '2025-06-05', 200.00),
(6, '2025-06-06', 350.00),
(7, '2025-06-07', 400.00),
(8, '2025-06-08', 150.00),
(9, '2025-06-09', 600.00),
(10, '2025-06-10', 750.00);

-- Insert sample OrderItems
INSERT INTO OrderItem (order_id, product_id, quantity)
VALUES
(1, 1, 2),
(1, 3, 1),
(2, 4, 3),
(2, 5, 2),
(3, 6, 1),
(4, 7, 4),
(5, 8, 1),
(6, 9, 2),
(7, 10, 1),
(8, 2, 2);

-- Insert sample Supplies
INSERT INTO Supplies (supplier_id, product_id, supply_date, cost_price)
VALUES
(1, 1, '2025-05-01', 180.00),
(2, 2, '2025-05-02', 150.00),
(3, 3, '2025-05-03', 120.00),
(4, 4, '2025-05-04', 100.00),
(5, 5, '2025-05-05', 90.00),
(6, 6, '2025-05-06', 110.00),
(7, 7, '2025-05-07', 160.00),
(8, 8, '2025-05-08', 85.00),
(9, 9, '2025-05-09', 220.00),
(10, 10, '2025-05-10', 800.00);
