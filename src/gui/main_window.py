"""
Main window for the Crafting Components Catalogue application
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QLineEdit, QLabel, QComboBox, QMessageBox,
                             QFileDialog, QHeaderView, QSplitter, QGroupBox,
                             QFormLayout, QTextEdit, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.database import DatabaseManager
from src.utils.excel_handler import ExcelHandler
from src.utils.pdf_exporter import PDFExporter

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.excel_handler = ExcelHandler()
        self.pdf_exporter = PDFExporter()
        
        self.setWindowTitle("Crafting Components Catalogue")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        self.setup_menu_bar()
        self.load_components()
        
    def setup_ui(self):
        """Set up the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Component form
        self.setup_component_form(splitter)
        
        # Right panel - Component table and controls
        self.setup_component_table(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
    def setup_component_form(self, parent):
        """Set up the component input form"""
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Form group box
        form_group = QGroupBox("Component Details")
        form_group_layout = QFormLayout(form_group)
        
        # Form fields
        self.name_input = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.quantity_input = QSpinBox()
        self.quantity_input.setMaximum(999999)
        self.unit_input = QLineEdit()
        self.unit_input.setText("pieces")
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setMaximum(999999.99)
        self.cost_input.setDecimals(2)
        self.supplier_input = QLineEdit()
        self.location_input = QLineEdit()
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        
        # Add fields to form
        form_group_layout.addRow("Name*:", self.name_input)
        form_group_layout.addRow("Category:", self.category_combo)
        form_group_layout.addRow("Description:", self.description_input)
        form_group_layout.addRow("Quantity:", self.quantity_input)
        form_group_layout.addRow("Unit:", self.unit_input)
        form_group_layout.addRow("Cost per Unit:", self.cost_input)
        form_group_layout.addRow("Supplier:", self.supplier_input)
        form_group_layout.addRow("Location:", self.location_input)
        form_group_layout.addRow("Notes:", self.notes_input)
        
        form_layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Component")
        self.update_button = QPushButton("Update Component")
        self.clear_button = QPushButton("Clear Form")
        
        self.add_button.clicked.connect(self.add_component)
        self.update_button.clicked.connect(self.update_component)
        self.clear_button.clicked.connect(self.clear_form)
        
        self.update_button.setEnabled(False)  # Initially disabled
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.clear_button)
        
        form_layout.addLayout(button_layout)
        form_layout.addStretch()
        
        parent.addWidget(form_widget)
        
    def setup_component_table(self, parent):
        """Set up the component table and controls"""
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        # Search and filter controls
        controls_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, category, or description...")
        self.search_input.textChanged.connect(self.search_components)
        
        category_label = QLabel("Filter by Category:")
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.filter_by_category)
        
        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(category_label)
        controls_layout.addWidget(self.category_filter)
        controls_layout.addStretch()
        
        table_layout.addLayout(controls_layout)
        
        # Component table
        self.component_table = QTableWidget()
        self.setup_table_headers()
        self.component_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.component_table.itemDoubleClicked.connect(self.edit_selected_component)
        
        table_layout.addWidget(self.component_table)
        
        # Table action buttons
        table_buttons_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit Selected")
        self.delete_button = QPushButton("Delete Selected")
        self.import_button = QPushButton("Import from Excel")
        self.export_button = QPushButton("Export to Excel")
        self.print_button = QPushButton("Print Catalogue")
        
        self.edit_button.clicked.connect(self.edit_selected_component)
        self.delete_button.clicked.connect(self.delete_selected_component)
        self.import_button.clicked.connect(self.import_from_excel)
        self.export_button.clicked.connect(self.export_to_excel)
        self.print_button.clicked.connect(self.print_catalogue)
        
        # Initially disable edit/delete buttons
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        table_buttons_layout.addWidget(self.edit_button)
        table_buttons_layout.addWidget(self.delete_button)
        table_buttons_layout.addStretch()
        table_buttons_layout.addWidget(self.import_button)
        table_buttons_layout.addWidget(self.export_button)
        table_buttons_layout.addWidget(self.print_button)
        
        table_layout.addLayout(table_buttons_layout)
        
        parent.addWidget(table_widget)
        
    def setup_table_headers(self):
        """Set up the table headers"""
        headers = ["ID", "Name", "Category", "Description", "Quantity", 
                  "Unit", "Cost/Unit", "Supplier", "Location", "Notes"]
        self.component_table.setColumnCount(len(headers))
        self.component_table.setHorizontalHeaderLabels(headers)
        
        # Hide ID column
        self.component_table.setColumnHidden(0, True)
        
        # Set column widths
        header = self.component_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Description
        
    def setup_menu_bar(self):
        """Set up the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        import_action = QAction("Import from Excel", self)
        import_action.triggered.connect(self.import_from_excel)
        file_menu.addAction(import_action)
        
        export_action = QAction("Export to Excel", self)
        export_action.triggered.connect(self.export_to_excel)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        print_action = QAction("Print Catalogue", self)
        print_action.triggered.connect(self.print_catalogue)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def load_components(self):
        """Load all components into the table"""
        components = self.db_manager.get_all_components()
        self.populate_table(components)
        self.update_category_filters()
        
    def populate_table(self, components):
        """Populate the table with component data"""
        self.component_table.setRowCount(len(components))
        
        for row, component in enumerate(components):
            self.component_table.setItem(row, 0, QTableWidgetItem(str(component['id'])))
            self.component_table.setItem(row, 1, QTableWidgetItem(component['name'] or ''))
            self.component_table.setItem(row, 2, QTableWidgetItem(component['category'] or ''))
            self.component_table.setItem(row, 3, QTableWidgetItem(component['description'] or ''))
            self.component_table.setItem(row, 4, QTableWidgetItem(str(component['quantity'])))
            self.component_table.setItem(row, 5, QTableWidgetItem(component['unit'] or ''))
            self.component_table.setItem(row, 6, QTableWidgetItem(f"{component['cost_per_unit']:.2f}"))
            self.component_table.setItem(row, 7, QTableWidgetItem(component['supplier'] or ''))
            self.component_table.setItem(row, 8, QTableWidgetItem(component['location'] or ''))
            self.component_table.setItem(row, 9, QTableWidgetItem(component['notes'] or ''))
            
    def update_category_filters(self):
        """Update the category filter dropdown"""
        categories = self.db_manager.get_categories()
        
        # Update form category combo
        current_category = self.category_combo.currentText()
        self.category_combo.clear()
        self.category_combo.addItems(categories)
        if current_category in categories:
            self.category_combo.setCurrentText(current_category)
            
        # Update filter combo
        current_filter = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(categories)
        if current_filter != "All Categories" and current_filter in categories:
            self.category_filter.setCurrentText(current_filter)
            
    def add_component(self):
        """Add a new component"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Component name is required!")
            return
            
        component_data = self.get_form_data()
        
        try:
            self.db_manager.add_component(component_data)
            self.load_components()
            self.clear_form()
            QMessageBox.information(self, "Success", "Component added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add component: {str(e)}")
            
    def update_component(self):
        """Update the selected component"""
        if not hasattr(self, 'current_component_id'):
            return
            
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Component name is required!")
            return
            
        component_data = self.get_form_data()
        
        try:
            success = self.db_manager.update_component(self.current_component_id, component_data)
            if success:
                self.load_components()
                self.clear_form()
                QMessageBox.information(self, "Success", "Component updated successfully!")
            else:
                QMessageBox.warning(self, "Warning", "Component not found or no changes made.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update component: {str(e)}")
            
    def get_form_data(self):
        """Get data from the form fields"""
        return {
            'name': self.name_input.text().strip(),
            'category': self.category_combo.currentText().strip(),
            'description': self.description_input.toPlainText().strip(),
            'quantity': self.quantity_input.value(),
            'unit': self.unit_input.text().strip(),
            'cost_per_unit': self.cost_input.value(),
            'supplier': self.supplier_input.text().strip(),
            'location': self.location_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip()
        }
        
    def clear_form(self):
        """Clear all form fields"""
        self.name_input.clear()
        self.category_combo.setCurrentText("")
        self.description_input.clear()
        self.quantity_input.setValue(0)
        self.unit_input.setText("pieces")
        self.cost_input.setValue(0.0)
        self.supplier_input.clear()
        self.location_input.clear()
        self.notes_input.clear()
        
        self.add_button.setEnabled(True)
        self.update_button.setEnabled(False)
        
        if hasattr(self, 'current_component_id'):
            delattr(self, 'current_component_id')
            
    def on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = set()
        for item in self.component_table.selectedItems():
            selected_rows.add(item.row())
            
        has_selection = len(selected_rows) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def edit_selected_component(self):
        """Edit the selected component"""
        current_row = self.component_table.currentRow()
        if current_row < 0:
            return
            
        component_id = int(self.component_table.item(current_row, 0).text())
        component = self.db_manager.get_component_by_id(component_id)
        
        if component:
            self.populate_form(component)
            
    def populate_form(self, component):
        """Populate the form with component data"""
        self.name_input.setText(component['name'] or '')
        self.category_combo.setCurrentText(component['category'] or '')
        self.description_input.setPlainText(component['description'] or '')
        self.quantity_input.setValue(component['quantity'] or 0)
        self.unit_input.setText(component['unit'] or 'pieces')
        self.cost_input.setValue(component['cost_per_unit'] or 0.0)
        self.supplier_input.setText(component['supplier'] or '')
        self.location_input.setText(component['location'] or '')
        self.notes_input.setPlainText(component['notes'] or '')
        
        self.current_component_id = component['id']
        self.add_button.setEnabled(False)
        self.update_button.setEnabled(True)
        
    def delete_selected_component(self):
        """Delete the selected component"""
        current_row = self.component_table.currentRow()
        if current_row < 0:
            return
            
        component_name = self.component_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete '{component_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            component_id = int(self.component_table.item(current_row, 0).text())
            
            try:
                success = self.db_manager.delete_component(component_id)
                if success:
                    self.load_components()
                    self.clear_form()
                    QMessageBox.information(self, "Success", "Component deleted successfully!")
                else:
                    QMessageBox.warning(self, "Warning", "Component not found.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete component: {str(e)}")
                
    def search_components(self):
        """Search components based on search input"""
        search_term = self.search_input.text().strip()
        
        if search_term:
            components = self.db_manager.search_components(search_term)
        else:
            components = self.db_manager.get_all_components()
            
        self.populate_table(components)
        
    def filter_by_category(self):
        """Filter components by selected category"""
        category = self.category_filter.currentText()
        
        if category == "All Categories":
            components = self.db_manager.get_all_components()
        else:
            components = self.db_manager.get_components_by_category(category)
            
        self.populate_table(components)
        
    def import_from_excel(self):
        """Import components from Excel file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Excel File", "", 
            "Excel files (*.xlsx *.xls);;All files (*.*)"
        )
        
        if file_path:
            try:
                components = self.excel_handler.import_from_excel(file_path)
                
                # Add components to database
                added_count = 0
                for component in components:
                    self.db_manager.add_component(component)
                    added_count += 1
                    
                self.load_components()
                QMessageBox.information(
                    self, "Success", 
                    f"Successfully imported {added_count} components from Excel!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import Excel file: {str(e)}")
                
    def export_to_excel(self):
        """Export components to Excel file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to Excel", "crafting_components.xlsx",
            "Excel files (*.xlsx);;All files (*.*)"
        )
        
        if file_path:
            try:
                components = self.db_manager.get_all_components()
                self.excel_handler.export_to_excel(components, file_path)
                QMessageBox.information(self, "Success", f"Components exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export to Excel: {str(e)}")
                
    def print_catalogue(self):
        """Print the catalogue as PDF"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "crafting_catalogue.pdf",
            "PDF files (*.pdf);;All files (*.*)"
        )
        
        if file_path:
            try:
                components = self.db_manager.get_all_components()
                self.pdf_exporter.export_to_pdf(components, file_path)
                QMessageBox.information(self, "Success", f"Catalogue saved as PDF: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create PDF: {str(e)}")
                
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Crafting Components Catalogue",
            "Crafting Components Catalogue v1.0\n\n"
            "A desktop application for managing crafting components inventory.\n\n"
            "Features:\n"
            "• Add, edit, and delete components\n"
            "• Import from Excel files\n"
            "• Export to Excel and PDF\n"
            "• Search and filter components\n"
            "• Print catalogue\n\n"
            "Created with PyQt6 and Python"
        )
