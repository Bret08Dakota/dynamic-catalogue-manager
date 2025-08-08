"""
Dynamic main window that adapts to user-defined catalogue structure
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QLineEdit, QLabel, QComboBox, QMessageBox,
                             QFileDialog, QHeaderView, QSplitter, QGroupBox,
                             QFormLayout, QTextEdit, QSpinBox, QDoubleSpinBox,
                             QCheckBox, QDateEdit, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QAction, QIcon
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.dynamic_database import DynamicDatabaseManager
from src.gui.setup_wizard import SetupWizard, ColumnDefinition
from src.utils.dynamic_excel_handler import DynamicExcelHandler
from src.utils.dynamic_pdf_exporter import DynamicPDFExporter

class DynamicFormWidget(QWidget):
    """Dynamic form widget that creates input fields based on column definitions"""
    
    def __init__(self, columns: list):
        super().__init__()
        self.columns = [ColumnDefinition.from_dict(col) if isinstance(col, dict) else col for col in columns]
        self.form_widgets = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dynamic form"""
        layout = QVBoxLayout(self)
        
        # Create scroll area for the form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        
        # Create input widgets for each column
        for column in self.columns:
            widget = self.create_input_widget(column)
            self.form_widgets[column.name] = widget
            
            label_text = column.display_name
            if column.required:
                label_text += "*"
            
            form_layout.addRow(f"{label_text}:", widget)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
    
    def create_input_widget(self, column: ColumnDefinition):
        """Create appropriate input widget based on column data type"""
        if column.data_type == 'text':
            if 'note' in column.name.lower() or 'description' in column.name.lower():
                widget = QTextEdit()
                widget.setMaximumHeight(80)
                if column.default_value:
                    widget.setPlainText(column.default_value)
            else:
                widget = QLineEdit()
                if column.default_value:
                    widget.setText(column.default_value)
        
        elif column.data_type == 'number':
            widget = QSpinBox()
            widget.setMaximum(999999)
            widget.setMinimum(-999999)
            if column.default_value:
                try:
                    widget.setValue(int(column.default_value))
                except ValueError:
                    widget.setValue(0)
        
        elif column.data_type == 'decimal':
            widget = QDoubleSpinBox()
            widget.setMaximum(999999.99)
            widget.setMinimum(-999999.99)
            widget.setDecimals(2)
            if column.default_value:
                try:
                    widget.setValue(float(column.default_value))
                except ValueError:
                    widget.setValue(0.0)
        
        elif column.data_type == 'date':
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            if column.default_value:
                try:
                    # Try to parse date, default to current date if invalid
                    widget.setDate(QDate.fromString(column.default_value, Qt.DateFormat.ISODate))
                except:
                    widget.setDate(QDate.currentDate())
            else:
                widget.setDate(QDate.currentDate())
        
        elif column.data_type == 'boolean':
            widget = QCheckBox()
            if column.default_value:
                widget.setChecked(column.default_value.lower() in ('true', '1', 'yes', 'on'))
        
        else:  # Default to text
            widget = QLineEdit()
            if column.default_value:
                widget.setText(column.default_value)
        
        return widget
    
    def get_form_data(self) -> dict:
        """Get data from all form widgets"""
        data = {}
        
        for column in self.columns:
            widget = self.form_widgets[column.name]
            
            if column.data_type == 'text':
                if isinstance(widget, QTextEdit):
                    data[column.name] = widget.toPlainText().strip()
                else:
                    data[column.name] = widget.text().strip()
            
            elif column.data_type == 'number':
                data[column.name] = widget.value()
            
            elif column.data_type == 'decimal':
                data[column.name] = widget.value()
            
            elif column.data_type == 'date':
                data[column.name] = widget.date().toString(Qt.DateFormat.ISODate)
            
            elif column.data_type == 'boolean':
                data[column.name] = widget.isChecked()
            
            else:
                data[column.name] = widget.text().strip()
        
        return data
    
    def set_form_data(self, data: dict):
        """Set form data from dictionary"""
        for column in self.columns:
            if column.name in data:
                widget = self.form_widgets[column.name]
                value = data[column.name]
                
                if column.data_type == 'text':
                    if isinstance(widget, QTextEdit):
                        widget.setPlainText(str(value) if value else '')
                    else:
                        widget.setText(str(value) if value else '')
                
                elif column.data_type == 'number':
                    try:
                        widget.setValue(int(value) if value is not None else 0)
                    except (ValueError, TypeError):
                        widget.setValue(0)
                
                elif column.data_type == 'decimal':
                    try:
                        widget.setValue(float(value) if value is not None else 0.0)
                    except (ValueError, TypeError):
                        widget.setValue(0.0)
                
                elif column.data_type == 'date':
                    if value:
                        try:
                            widget.setDate(QDate.fromString(str(value), Qt.DateFormat.ISODate))
                        except:
                            widget.setDate(QDate.currentDate())
                    else:
                        widget.setDate(QDate.currentDate())
                
                elif column.data_type == 'boolean':
                    if isinstance(value, bool):
                        widget.setChecked(value)
                    elif isinstance(value, (int, str)):
                        widget.setChecked(bool(value))
                    else:
                        widget.setChecked(False)
                
                else:
                    widget.setText(str(value) if value else '')
    
    def clear_form(self):
        """Clear all form fields"""
        for column in self.columns:
            widget = self.form_widgets[column.name]
            
            if column.data_type == 'text':
                if isinstance(widget, QTextEdit):
                    widget.setPlainText(column.default_value or '')
                else:
                    widget.setText(column.default_value or '')
            
            elif column.data_type == 'number':
                try:
                    default_val = int(column.default_value) if column.default_value else 0
                except ValueError:
                    default_val = 0
                widget.setValue(default_val)
            
            elif column.data_type == 'decimal':
                try:
                    default_val = float(column.default_value) if column.default_value else 0.0
                except ValueError:
                    default_val = 0.0
                widget.setValue(default_val)
            
            elif column.data_type == 'date':
                if column.default_value:
                    try:
                        widget.setDate(QDate.fromString(column.default_value, Qt.DateFormat.ISODate))
                    except:
                        widget.setDate(QDate.currentDate())
                else:
                    widget.setDate(QDate.currentDate())
            
            elif column.data_type == 'boolean':
                default_val = column.default_value.lower() in ('true', '1', 'yes', 'on') if column.default_value else False
                widget.setChecked(default_val)
            
            else:
                widget.setText(column.default_value or '')
    
    def validate_form(self) -> tuple[bool, str]:
        """Validate form data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        for column in self.columns:
            if column.required:
                widget = self.form_widgets[column.name]
                
                if column.data_type == 'text':
                    if isinstance(widget, QTextEdit):
                        value = widget.toPlainText().strip()
                    else:
                        value = widget.text().strip()
                    
                    if not value:
                        return False, f"{column.display_name} is required!"
        
        return True, ""

class DynamicMainWindow(QMainWindow):
    """Main application window with dynamic structure"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DynamicDatabaseManager()
        self.excel_handler = None
        self.pdf_exporter = None
        
        self.catalogue_config = None
        self.form_widget = None
        self.current_item_id = None
        
        self.setWindowTitle("Dynamic Catalogue Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        # Try to load existing configuration
        if not self.load_existing_config():
            # Show setup wizard for new configuration
            self.show_setup_wizard()
        
        if self.catalogue_config:
            self._initialize_handlers()
            self.setup_ui()
            self.load_items()
    
    def _initialize_handlers(self):
        """Initialize Excel and PDF handlers with catalogue configuration"""
        if self.catalogue_config:
            self.excel_handler = DynamicExcelHandler(self.catalogue_config)
            self.pdf_exporter = DynamicPDFExporter(self.catalogue_config)
        
    def load_existing_config(self) -> bool:
        """Try to load existing catalogue configuration"""
        config = self.db_manager.load_catalogue_config()
        if config:
            self.catalogue_config = config
            self.setWindowTitle(f"Dynamic Catalogue Manager - {config['name']}")
            return True
        return False
    
    def show_setup_wizard(self):
        """Show the setup wizard"""
        wizard = SetupWizard(self)
        if wizard.exec() == wizard.DialogCode.Accepted:
            config = wizard.get_catalogue_config()
            
            # Create database structure
            if self.db_manager.create_catalogue_structure(config):
                self.catalogue_config = config
                self.setWindowTitle(f"Dynamic Catalogue Manager - {config['name']}")
                QMessageBox.information(self, "Success", "Catalogue structure created successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to create catalogue structure!")
                self.close()
        else:
            self.close()
    
    def setup_ui(self):
        """Set up the user interface"""
        if not self.catalogue_config:
            return
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Dynamic form
        self.setup_form_panel(splitter)
        
        # Right panel - Items table and controls
        self.setup_table_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
        # Setup menu bar
        self.setup_menu_bar()
    
    def setup_form_panel(self, parent):
        """Set up the dynamic form panel"""
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Form group box
        form_group = QGroupBox("Item Details")
        form_group_layout = QVBoxLayout(form_group)
        
        # Create dynamic form
        columns = [ColumnDefinition.from_dict(col) for col in self.catalogue_config['columns']]
        self.form_widget = DynamicFormWidget(columns)
        form_group_layout.addWidget(self.form_widget)
        
        form_layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Item")
        self.update_button = QPushButton("Update Item")
        self.clear_button = QPushButton("Clear Form")
        
        self.add_button.clicked.connect(self.add_item)
        self.update_button.clicked.connect(self.update_item)
        self.clear_button.clicked.connect(self.clear_form)
        
        self.update_button.setEnabled(False)  # Initially disabled
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.clear_button)
        
        form_layout.addLayout(button_layout)
        form_layout.addStretch()
        
        parent.addWidget(form_widget)
    
    def setup_table_panel(self, parent):
        """Set up the items table panel"""
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        # Search controls
        controls_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.search_items)
        
        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.search_input)
        controls_layout.addStretch()
        
        table_layout.addLayout(controls_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.setup_table_headers()
        self.items_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.items_table.itemDoubleClicked.connect(self.edit_selected_item)
        
        table_layout.addWidget(self.items_table)
        
        # Table action buttons
        table_buttons_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit Selected")
        self.delete_button = QPushButton("Delete Selected")
        self.import_button = QPushButton("Import from Excel")
        self.export_button = QPushButton("Export to Excel")
        self.print_button = QPushButton("Print Catalogue")
        
        self.edit_button.clicked.connect(self.edit_selected_item)
        self.delete_button.clicked.connect(self.delete_selected_item)
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
        """Set up the table headers based on column configuration"""
        if not self.catalogue_config:
            return
        
        columns = [ColumnDefinition.from_dict(col) for col in self.catalogue_config['columns']]
        headers = ["ID"] + [col.display_name for col in columns]
        
        self.items_table.setColumnCount(len(headers))
        self.items_table.setHorizontalHeaderLabels(headers)
        
        # Hide ID column
        self.items_table.setColumnHidden(0, True)
        
        # Set column widths
        header = self.items_table.horizontalHeader()
        for i in range(1, len(headers)):
            if i == 1:  # First visible column stretches
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
    
    def setup_menu_bar(self):
        """Set up the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_catalogue_action = QAction("New Catalogue Structure", self)
        new_catalogue_action.triggered.connect(self.create_new_catalogue)
        file_menu.addAction(new_catalogue_action)
        
        file_menu.addSeparator()
        
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
    
    def create_new_catalogue(self):
        """Create a new catalogue structure"""
        reply = QMessageBox.question(
            self, "New Catalogue", 
            "Creating a new catalogue will replace the current one and all its data. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.show_setup_wizard()
            if self.catalogue_config:
                self.setup_ui()
                self.load_items()
    
    def load_items(self):
        """Load all items into the table"""
        items = self.db_manager.get_all_items()
        self.populate_table(items)
    
    def populate_table(self, items):
        """Populate the table with item data"""
        if not self.catalogue_config:
            return
        
        columns = [ColumnDefinition.from_dict(col) for col in self.catalogue_config['columns']]
        self.items_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # ID column
            self.items_table.setItem(row, 0, QTableWidgetItem(str(item.get('id', ''))))
            
            # Data columns
            for col_idx, column in enumerate(columns, 1):
                value = item.get(column.name, '')
                
                # Format value based on data type
                if column.data_type == 'boolean':
                    display_value = "Yes" if value else "No"
                elif column.data_type == 'decimal':
                    try:
                        display_value = f"{float(value):.2f}" if value is not None else "0.00"
                    except (ValueError, TypeError):
                        display_value = str(value) if value is not None else ""
                else:
                    display_value = str(value) if value is not None else ""
                
                self.items_table.setItem(row, col_idx, QTableWidgetItem(display_value))
    
    def add_item(self):
        """Add a new item"""
        if not self.form_widget:
            return
        
        # Validate form
        is_valid, error_msg = self.form_widget.validate_form()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        item_data = self.form_widget.get_form_data()
        
        try:
            self.db_manager.add_item(item_data)
            self.load_items()
            self.clear_form()
            QMessageBox.information(self, "Success", "Item added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add item: {str(e)}")
    
    def update_item(self):
        """Update the selected item"""
        if not self.current_item_id or not self.form_widget:
            return
        
        # Validate form
        is_valid, error_msg = self.form_widget.validate_form()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        item_data = self.form_widget.get_form_data()
        
        try:
            success = self.db_manager.update_item(self.current_item_id, item_data)
            if success:
                self.load_items()
                self.clear_form()
                QMessageBox.information(self, "Success", "Item updated successfully!")
            else:
                QMessageBox.warning(self, "Warning", "Item not found or no changes made.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update item: {str(e)}")
    
    def clear_form(self):
        """Clear the form"""
        if self.form_widget:
            self.form_widget.clear_form()
        
        self.add_button.setEnabled(True)
        self.update_button.setEnabled(False)
        self.current_item_id = None
    
    def on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = set()
        for item in self.items_table.selectedItems():
            selected_rows.add(item.row())
        
        has_selection = len(selected_rows) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def edit_selected_item(self):
        """Edit the selected item"""
        current_row = self.items_table.currentRow()
        if current_row < 0:
            return
        
        item_id = int(self.items_table.item(current_row, 0).text())
        item = self.db_manager.get_item_by_id(item_id)
        
        if item and self.form_widget:
            self.form_widget.set_form_data(item)
            self.current_item_id = item_id
            self.add_button.setEnabled(False)
            self.update_button.setEnabled(True)
    
    def delete_selected_item(self):
        """Delete the selected item"""
        current_row = self.items_table.currentRow()
        if current_row < 0:
            return
        
        # Get first column value for display
        first_col_value = self.items_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete '{first_col_value}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            item_id = int(self.items_table.item(current_row, 0).text())
            
            try:
                success = self.db_manager.delete_item(item_id)
                if success:
                    self.load_items()
                    self.clear_form()
                    QMessageBox.information(self, "Success", "Item deleted successfully!")
                else:
                    QMessageBox.warning(self, "Warning", "Item not found.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")
    
    def search_items(self):
        """Search items based on search input"""
        search_term = self.search_input.text().strip()
        
        if search_term:
            items = self.db_manager.search_items(search_term)
        else:
            items = self.db_manager.get_all_items()
        
        self.populate_table(items)
    
    def import_from_excel(self):
        """Import items from Excel file"""
        if not self.excel_handler:
            QMessageBox.warning(self, "Error", "Excel handler not initialized!")
            return
        
        # Option to create template first
        reply = QMessageBox.question(
            self, "Import Options", 
            "Would you like to create an Excel template first, or import from an existing file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return
        elif reply == QMessageBox.StandardButton.Yes:
            # Create template
            template_path, _ = QFileDialog.getSaveFileName(
                self, "Save Excel Template", "catalogue_template.xlsx",
                "Excel files (*.xlsx);;All files (*.*)"
            )
            
            if template_path:
                try:
                    self.excel_handler.create_template_excel(template_path)
                    QMessageBox.information(
                        self, "Template Created", 
                        f"Excel template created at {template_path}\n\n"
                        "Fill in your data and then use 'Import from Excel' again to load it."
                    )
                    return
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create template: {str(e)}")
                    return
        
        # Import from existing file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Excel File", "", 
            "Excel files (*.xlsx *.xls);;All files (*.*)"
        )
        
        if file_path:
            try:
                # Validate file first
                validation = self.excel_handler.validate_excel_format(file_path)
                
                if not validation['valid']:
                    error_msg = "Excel file validation failed:\n\n" + "\n".join(validation['errors'])
                    if validation['missing_columns']:
                        error_msg += f"\n\nMissing required columns: {', '.join(validation['missing_columns'])}"
                    QMessageBox.warning(self, "Validation Error", error_msg)
                    return
                
                # Show mapping information
                if validation['matched_columns'] or validation['unmatched_columns']:
                    info_parts = []
                    if validation['matched_columns']:
                        info_parts.append("Matched columns:")
                        for match in validation['matched_columns']:
                            info_parts.append(f"• {match['excel_column']} → {match['catalogue_column']}")
                    
                    if validation['unmatched_columns']:
                        info_parts.append("\nUnmatched columns (will use defaults):")
                        for col in validation['unmatched_columns']:
                            info_parts.append(f"• {col}")
                    
                    info_msg = "\n".join(info_parts) + f"\n\nFound {validation['rows']} rows to import. Continue?"
                    
                    reply = QMessageBox.question(
                        self, "Import Preview", info_msg,
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                # Import the data
                items = self.excel_handler.import_from_excel(file_path)
                
                if not items:
                    QMessageBox.information(self, "No Data", "No valid items found in the Excel file.")
                    return
                
                # Add items to database
                added_count = 0
                errors = []
                
                for i, item in enumerate(items, 1):
                    try:
                        self.db_manager.add_item(item)
                        added_count += 1
                    except Exception as e:
                        errors.append(f"Row {i}: {str(e)}")
                
                # Show results
                if added_count > 0:
                    self.load_items()
                    
                result_msg = f"Successfully imported {added_count} items from Excel!"
                if errors:
                    result_msg += f"\n\nErrors encountered:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        result_msg += f"\n... and {len(errors) - 5} more errors."
                
                QMessageBox.information(self, "Import Complete", result_msg)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import Excel file: {str(e)}")
    
    def export_to_excel(self):
        """Export items to Excel file"""
        if not self.excel_handler:
            QMessageBox.warning(self, "Error", "Excel handler not initialized!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to Excel", f"{self.catalogue_config['name'].replace(' ', '_')}.xlsx",
            "Excel files (*.xlsx);;All files (*.*)"
        )
        
        if file_path:
            try:
                items = self.db_manager.get_all_items()
                self.excel_handler.export_to_excel(items, file_path)
                
                # Show success message with option to open file
                reply = QMessageBox.question(
                    self, "Export Complete", 
                    f"Successfully exported {len(items)} items to Excel!\n\n"
                    f"File saved as: {file_path}\n\n"
                    "Would you like to open the file location?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    import os
                    import subprocess
                    import platform
                    
                    # Open file location in file explorer
                    if platform.system() == "Windows":
                        subprocess.run(["explorer", "/select,", file_path])
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", "-R", file_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", os.path.dirname(file_path)])
                        
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export to Excel: {str(e)}")
    
    def print_catalogue(self):
        """Print the catalogue as PDF"""
        if not self.pdf_exporter:
            QMessageBox.warning(self, "Error", "PDF exporter not initialized!")
            return
        
        # Ask user for PDF options
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QLabel
        
        options_dialog = QDialog(self)
        options_dialog.setWindowTitle("PDF Export Options")
        options_dialog.setModal(True)
        options_dialog.resize(350, 200)
        
        layout = QVBoxLayout(options_dialog)
        
        layout.addWidget(QLabel("Choose PDF export options:"))
        
        summary_checkbox = QCheckBox("Include summary statistics")
        summary_checkbox.setChecked(True)
        layout.addWidget(summary_checkbox)
        
        detailed_checkbox = QCheckBox("Include detailed text sections")
        detailed_checkbox.setChecked(True)
        layout.addWidget(detailed_checkbox)
        
        category_checkbox = QCheckBox("Create category summary (if applicable)")
        category_checkbox.setChecked(False)
        layout.addWidget(category_checkbox)
        
        buttons = QHBoxLayout()
        export_btn = QPushButton("Export PDF")
        cancel_btn = QPushButton("Cancel")
        
        export_btn.clicked.connect(options_dialog.accept)
        cancel_btn.clicked.connect(options_dialog.reject)
        
        buttons.addStretch()
        buttons.addWidget(export_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        if options_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Get export options
        include_summary = summary_checkbox.isChecked()
        include_detailed = detailed_checkbox.isChecked()
        create_category_summary = category_checkbox.isChecked()
        
        # Choose file location
        default_filename = f"{self.catalogue_config['name'].replace(' ', '_')}_catalogue.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Catalogue", default_filename,
            "PDF files (*.pdf);;All files (*.*)"
        )
        
        if file_path:
            try:
                items = self.db_manager.get_all_items()
                
                if not items:
                    QMessageBox.information(self, "No Data", "No items found to export.")
                    return
                
                # Export main PDF
                self.pdf_exporter.export_to_pdf(
                    items, file_path, 
                    title=self.catalogue_config['name'],
                    include_summary=include_summary
                )
                
                # Create category summary if requested
                if create_category_summary:
                    try:
                        category_file = file_path.replace('.pdf', '_category_summary.pdf')
                        self.pdf_exporter.export_category_summary_pdf(items, category_file)
                        
                        success_msg = (f"PDF catalogue exported successfully!\n\n"
                                     f"Main catalogue: {file_path}\n"
                                     f"Category summary: {category_file}")
                    except Exception as e:
                        success_msg = (f"Main PDF exported successfully: {file_path}\n\n"
                                     f"Category summary failed: {str(e)}")
                else:
                    success_msg = f"PDF catalogue exported successfully!\n\nFile saved as: {file_path}"
                
                # Show success message with option to open file
                reply = QMessageBox.question(
                    self, "Export Complete", 
                    success_msg + "\n\nWould you like to open the file location?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    import os
                    import subprocess
                    import platform
                    
                    # Open file location in file explorer
                    if platform.system() == "Windows":
                        subprocess.run(["explorer", "/select,", file_path])
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", "-R", file_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", os.path.dirname(file_path)])
                        
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create PDF: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Dynamic Catalogue Manager",
            "Dynamic Catalogue Manager v2.0\n\n"
            "A desktop application for managing custom catalogues with user-defined structures.\n\n"
            "Features:\n"
            "• Custom column definitions\n"
            "• Dynamic form generation\n"
            "• Add, edit, and delete items\n"
            "• Search and filter items\n"
            "• Import/Export capabilities\n"
            "• Print catalogue\n\n"
            "Created with PyQt6 and Python"
        )
