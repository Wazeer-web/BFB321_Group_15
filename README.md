# BFB321 Group 15
## Kopano Home & Lifestyle Inventory Dashboard

A web-based inventory dashboard developed for the BFB321 project. The system brings product stock information, supplier records and delivery information together in one place. It also includes an Economic Order Quantity (EOQ) calculator to support inventory ordering decisions.

## Group members

| Name | Student number | Main contribution |
|---|---|---|
| Wazeer Parker | U21529320 | Web application development, backend implementation, database integration and testing |
| Fayyad Gani | U23629968 | Backend implementation, report preparation and documentation |
| Ilma Osman | U23528037 | database intergration, report preparation and documentation |

All three group members participated in developing the Kopano Home & Lifestyle inventory management application. The group worked collaboratively on a shared laptop, using Wazeer Parker’s GitHub account to manage and upload the project files.

As a result, the GitHub commit history mainly reflects one account, although the development work was completed collectively. The group collaborated on the application functionality, database integration, testing and documentation.

All members contributed to discussions, problem-solving and reviewing the final application.
## What the system does

### Inventory
- Displays products, stock quantities and reorder levels.
- Allows users to search and sort product information.
- Supports stock quantity updates, which are saved to the MySQL database.
- Identifies products that are below their reorder level.
- Includes a CSV export option.

### Suppliers
- Stores supplier names and contact information.
- Provides API operations to create, view, update and delete supplier records.

### Deliveries
- Stores delivery references, expected and actual dates, statuses and notes.
- Provides API operations to create, view, update and delete delivery records.
- Displays delivery information and status details in the application.

The delivery records in the project are sample/illustrative records. The application is not connected to a live courier or shipment-tracking service.

### Dashboard and EOQ
- Displays summary information from the database, including product and stock figures.
- Includes an EOQ calculator.
- Calculates Economic Order Quantity, the number of orders per year, and annual ordering and holding costs.

## Technologies

| Technology | How it is used |
|---|---|
| Python and Flask | Backend application and REST API |
| MySQL | Stores products, suppliers and deliveries |
| HTML and CSS | Page structure and styling |
| JavaScript | Dashboard behaviour and API communication |
| Bootstrap 5 | Layout and responsive components |
| MySQL Connector/Python | Connects Flask to MySQL |
| python-dotenv | Loads local environment settings |
| `unittest` | Automated tests |
| Git and GitHub | Version control |

## Database

The MySQL database is named `kopano_inventory` and contains three main tables:

- **suppliers** – supplier names and contact details.
- **products** – product details, SKUs, prices, stock quantities and supplier references.
- **deliveries** – delivery references, dates, statuses, notes and supplier references.

The tables are connected using primary and foreign keys. The database also uses unique constraints, CHECK constraints, indexes and timestamp fields.

The Entity Relationship Diagram is saved in `database/ERD-Diagram.png`.

Database setup files:

| File | Purpose |
|---|---|
| `database/schema.sql` | Creates the database and tables |
| `database/seed.sql` | Adds the sample suppliers, products and deliveries |

## Project files

```text
BFB321_Group_15/
├── app.py
├── config.py
├── db.py
├── requirements.txt
├── README.md
├── .env.example
├── database/
│   ├── ERD-Diagram.png
│   ├── schema.sql
│   └── seed.sql
├── models/
│   └── eoq.py
├── scripts/
│   ├── backup_database.ps1
│   └── restore_database.ps1
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   ├── contents.html
│   └── index.html
└── tests/
    ├── test_api.py
    └── test_eoq.py
```

The local `.env` file, virtual environment, log file and database backups are excluded from Git.

## Installation and running the application

### Requirements

Install the following first:

- Python 3
- MySQL Server 8.0 or later
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Wazeer-web/BFB321_Group_15.git
cd BFB321_Group_15
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install the Python packages

```powershell
pip install -r requirements.txt
```

### 4. Set up the environment file

Copy `.env.example` and rename the copy to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter the details for your local MySQL setup. The values should follow this format:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=kopano_inventory
DB_PORT=3306
FLASK_ENV=development
SECRET_KEY=replace_with_a_secure_random_key
```

Use your own MySQL password and a secure secret key. Do not upload `.env` to GitHub because it can contain private credentials.

### 5. Create and populate the database

Open MySQL Workbench or another MySQL client and run these files in order:

1. `database/schema.sql`
2. `database/seed.sql`

The first file creates the database structure. The second adds the sample records. The seed file is intended for initial setup; running it again may affect records that have been changed since setup.

### 6. Start the application

With the virtual environment activated, run:

```powershell
python app.py
```

Open the dashboard at:

`http://127.0.0.1:5000/`

The contents page is available at:

`http://127.0.0.1:5000/contents`

## REST API

The Flask backend provides endpoints for products, suppliers, deliveries and dashboard information.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/products` | Get products, with pagination and filtering |
| GET | `/api/products/low-stock` | Get products below their reorder levels |
| POST | `/api/products` | Create a product |
| PUT | `/api/products/<id>` | Update a product |
| DELETE | `/api/products/<id>` | Delete a product |
| GET | `/api/suppliers` | Get suppliers |
| POST | `/api/suppliers` | Create a supplier |
| PUT | `/api/suppliers/<id>` | Update a supplier |
| DELETE | `/api/suppliers/<id>` | Delete a supplier |
| GET | `/api/deliveries` | Get deliveries |
| POST | `/api/deliveries` | Create a delivery |
| PUT | `/api/deliveries/<id>` | Update a delivery |
| DELETE | `/api/deliveries/<id>` | Delete a delivery |
| GET | `/api/dashboard/summary` | Get dashboard summary figures |

The API exchanges data using JSON. The application includes input validation, parameterised database queries and API error handling.

## EOQ model and tests

The EOQ calculation is in `models/eoq.py`. It calculates:

- Economic Order Quantity.
- Number of orders per year.
- Annual ordering and holding costs.

The automated tests are in `tests/test_eoq.py` and `tests/test_api.py`. They cover EOQ calculations and invalid inputs, as well as API validation, pagination and error responses.

To run the tests:

```powershell
python -m unittest discover -s tests -v
```

At the time this README was prepared, all 15 tests in the test suite passed.

## Configuration, backups and logging

- `.env.example` shows which environment variables need to be configured.
- `.env` holds local settings and should not be committed.
- `config.py` contains the application configuration.
- The application uses parameterised SQL queries and validates incoming API data.
- Application errors are recorded using Python logging.

PowerShell scripts are included for database backup and recovery:

```powershell
.\scripts\backup_database.ps1
```

```powershell
.\scripts\restore_database.ps1
```

The backup script creates a timestamped SQL backup in the `backups/` folder. The restore script asks the user to select a backup and confirm the restore. Restoring a backup can overwrite current database records, so make a backup of the current database first.

For a production setup, the application would still need production hosting, a production-ready WSGI server, secure database permissions and appropriate monitoring. The project is currently intended to be run locally for demonstration and assessment.

## Project impact and possible improvements

The dashboard brings inventory, supplier and delivery information into one application. Low-stock indicators make it easier to spot products that may need reordering, while the EOQ calculator gives users a way to compare ordering and holding costs when planning stock.

These are intended benefits of the implemented features. We did not measure actual reductions in costs, processing time or environmental impact, so no quantified savings are claimed.

Possible future improvements include:
- Adding user accounts and different access levels.
- Connecting the delivery section to a live tracking service.
- Adding automatic low-stock notifications.
- Expanding the reporting and analytics features.
- Connecting the system to other business applications.

## Version control

Git and GitHub were used to keep track of project changes. The repository contains the application code, database scripts, tests and setup instructions.