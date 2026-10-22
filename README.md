# BFB321 — Group 15
## Kopano Home & Lifestyle Inventory Dashboard

### Group Members

| Name and Surname | Student Number |
|---|---|
| Wazeer Parker | U21529320 |
| Fayyad Gani | U23629968 |
| Ilma Osman | U23528037 |

### Project Description

The Kopano Home & Lifestyle Inventory Dashboard is a frontend inventory-management dashboard designed to demonstrate inventory monitoring, stock updates, supplier information, delivery tracking, and Economic Order Quantity (EOQ) calculations.

The project also includes a standalone Python EOQ model with unit tests to verify the inventory calculations.

**Important:** The dashboard currently uses simulated data. It is a prototype and is not connected to a live database or backend.

### Features

- Inventory overview and stock-level monitoring
- Inventory search and sorting
- Stock quantity updates
- CSV export of inventory data
- Delivery and logistics tracking
- Supplier information
- Economic Order Quantity (EOQ) calculator
- Standalone Python EOQ calculation model
- Automated unit tests for the EOQ model

### Project Structure

```text
BFB321_Group_15/
├── index.html
├── contents.html
├── style.css
├── app.js
├── models/
│   └── eoq.py
└── tests/
    └── test_eoq.py
```

### Setup and Installation

**Frontend dashboard**

1. Download or clone this repository.
2. Open the project folder.
3. Open `index.html` in a web browser.
4. An internet connection is required to load Bootstrap from its CDN.

**Python EOQ model and tests**

1. Install Python 3.
2. Open a terminal in the project folder.
3. Run the unit tests using:

```bash
python -m unittest discover -s tests -v
```

The tests check the EOQ calculation, expected orders per year, annual ordering and holding costs, and input validation.

### Limitations

The frontend uses simulated data, and updates are not saved permanently. The Python model runs independently and does not currently connect to the frontend or a database.

### Technologies Used

- HTML
- CSS
- JavaScript
- Bootstrap 5
- Python
- Python `unittest`
