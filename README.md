# Dynamic Catalogue Manager

🎯 **A powerful desktop application for creating and managing custom catalogues with user-defined column structures**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)](https://pypi.org/project/PyQt6/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Dynamic Catalogue Manager](https://via.placeholder.com/800x400/366092/FFFFFF?text=Dynamic+Catalogue+Manager)

## ✨ What Makes This Special

Unlike traditional catalogue applications with fixed fields, **Dynamic Catalogue Manager** lets YOU define exactly what columns and data types you need. Whether you're managing crafting supplies, book collections, inventory, or any other items, this application adapts to your specific requirements.

## Features

- **Manual Entry**: Add crafting components with detailed information
- **Excel Import**: Import existing component lists from Excel files
- **Edit & Delete**: Modify or remove components from your catalogue
- **Search & Filter**: Find components by name, category, or description
- **Export Options**: Save catalogue to Excel or PDF formats
- **Print Support**: Generate printable PDF catalogues
- **Data Persistence**: SQLite database for reliable data storage

## Requirements

- Python 3.8 or higher
- PyQt6
- pandas
- openpyxl
- reportlab

## Installation

1. Clone or download this project
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### Adding Components

1. Fill in the component details in the left panel
2. Click "Add Component" to save to the database

### Importing from Excel

1. Click "Import from Excel" button
2. Select your Excel file
3. The file should have columns like: Name, Category, Description, Quantity, Unit, Cost per Unit, Supplier, Location, Notes
4. Components will be automatically imported

### Exporting Data

- **Excel Export**: Click "Export to Excel" to save all components
- **PDF Export**: Click "Print Catalogue" to generate a PDF report

### Searching and Filtering

- Use the search box to find components by name, category, or description
- Use the category filter dropdown to show only specific categories

## Excel Import Format

Your Excel file should contain the following columns (case-insensitive):
- **Name** (required): Component name
- **Category**: Component category/type
- **Description**: Detailed description
- **Quantity**: Number of items
- **Unit**: Measurement unit (pieces, meters, etc.)
- **Cost per Unit**: Price per individual item
- **Supplier**: Where to buy the component
- **Location**: Storage location
- **Notes**: Additional notes

## Database

The application uses SQLite database stored in `data/crafting_catalogue.db`. The database is created automatically on first run.

## Project Structure

```
crafting-catalogue/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── gui/
│   │   └── main_window.py # Main GUI window
│   ├── database/
│   │   └── database.py    # Database operations
│   └── utils/
│       ├── excel_handler.py # Excel import/export
│       └── pdf_exporter.py  # PDF generation
└── data/                  # Database storage (created automatically)
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
