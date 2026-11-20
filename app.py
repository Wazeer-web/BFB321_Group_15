"""Kopano Home & Lifestyle - Flask REST API and dashboard routes.

Requires the existing db.py and .env configuration. Never commit .env.
"""

from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps
import logging
import os

from flask import Flask, jsonify, render_template, request
from mysql.connector import IntegrityError

from db import get_db_connection
from config import configurations

app = Flask(__name__)

environment = os.getenv("FLASK_ENV", "development").lower()

app.config.from_object(
    configurations.get(environment, configurations["development"])
)

app.config["JSON_SORT_KEYS"] = False

# Log application errors to the terminal and to kopano.log.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
if not any(isinstance(handler, logging.FileHandler) for handler in app.logger.handlers):
    file_handler = logging.FileHandler("kopano.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    ))
    app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

DELIVERY_STATUSES = {"Pending", "In Transit", "Delivered", "Delayed", "Cancelled"}


# -----------------------------------------------------------------------------
# SHARED HELPERS
# -----------------------------------------------------------------------------

def close_database(connection=None, cursor=None):
    """Close a cursor and connection safely."""
    try:
        if cursor is not None:
            cursor.close()
    except Exception:
        app.logger.exception("Could not close database cursor")

    try:
        if connection is not None and connection.is_connected():
            connection.close()
    except Exception:
        app.logger.exception("Could not close database connection")


def api_error(message, status_code):
    return jsonify({"error": message}), status_code


def get_json_object():
    """Return a JSON object, or (None, error_response)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, api_error("A JSON object is required", 400)
    return data, None


def validate_non_empty_string(data, field, required=False, max_length=None):
    if field not in data:
        return f"Missing required field: {field}" if required else None
    value = data[field]
    if not isinstance(value, str) or not value.strip():
        return f"{field} must be a non-empty string"
    if max_length is not None and len(value.strip()) > max_length:
        return f"{field} must not exceed {max_length} characters"
    return None


def validate_integer(data, field, required=False, minimum=0):
    if field not in data:
        return f"Missing required field: {field}" if required else None
    value = data[field]
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        return f"{field} must be an integer greater than or equal to {minimum}"
    return None


def validate_money(data, field, required=False):
    if field not in data:
        return f"Missing required field: {field}" if required else None
    value = data[field]
    if isinstance(value, bool):
        return f"{field} must be a non-negative number"
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return f"{field} must be a valid number"
    if not amount.is_finite() or amount < 0:
        return f"{field} must be a non-negative number"
    return None


def validate_date(value, field, allow_none=False):
    if value is None and allow_none:
        return None
    if not isinstance(value, str):
        return f"{field} must be a date in YYYY-MM-DD format"
    try:
        date.fromisoformat(value)
    except ValueError:
        return f"{field} must be a valid date in YYYY-MM-DD format"
    return None


def validate_product_payload(data, creating=False):
    required = ["supplier_id", "product_name", "category", "sku",
                "unit_price", "quantity_in_stock", "reorder_level"] if creating else []
    for field in required:
        if field not in data:
            return f"Missing required field: {field}"

    checks = [
        validate_integer(data, "supplier_id", required=creating, minimum=1),
        validate_non_empty_string(data, "product_name", required=creating, max_length=150),
        validate_non_empty_string(data, "category", required=creating, max_length=100),
        validate_non_empty_string(data, "sku", required=creating, max_length=50),
        validate_money(data, "unit_price", required=creating),
        validate_integer(data, "quantity_in_stock", required=creating),
        validate_integer(data, "reorder_level", required=creating),
    ]
    for error in checks:
        if error:
            return error

    if "description" in data and data["description"] is not None and not isinstance(data["description"], str):
        return "description must be a string or null"
    return None


def validate_supplier_payload(data, creating=False):
    if creating:
        error = validate_non_empty_string(data, "supplier_name", required=True, max_length=100)
        if error:
            return error
    for field, max_length in (("supplier_name", 100), ("contact_person", 100),
                              ("email", 150), ("phone", 20), ("address", 255)):
        error = validate_non_empty_string(data, field, max_length=max_length)
        if error:
            return error
    return None


def validate_delivery_payload(data, creating=False):
    if creating:
        required_fields = ["supplier_id", "delivery_reference", "expected_date"]
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"

    if "supplier_id" in data:
        error = validate_integer(data, "supplier_id", minimum=1)
        if error:
            return error

    if "delivery_reference" in data:
        error = validate_non_empty_string(data, "delivery_reference", max_length=50)
        if error:
            return error

    if "delivery_status" in data:
        status = data["delivery_status"]
        if not isinstance(status, str) or status not in DELIVERY_STATUSES:
            return "delivery_status must be one of: " + ", ".join(sorted(DELIVERY_STATUSES))

    if "expected_date" in data:
        error = validate_date(data["expected_date"], "expected_date")
        if error:
            return error

    if "actual_date" in data:
        error = validate_date(data["actual_date"], "actual_date", allow_none=True)
        if error:
            return error

    if "notes" in data:
        if data["notes"] is not None and not isinstance(data["notes"], str):
            return "notes must be a string or null"
        if data["notes"] is not None and len(data["notes"]) > 250:
            return "notes must not exceed 250 characters"

    return None


def run_db_read(query, params=(), fetch="all"):
    """Execute a read query and always close its resources."""
    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        return cursor.fetchone() if fetch == "one" else cursor.fetchall()
    finally:
        close_database(connection, cursor)


# -----------------------------------------------------------------------------
# PAGE ROUTES
# -----------------------------------------------------------------------------

@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/contents")
def contents():
    return render_template("contents.html")


# -----------------------------------------------------------------------------
# PRODUCT API
# -----------------------------------------------------------------------------

@app.route("/api/products", methods=["GET"])
def get_products():
    connection = cursor = None
    try:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)
        search = request.args.get("search", default="", type=str).strip()
        category = request.args.get("category", default="", type=str).strip()
        if page < 1 or per_page < 1 or per_page > 100:
            return api_error("page must be at least 1 and per_page must be between 1 and 100", 400)

        conditions, params = [], []
        if search:
            conditions.append("(p.product_name LIKE %s OR p.sku LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        if category:
            conditions.append("p.category = %s")
            params.append(category)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT COUNT(*) AS total FROM products p{where}", tuple(params))
        total = cursor.fetchone()["total"]
        cursor.execute(f"""
            SELECT p.product_id, p.product_name, p.category, p.sku, p.description,
                   p.unit_price, p.quantity_in_stock, p.reorder_level,
                   p.supplier_id, s.supplier_name
            FROM products p
            INNER JOIN suppliers s ON p.supplier_id = s.supplier_id
            {where}
            ORDER BY p.product_id
            LIMIT %s OFFSET %s
        """, tuple(params + [per_page, (page - 1) * per_page]))
        products = cursor.fetchall()
        return jsonify({
            "data": products,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        }), 200
    except Exception:
        app.logger.exception("Failed to retrieve products")
        return api_error("Unable to retrieve products", 500)
    finally:
        close_database(connection, cursor)


@app.route("/api/products/low-stock", methods=["GET"])
def get_low_stock_products():
    try:
        rows = run_db_read("""
            SELECT p.product_id, p.product_name, p.category, p.sku,
                   p.quantity_in_stock, p.reorder_level, s.supplier_name
            FROM products p
            INNER JOIN suppliers s ON p.supplier_id = s.supplier_id
            WHERE p.quantity_in_stock <= p.reorder_level
            ORDER BY p.quantity_in_stock ASC
        """)
        return jsonify(rows), 200
    except Exception:
        app.logger.exception("Failed to retrieve low-stock products")
        return api_error("Unable to retrieve low-stock products", 500)


@app.route("/api/products", methods=["POST"])
def create_product():
    data, error_response = get_json_object()
    if error_response:
        return error_response
    error = validate_product_payload(data, creating=True)
    if error:
        return api_error(error, 400)

    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO products
                (supplier_id, product_name, category, sku, description,
                 unit_price, quantity_in_stock, reorder_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["supplier_id"], data["product_name"].strip(),
            data["category"].strip(), data["sku"].strip(),
            data.get("description"), data["unit_price"],
            data["quantity_in_stock"], data["reorder_level"],
        ))
        new_id = cursor.lastrowid
        connection.commit()
        return jsonify({"message": "Product created successfully", "product_id": new_id}), 201
    except IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return api_error("Duplicate SKU or invalid supplier ID", 409)
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Failed to create product")
        return api_error("Unable to create product", 500)
    finally:
        close_database(connection, cursor)


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data, error_response = get_json_object()
    if error_response:
        return error_response
    if not data:
        return api_error("At least one field must be supplied", 400)
    error = validate_product_payload(data)
    if error:
        return api_error(error, 400)

    allowed = {"supplier_id", "product_name", "category", "sku", "description",
               "unit_price", "quantity_in_stock", "reorder_level"}
    fields = [field for field in data if field in allowed]
    if not fields:
        return api_error("No updatable fields supplied", 400)

    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        assignments = ", ".join(f"{field} = %s" for field in fields)
        values = [data[field].strip() if isinstance(data[field], str) else data[field]
                  for field in fields]
        cursor.execute(f"UPDATE products SET {assignments} WHERE product_id = %s",
                       tuple(values + [product_id]))
        if cursor.rowcount == 0:
            cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
            if cursor.fetchone() is None:
                return api_error("Product not found", 404)
        connection.commit()
        return jsonify({"message": "Product updated successfully", "product_id": product_id}), 200
    except IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return api_error("Duplicate SKU or invalid supplier ID", 409)
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Failed to update product %s", product_id)
        return api_error("Unable to update product", 500)
    finally:
        close_database(connection, cursor)


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        if cursor.rowcount == 0:
            return api_error("Product not found", 404)
        connection.commit()
        return jsonify({"message": "Product deleted successfully", "product_id": product_id}), 200
    except IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return api_error("This product is referenced by other records and cannot be deleted", 409)
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Failed to delete product %s", product_id)
        return api_error("Unable to delete product", 500)
    finally:
        close_database(connection, cursor)


# -----------------------------------------------------------------------------
# SUPPLIER API
# -----------------------------------------------------------------------------

@app.route("/api/suppliers", methods=["GET"])
def get_suppliers():
    try:
        rows = run_db_read("""
            SELECT supplier_id, supplier_name, contact_person, email, phone, address
            FROM suppliers ORDER BY supplier_id
        """)
        return jsonify(rows), 200
    except Exception:
        app.logger.exception("Failed to retrieve suppliers")
        return api_error("Unable to retrieve suppliers", 500)


@app.route("/api/suppliers", methods=["POST"])
def create_supplier():
    data, error_response = get_json_object()
    if error_response:
        return error_response
    error = validate_supplier_payload(data, creating=True)
    if error:
        return api_error(error, 400)

    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO suppliers (supplier_name, contact_person, email, phone, address)
            VALUES (%s, %s, %s, %s, %s)
        """, tuple(data.get(field) for field in
                   ("supplier_name", "contact_person", "email", "phone", "address")))
        supplier_id = cursor.lastrowid
        connection.commit()
        return jsonify({"message": "Supplier created successfully", "supplier_id": supplier_id}), 201
    except IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return api_error("Supplier email already exists or supplied data violates a database constraint", 409)
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Failed to create supplier")
        return api_error("Unable to create supplier", 500)
    finally:
        close_database(connection, cursor)


