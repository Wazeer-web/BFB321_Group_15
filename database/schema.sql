
-- =====================================================
-- KOPANO HOME & LIFESTYLE
-- Database Schema
-- BFB321 Group 15
-- =====================================================

CREATE DATABASE IF NOT EXISTS kopano_inventory;

USE kopano_inventory;

-- =====================================================
-- TABLE 1: SUPPLIERS
-- =====================================================

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE 2: PRODUCTS
-- =====================================================

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    unit_price DECIMAL(10,2) NOT NULL,
    quantity_in_stock INT NOT NULL DEFAULT 0,
    reorder_level INT NOT NULL DEFAULT 10,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_products_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id),

    CONSTRAINT chk_product_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_product_quantity
        CHECK (quantity_in_stock >= 0),

    CONSTRAINT chk_reorder_level
        CHECK (reorder_level >= 0),

    INDEX idx_product_name (product_name),
    INDEX idx_product_category (category)
);

-- =====================================================
-- TABLE 3: DELIVERIES
-- =====================================================

CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    delivery_reference VARCHAR(50) NOT NULL UNIQUE,
    expected_date DATE NOT NULL,
    actual_date DATE,

    delivery_status ENUM(
        'Pending',
        'In Transit',
        'Delivered',
        'Delayed',
        'Cancelled'
    ) NOT NULL DEFAULT 'Pending',

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_deliveries_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id),

    INDEX idx_delivery_status (delivery_status),
    INDEX idx_expected_date (expected_date)
);
