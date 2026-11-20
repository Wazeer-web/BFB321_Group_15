# BFB321 — Group 15
## Kopano Home & Lifestyle Inventory Dashboard

### Group Members

| Name and Surname | Student Number |
|---|---|
| Wazeer Parker | U21529320 |
| Fayyad Gani | U23629968 |
| Ilma Osman | U23528037 |

---

## 1. Project Description

The Kopano Home & Lifestyle Inventory Dashboard is an inventory-management application developed for the BFB321 project.

The system is designed to support inventory monitoring, stock management, supplier information, delivery tracking and Economic Order Quantity (EOQ) calculations.

The application uses a Flask backend connected to a MySQL relational database. Data is retrieved and updated through REST API endpoints, allowing dashboard information to reflect database records.

The project also includes a standalone Python EOQ model with automated unit tests to verify inventory calculations.

## 2. Features

### Inventory Management
- Inventory overview and stock-level monitoring.
- Product search and sorting.
- Stock quantity updates.
- Product creation, editing and deletion through the API.
- Low-stock identification.
- CSV export of inventory data.

### Supplier Management
- Supplier information and contact details.
- Supplier creation, retrieval, updating and deletion through the API.

### Delivery Management
- Delivery tracking and status monitoring.
- Delivery creation, retrieval, updating and deletion through the API.
- Delivery exception updates from the dashboard.

### Dashboard and Calculations
- Live dashboard statistics from the database.
- Inventory and delivery summaries.
- Economic Order Quantity (EOQ) calculator.
- Standalone Python EOQ calculation model.
- Automated unit tests.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| HTML5 | Dashboard structure |
| CSS3 | Dashboard styling |
| JavaScript | Frontend functionality and API communication |
| Bootstrap 5 | Responsive interface |
| Python | Backend application and calculations |
| Flask | Web framework and REST API |
| MySQL | Relational database |
| MySQL Connector/Python | Database connectivity |
| python-dotenv | Environment variable management |
| unittest | Automated testing |
| Git and GitHub | Version control and collaboration |

## 4. Database Design

The application uses a MySQL database named `kopano_inventory`.

The database consists of three related tables:

**Suppliers**
- Stores supplier names and contact information.
- Primary key: `supplier_id`.

**Products**
- Stores product details, categories, SKUs, prices and stock quantities.
- Primary key: `product_id`.
- Foreign key: `supplier_id`, referencing the suppliers table.

**Deliveries**
- Stores delivery references, expected dates, actual dates, statuses and notes.
- Primary key: `delivery_id`.
- Foreign key: `supplier_id`, referencing the suppliers table.

### Entity Relationship Diagram

The ERD is available in:

`database/ERD-Diagram.png`

### Database Files

| File | Purpose |
|---|---|
| `database/schema.sql` | Creates the database tables, constraints and indexes. |
| `database/seed.sql` | Inserts sample suppliers, products and deliveries. |

## 5. Project Structure

```text
BFB321_Group_15/
│
├── app.py
├── config.py
├── db.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── database/
│   ├── ERD-Diagram.png
│   ├── schema.sql
│   └── seed.sql
│
├── models/
│   └── eoq.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── templates/
│   ├── index.html
│   └── contents.html
│
└── tests/
    └── test_eoq.py
```

The `.env` file and virtual environment are kept locally and are excluded from version control.

## 6. Setup and Installation

### Prerequisites

Install the following software:

- Python 3
- MySQL Server 8.0 or later
- Git
- A web browser

### Step 1: Clone the Repository

```bash
git clone https://github.com/Wazeer-web/BFB321_Group_15.git
```

Navigate into the project directory:

```bash
cd BFB321_Group_15
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a copy of `.env.example` and name it `.env`.

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter your local MySQL credentials.

Example:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=kopano_inventory
DB_PORT=3306
```

The `.env` file contains local credentials and must not be committed to GitHub.

### Step 5: Set Up the Database

Open MySQL Workbench or another MySQL client.

Execute the SQL files in this order:

1. `database/schema.sql`
2. `database/seed.sql`

This creates the database tables and inserts the sample data.

**Important:** The seed file is intended for initial database setup. Running it again can restore the sample records over later changes.