@app.route("/api/suppliers/<int:supplier_id>", methods=["PUT"])
def update_supplier(supplier_id):
    data, error_response = get_json_object()
    if error_response:
        return error_response
    if not data:
        return api_error("At least one field must be supplied", 400)
    error = validate_supplier_payload(data)
    if error:
        return api_error(error, 400)
    allowed = {"supplier_name", "contact_person", "email", "phone", "address"}
    fields = [field for field in data if field in allowed]
    if not fields:
        return api_error("No updatable fields supplied", 400)

    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        assignments = ", ".join(f"{field} = %s" for field in fields)
        values = [data[field].strip() if isinstance(data[field], str) else data[field]
                  for field in fields]
        cursor.execute(f"UPDATE suppliers SET {assignments} WHERE supplier_id = %s",
                       tuple(values + [supplier_id]))
        if cursor.rowcount == 0:
            cursor.execute("SELECT supplier_id FROM suppliers WHERE supplier_id = %s", (supplier_id,))
            if cursor.fetchone() is None:
                return api_error("Supplier not found", 404)
        connection.commit()
        return jsonify({"message": "Supplier updated successfully", "supplier_id": supplier_id}), 200
    except IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return api_error("Supplier email already exists or supplied data violates a database constraint", 409)
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Failed to update supplier %s", supplier_id)
        return api_error("Unable to update supplier", 500)
    finally:
        close_database(connection, cursor)


