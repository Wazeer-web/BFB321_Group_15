# BFB321 – Group 15
## Kopano Home & Lifestyle Inventory Dashboard

## Group Members

| Name and Surname | Student Number | Contribution |
|---|---|---|
| Wazeer Parker | U21529320 | 33.33% |
| Fayyad Gani | U23629968 | 33.33% |
| Ilma Osman | U23528037 | 33.33% |

---

## 1. Project Description

The Kopano Home & Lifestyle Inventory Dashboard is an inventory-management application developed for the BFB321 project.

The system is designed to support inventory monitoring, stock management, supplier information, delivery tracking and Economic Order Quantity (EOQ) calculations.

The application uses a Flask backend connected to a MySQL relational database. Data is retrieved and updated through REST API endpoints, allowing dashboard information to reflect database records.

The project also includes a standalone Python EOQ model with automated unit tests.

## 2. System Features

### Inventory Management
- Inventory overview and stock-level monitoring.
- Product search and sorting.
- Stock quantity updates saved to MySQL.
- Product creation, editing and deletion through the API.
- Automated low-stock identification.
- CSV export of inventory data.

### Supplier Management
- Supplier information and contact details.
- Supplier creation, retrieval, updating and deletion through the API.

### Delivery Management
- Delivery tracking and status monitoring.
- Delivery creation, retrieval, updating and deletion through the API.
- Delivery exception and status updates from the dashboard.

### Dashboard and Calculations
- Live dashboard statistics retrieved from the database.
- Inventory and delivery summaries.
- Economic Order Quantity (EOQ) calculator.
- Standalone Python EOQ calculation model.
- Automated unit and API validation tests.

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

The database consists of three related tables.

### Suppliers
Stores supplier names and contact information.

- Primary key: `supplier_id`
- Unique field: `email`

### Products
Stores product details, categories, SKUs, prices and stock quantities.

- Primary key: `product_id`
- Foreign key: `supplier_id`, referencing `suppliers.supplier_id`
- Unique field: `sku`

### Deliveries
Stores delivery references, expected dates, actual dates, statuses and notes.

- Primary key: `delivery_id`
- Foreign key: `supplier_id`, referencing `suppliers.supplier_id`
- Unique field: `delivery_reference`

### Relationships

- One supplier can supply multiple products.
- One supplier can be associated with multiple deliveries.
- Each product belongs to one supplier.
- Each delivery is associated with one supplier.

The database includes primary keys, foreign keys, unique constraints, CHECK constraints, indexes and `created_at` and `updated_at` timestamp fields.

### Entity Relationship Diagram

The Entity Relationship Diagram is available at:

`database/ERD-Diagram.png`

### Database Files

| File | Purpose |
|---|---|
| `database/schema.sql` | Creates the database tables, constraints and indexes |
| `database/seed.sql` | Inserts sample suppliers, products and deliveries |

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
├── scripts/
│   ├── backup_database.ps1
│   └── restore_database.ps1
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── templates/
│   ├── contents.html
│   └── index.html
│
└── tests/
    ├── test_api.py
    └── test_eoq.py
```

The `.env` file, virtual environment, application log and database backups are kept locally and excluded from version control.

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

```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a copy of `.env.example` and name it `.env`.

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter your local MySQL credentials and application configuration.

Example:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=kopano_inventory
DB_PORT=3306
FLASK_ENV=development
SECRET_KEY=replace_with_a_secure_random_key
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

```powershell
python app.py
```

Open the dashboard in a browser:

`http://127.0.0.1:5000/`

The contents page is available at:

`http://127.0.0.1:5000/contents`

## 7. REST API Endpoints