### Step 6: Run the Application

Activate the virtual environment and execute:

```bash
python app.py
```

Open the dashboard in a browser:

```text
http://127.0.0.1:5000/
```

The contents page is available at:

```text
http://127.0.0.1:5000/contents
```

## 7. REST API Endpoints

The Flask application provides REST API endpoints for inventory, suppliers, deliveries and dashboard information.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/products` | Retrieve products with pagination and filtering. |
| GET | `/api/products/low-stock` | Retrieve low-stock products. |
| POST | `/api/products` | Create a product. |
| PUT | `/api/products/<id>` | Update a product. |
| DELETE | `/api/products/<id>` | Delete a product. |
| GET | `/api/suppliers` | Retrieve suppliers. |
| POST | `/api/suppliers` | Create a supplier. |
| PUT | `/api/suppliers/<id>` | Update a supplier. |
| DELETE | `/api/suppliers/<id>` | Delete a supplier. |
| GET | `/api/deliveries` | Retrieve deliveries. |
| POST | `/api/deliveries` | Create a delivery. |
| PUT | `/api/deliveries/<id>` | Update a delivery. |
| DELETE | `/api/deliveries/<id>` | Delete a delivery. |
| GET | `/api/dashboard/summary` | Retrieve dashboard summary statistics. |

The API uses JSON for data exchange and communicates with the MySQL database.

## 8. EOQ Model and Testing

The project includes a standalone Python EOQ model located in:

`models/eoq.py`

The model provides calculations for:

- Economic Order Quantity.
- Number of orders per year.
- Total annual ordering and holding costs.

Automated unit tests are located in:

`tests/test_eoq.py`

Run the tests using:

```bash
python -m unittest discover -s tests -v
```

The tests cover calculation accuracy and input validation.

## 9. Configuration and Security

The project uses environment variables to manage database credentials.

- `.env` stores local database credentials.
- `.env.example` provides a configuration template.
- `.gitignore` prevents sensitive environment files and unnecessary generated files from being committed.
- Parameterized SQL queries are used for database operations.
- Flask logging is used to record application activity and errors.

## 10. Current Development Status

The application has progressed from a frontend prototype to a Flask and MySQL integrated system.

Completed functionality includes:

- MySQL database with three related tables.
- Database connectivity through Flask.
- REST API operations for products, suppliers and deliveries.
- Dashboard data retrieved from the database.
- Stock updates saved to MySQL.
- Delivery status updates saved to MySQL.
- EOQ model and automated unit tests.

Further deployment documentation, backup and recovery procedures, and final integration checks form part of the project completion process.

## 11. Deployment, Backup and Recovery

### Database Backup

The project includes a PowerShell backup script located at:

`scripts/backup_database.ps1`

The script uses MySQL's `mysqldump` utility to create a timestamped SQL backup of the `kopano_inventory` database.

To create a backup, run:

```powershell
.\scripts\backup_database.ps1
```

The script prompts for the MySQL password and saves the backup in the `backups/` directory.

### Database Recovery

A database recovery script is provided at:

`scripts/restore_database.ps1`

To restore a previous backup, run:

```powershell
.\scripts\restore_database.ps1
```

The user selects an existing backup file and must explicitly confirm the recovery operation.

**Warning:** Restoring a database backup can overwrite existing database records. A backup of the current database should be created before performing a recovery.

### Environment Configuration

Database credentials are stored in a local `.env` file and are excluded from version control.

The `.env.example` file provides a template for configuring the application on another computer.

### Logging

The application records activity and errors through Python logging. Log information is written to the terminal and `kopano.log`.

### Deployment Considerations

Before production deployment:

- Configure production environment variables and a secure Flask secret key.
- Disable Flask debug mode.
- Use a production-ready WSGI server.
- Restrict database access and use appropriate database permissions.
- Store database backups securely.
- Test database recovery procedures.
- Monitor application logs and database availability.

## 12. Team Contributions

| Team Member | Student Number | Contribution |
|---|---|---|
| Wazeer Parker | U21529320 | 33.33 |
| Fayyad Gani | U23629968 | 33.33 |
| Ilma Osman | U23528037 | 33.33 |