@app.route("/api/suppliers/<int:supplier_id>", methods=["DELETE"])
def delete_supplier(supplier_id):
    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        if cursor.rowcount == 0:
            return api_error("Supplier not found", 404)
        connection.commit()
        return jsonify({"message": "Supplier deleted successfully", "supplier_id": supplier_id}), 200
    except IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return api_error("This supplier is linked to products or deliveries and cannot be deleted", 409)
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Failed to delete supplier %s", supplier_id)
        return api_error("Unable to delete supplier", 500)
    finally:
        close_database(connection, cursor)


# -----------------------------------------------------------------------------
# DELIVERY API
# -----------------------------------------------------------------------------

@app.route("/api/deliveries", methods=["GET"])
def get_deliveries():
    try:
        rows = run_db_read("""
            SELECT d.delivery_id, d.delivery_reference, d.supplier_id,
                   s.supplier_name, d.expected_date, d.actual_date,
                   d.delivery_status, d.notes
            FROM deliveries d
            INNER JOIN suppliers s ON d.supplier_id = s.supplier_id
            ORDER BY d.expected_date, d.delivery_id
        """)
        for row in rows:
            for field in ("expected_date", "actual_date"):
                if row[field] is not None:
                    row[field] = row[field].isoformat()
        return jsonify(rows), 200
    except Exception:
        app.logger.exception("Failed to retrieve deliveries")
        return api_error("Unable to retrieve deliveries", 500)