The Flask application provides REST API endpoints for inventory, suppliers, deliveries and dashboard information.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/products` | Retrieve products with pagination and filtering |
| GET | `/api/products/low-stock` | Retrieve low-stock products |
| POST | `/api/products` | Create a product |
| PUT | `/api/products/<id>` | Update a product |
| DELETE | `/api/products/<id>` | Delete a product |
| GET | `/api/suppliers` | Retrieve suppliers |
| POST | `/api/suppliers` | Create a supplier |
| PUT | `/api/suppliers/<id>` | Update a supplier |
| DELETE | `/api/suppliers/<id>` | Delete a supplier |
| GET | `/api/deliveries` | Retrieve deliveries |
| POST | `/api/deliveries` | Create a delivery |
| PUT | `/api/deliveries/<id>` | Update a delivery |
| DELETE | `/api/deliveries/<id>` | Delete a delivery |
| GET | `/api/dashboard/summary` | Retrieve dashboard summary statistics |

The API uses JSON for data exchange and communicates with the MySQL database.

The product listing endpoint supports pagination and filtering. Input validation, parameterised database queries and centralised API error responses are implemented.

## 8. EOQ Model and Automated Testing

The project includes a standalone Python EOQ model located in:

`models/eoq.py`

The model provides calculations for:

- Economic Order Quantity.
- Number of orders per year.
- Total annual ordering and holding costs.

Automated tests are located in:

- `tests/test_eoq.py`
- `tests/test_api.py`

The EOQ tests check calculation accuracy and invalid input handling. The API tests check request validation, pagination, HTTP errors and invalid data.

Run all tests using:

```powershell
python -m unittest discover -s tests -v
```

The current test suite contains 15 passing tests.

## 9. Configuration and Security

The project uses environment variables to manage database credentials and application configuration.

- `.env` stores local database credentials.
- `.env.example` provides a configuration template.
- `config.py` defines development, testing and production configurations.
- `.gitignore` prevents sensitive environment files and unnecessary generated files from being committed.
- Parameterised SQL queries are used for database operations.
- Flask logging records application errors.
- API validation checks incoming data before database operations.

## 10. Operational Impact and Sustainability

The Kopano Home & Lifestyle Inventory Dashboard is intended to improve inventory-management processes by centralising product, supplier and delivery information.

The following operational improvements are supported by the implemented system:

| Area | Manual process | Dashboard-supported process |
|---|---|---|
| Inventory visibility | Checking stock records separately | Centralised inventory dashboard |
| Low-stock monitoring | Manually checking quantities | Automated low-stock identification |
| Stock updates | Manual recording | Updates saved directly to MySQL |
| Delivery tracking | Separate delivery records | Centralised delivery status monitoring |
| Purchasing decisions | Manual quantity calculations | EOQ calculations to support ordering decisions |

### Sustainability Considerations

The system can support more efficient resource management through:

- Better stock visibility, which can help identify excess or insufficient inventory.
- Low-stock monitoring, which can help reduce the risk of stock shortages.
- EOQ calculations, which can support more informed ordering decisions.
- Centralised records, which reduce reliance on separate manual tracking processes.

These are expected operational benefits based on the implemented functionality. No quantified before-and-after time savings, cost reductions or environmental improvements were measured during the project.

### Future Scalability

The application provides a foundation that could be extended with:

- Additional product and supplier records.
- User authentication and role-based access.
- More detailed inventory reporting.
- Automated reorder notifications.
- Integration with additional business systems.

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

### Logging

The application records errors through Python logging. Log information is written to the terminal and `kopano.log`.

### Production Deployment Considerations

Before production deployment:

- Configure production environment variables and a secure Flask secret key.
- Disable Flask debug mode.
- Use a production-ready WSGI server.
- Restrict database access and use appropriate database permissions.
- Store database backups securely.
- Test database recovery procedures.
- Monitor application logs and database availability.

## 12. Team Collaboration

The project was developed collaboratively by the three group members.

| Team Member | Student Number | Main Responsibility |
|---|---|---|
| Wazeer Parker | U21529320 | Web application development, backend implementation, database integration and testing |
| Fayyad Gani | U23629968 | Report research, preparation and documentation |
| Ilma Osman | U23528037 | Report research, preparation and documentation |

Git and GitHub were used for version control and project collaboration.

