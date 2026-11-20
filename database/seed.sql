
-- =====================================================
-- KOPANO HOME & LIFESTYLE
-- Sample / Seed Data
-- BFB321 Group 15
-- =====================================================

USE kopano_inventory;

-- =====================================================
-- 1. SUPPLIERS
-- =====================================================

INSERT INTO suppliers
(supplier_id, supplier_name, contact_person, email, phone, address)
VALUES
(1, 'Cape Home Supplies', 'John Smith',
 'john@capehome.co.za', '0215550101', 'Cape Town'),

(2, 'Urban Living Distributors', 'Sarah Adams',
 'sarah@urbanliving.co.za', '0115550202', 'Johannesburg'),

(3, 'Premier Furniture Wholesale', 'David Brown',
 'david@premierfurniture.co.za', '0315550303', 'Durban')

ON DUPLICATE KEY UPDATE
supplier_name = VALUES(supplier_name),
contact_person = VALUES(contact_person),
email = VALUES(email),
phone = VALUES(phone),
address = VALUES(address);


-- =====================================================
-- 2. PRODUCTS
-- =====================================================

INSERT INTO products
(product_id, supplier_id, product_name, category, sku,
 description, unit_price, quantity_in_stock, reorder_level)
VALUES

(1, 1, 'Modern Ceramic Vase', 'Home Decor', 'KH001',
 'Decorative ceramic vase', 249.99, 35, 10),

(2, 1, 'Luxury Throw Blanket', 'Bedding', 'KH002',
 'Soft premium throw blanket', 399.99, 8, 15),

(3, 2, 'Oak Coffee Table', 'Furniture', 'KH003',
 'Modern oak coffee table', 2499.99, 12, 5),

(4, 2, 'Linen Cushion Set', 'Home Decor', 'KH004',
 'Set of two linen cushions', 299.99, 50, 10),

(5, 3, 'Dining Chair', 'Furniture', 'KH005',
 'Contemporary wooden dining chair', 899.99, 21, 5),

(6, 3, 'Ceramic Dinner Set', 'Kitchenware', 'KH006',
 'Six-piece ceramic dinner set', 599.99, 20, 8)

ON DUPLICATE KEY UPDATE
supplier_id = VALUES(supplier_id),
product_name = VALUES(product_name),
category = VALUES(category),
sku = VALUES(sku),
description = VALUES(description),
unit_price = VALUES(unit_price),
quantity_in_stock = VALUES(quantity_in_stock),
reorder_level = VALUES(reorder_level);


-- =====================================================
-- 3. DELIVERIES
-- =====================================================

INSERT INTO deliveries
(delivery_id, supplier_id, delivery_reference,
 expected_date, actual_date, delivery_status, notes)
VALUES

(1, 1, 'DEL-1001', '2026-11-18', '2026-11-18',
 'Delivered', 'Delivered on time'),

(2, 2, 'DEL-1002', '2026-11-22', NULL,
 'In Transit', 'Shipment currently in transit'),

(3, 3, 'DEL-1003', '2026-11-19', NULL,
 'Delayed', 'Supplier reported a transport delay'),

(4, 1, 'DEL-1004', '2026-11-25', NULL,
 'Pending', 'Awaiting dispatch'),

(5, 2, 'DEL-1005', '2026-11-16', '2026-11-16',
 'Delivered', 'Delivery received successfully')

ON DUPLICATE KEY UPDATE
supplier_id = VALUES(supplier_id),
delivery_reference = VALUES(delivery_reference),
expected_date = VALUES(expected_date),
actual_date = VALUES(actual_date),
delivery_status = VALUES(delivery_status),
notes = VALUES(notes);