@app.route("/api/deliveries", methods=["POST"])
def create_delivery():
    data, error_response = get_json_object()
    if error_response:
        return error_response
    error = validate_delivery_payload(data, creating=True)
    if error:
        return api_error(error, 400)

    status = data.get("delivery_status", "Pending")
    if status not in DELIVERY_STATUSES:
        return api_error("Invalid delivery_status", 400)

    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO deliveries
                (supplier_id, delivery_reference, expected_date, actual_date,
                 delivery_status, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["supplier_id"], data["delivery_reference"].strip(),
            data["expected_date"], data.get("actual_date"), status,
            data.get("notes"),
        ))
        delivery_id = cursor.lastrowid
        connection.commit()
        return jsonify({"message": "Delivery created successfully", "delivery_id": delivery_id}), 201
    except IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return api_error("Duplicate delivery reference or invalid supplier ID", 409)
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Failed to create delivery")
        return api_error("Unable to create delivery", 500)
    finally:
        close_database(connection, cursor)


@app.route("/api/deliveries/<int:delivery_id>", methods=["PUT"])
def update_delivery(delivery_id):
    data, error_response = get_json_object()
    if error_response:
        return error_response
    if not data:
        return api_error("At least one field must be supplied", 400)
    error = validate_delivery_payload(data)
    if error:
        return api_error(error, 400)

    allowed = {"supplier_id", "delivery_reference", "expected_date",
               "actual_date", "delivery_status", "notes"}
    fields = [field for field in data if field in allowed]
    if not fields:
        return api_error("No updatable fields supplied", 400)

    if data.get("delivery_status") == "Delivered" and "actual_date" not in data:
        data["actual_date"] = date.today().isoformat()
        fields.append("actual_date")

    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        assignments = ", ".join(f"{field} = %s" for field in fields)
        values = [data[field].strip() if isinstance(data[field], str) else data[field]
                  for field in fields]
        cursor.execute(f"UPDATE deliveries SET {assignments} WHERE delivery_id = %s",
                       tuple(values + [delivery_id]))
        if cursor.rowcount == 0:
            cursor.execute("SELECT delivery_id FROM deliveries WHERE delivery_id = %s", (delivery_id,))
            if cursor.fetchone() is None:
                return api_error("Delivery not found", 404)
        connection.commit()
        return jsonify({"message": "Delivery updated successfully", "delivery_id": delivery_id}), 200
    except IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return api_error("Duplicate delivery reference or invalid supplier ID", 409)
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Failed to update delivery %s", delivery_id)
        return api_error("Unable to update delivery", 500)
    finally:
        close_database(connection, cursor)


@app.route("/api/deliveries/<int:delivery_id>", methods=["DELETE"])
def delete_delivery(delivery_id):
    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM deliveries WHERE delivery_id = %s", (delivery_id,))
        if cursor.rowcount == 0:
            return api_error("Delivery not found", 404)
        connection.commit()
        return jsonify({"message": "Delivery deleted successfully", "delivery_id": delivery_id}), 200
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Failed to delete delivery %s", delivery_id)
        return api_error("Unable to delete delivery", 500)
    finally:
        close_database(connection, cursor)


# -----------------------------------------------------------------------------
# DASHBOARD SUMMARY
# -----------------------------------------------------------------------------

@app.route("/api/dashboard/summary", methods=["GET"])
def get_dashboard_summary():
    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) AS total_products,
                   COALESCE(SUM(quantity_in_stock), 0) AS total_units,
                   COALESCE(SUM(CASE WHEN quantity_in_stock <= reorder_level
                                     THEN 1 ELSE 0 END), 0) AS low_stock_products,
                   COALESCE(SUM(unit_price * quantity_in_stock), 0) AS inventory_value
            FROM products
        """)
        summary = cursor.fetchone()
        return jsonify(summary), 200
    except Exception:
        app.logger.exception("Failed to retrieve dashboard summary")
        return api_error("Unable to retrieve dashboard summary", 500)
    finally:
        close_database(connection, cursor)


# -----------------------------------------------------------------------------
# CENTRAL ERROR HANDLERS
# -----------------------------------------------------------------------------

@app.errorhandler(404)
def handle_not_found(error):
    if request.path.startswith("/api/"):
        return api_error("API endpoint or resource not found", 404)
    return error


@app.errorhandler(405)
def handle_method_not_allowed(error):
    if request.path.startswith("/api/"):
        return api_error("HTTP method not allowed for this endpoint", 405)
    return error


@app.errorhandler(500)
def handle_internal_error(error):
    app.logger.exception("Unhandled server error")
    if request.path.startswith("/api/"):
        return api_error("An unexpected server error occurred", 500)
    return "An unexpected server error occurred", 500


# -----------------------------------------------------------------------------
# START DEVELOPMENT SERVER
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    environment = os.getenv("FLASK_ENV", "development").lower()

    if environment == "production":
        app.run(debug=False)
    else:
        app.run(debug=True)