"""
Setup wizard for creating custom catalogue structure
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem,
                             QLineEdit, QComboBox, QCheckBox, QGroupBox,
                             QFormLayout, QMessageBox, QScrollArea, QWidget,
                             QTextEdit, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Dict

class ColumnDefinition:
    """Represents a column definition for the catalogue"""
    
    def __init__(self, name: str, display_name: str, data_type: str, 
                 required: bool = False, default_value: str = ""):
        self.name = name
        self.display_name = display_name
        self.data_type = data_type  # text, number, decimal, date, boolean
        self.required = required
        self.default_value = default_value
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'display_name': self.display_name,
            'data_type': self.data_type,
            'required': self.required,
            'default_value': self.default_value
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            data['name'],
            data['display_name'],
            data['data_type'],
            data.get('required', False),
            data.get('default_value', '')
        )

class ColumnEditor(QWidget):
    """Widget for editing a single column definition"""
    
    column_changed = pyqtSignal()
    
    def __init__(self, column_def: ColumnDefinition = None):
        super().__init__()
        self.column_def = column_def or ColumnDefinition("", "", "text")
        self.setup_ui()
        self.populate_fields()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Column name (internal identifier)
        self.name_input = QLineEdit()
        self.name_input.textChanged.connect(self.on_name_changed)
        self.name_input.textChanged.connect(self.column_changed.emit)
        layout.addRow("Column Name:", self.name_input)
        
        # Display name (what users see)
        self.display_name_input = QLineEdit()
        self.display_name_input.textChanged.connect(self.column_changed.emit)
        layout.addRow("Display Name:", self.display_name_input)
        
        # Data type
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems([
            "text", "number", "decimal", "date", "boolean"
        ])
        self.data_type_combo.currentTextChanged.connect(self.column_changed.emit)
        layout.addRow("Data Type:", self.data_type_combo)
        
        # Required field
        self.required_checkbox = QCheckBox()
        self.required_checkbox.toggled.connect(self.column_changed.emit)
        layout.addRow("Required:", self.required_checkbox)
        
        # Default value
        self.default_value_input = QLineEdit()
        self.default_value_input.textChanged.connect(self.column_changed.emit)
        layout.addRow("Default Value:", self.default_value_input)
        
    def on_name_changed(self):
        """Auto-generate display name from column name if display name is empty"""
        if not self.display_name_input.text():
            name = self.name_input.text()
            # Convert snake_case to Title Case
            display_name = name.replace('_', ' ').title()
            self.display_name_input.setText(display_name)
    
    def populate_fields(self):
        """Populate fields with column definition data"""
        self.name_input.setText(self.column_def.name)
        self.display_name_input.setText(self.column_def.display_name)
        self.data_type_combo.setCurrentText(self.column_def.data_type)
        self.required_checkbox.setChecked(self.column_def.required)
        self.default_value_input.setText(self.column_def.default_value)
    
    def get_column_definition(self) -> ColumnDefinition:
        """Get the current column definition"""
        return ColumnDefinition(
            name=self.name_input.text().strip().lower().replace(' ', '_'),
            display_name=self.display_name_input.text().strip(),
            data_type=self.data_type_combo.currentText(),
            required=self.required_checkbox.isChecked(),
            default_value=self.default_value_input.text().strip()
        )
    
    def is_valid(self) -> bool:
        """Check if the column definition is valid"""
        return bool(self.name_input.text().strip() and 
                   self.display_name_input.text().strip())

class SetupWizard(QDialog):
    """Wizard for setting up catalogue structure"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Catalogue Setup Wizard")
        self.setModal(True)
        self.resize(800, 600)
        
        self.column_editors = []
        self.catalogue_columns = []
        
        self.setup_ui()
        self.add_default_columns()
        
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel("Create Your Custom Catalogue")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        description = QLabel(
            "Define the columns you want in your catalogue. You can add, remove, and customize "
            "each column to match your specific needs. Each column will become a field in your "
            "catalogue where you can enter and manage your data."
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin-bottom: 20px;")
        layout.addWidget(description)
        
        # Catalogue name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Catalogue Name:"))
        self.catalogue_name_input = QLineEdit()
        self.catalogue_name_input.setText("My Crafting Components")
        self.catalogue_name_input.setPlaceholderText("Enter a name for your catalogue...")
        name_layout.addWidget(self.catalogue_name_input)
        layout.addLayout(name_layout)
        
        # Column management buttons
        button_layout = QHBoxLayout()
        self.add_column_btn = QPushButton("Add Column")
        self.remove_column_btn = QPushButton("Remove Selected")
        self.preset_btn = QPushButton("Load Preset")
        
        self.add_column_btn.clicked.connect(self.add_column)
        self.remove_column_btn.clicked.connect(self.remove_selected_column)
        self.preset_btn.clicked.connect(self.show_presets)
        
        button_layout.addWidget(self.add_column_btn)
        button_layout.addWidget(self.remove_column_btn)
        button_layout.addWidget(self.preset_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Scrollable area for column editors
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        scroll_area.setWidget(self.scroll_widget)
        
        layout.addWidget(scroll_area)
        
        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.create_btn = QPushButton("Create Catalogue")
        
        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self.create_catalogue)
        
        dialog_buttons.addStretch()
        dialog_buttons.addWidget(self.cancel_btn)
        dialog_buttons.addWidget(self.create_btn)
        
        layout.addLayout(dialog_buttons)
        
    def add_default_columns(self):
        """Add some default columns to get started"""
        default_columns = [
            ColumnDefinition("name", "Name", "text", required=True),
            ColumnDefinition("category", "Category", "text"),
            ColumnDefinition("quantity", "Quantity", "number", default_value="0"),
            ColumnDefinition("notes", "Notes", "text")
        ]
        
        for col_def in default_columns:
            self.add_column_editor(col_def)
    
    def add_column(self):
        """Add a new column editor"""
        self.add_column_editor()
        
    def add_column_editor(self, column_def: ColumnDefinition = None):
        """Add a column editor widget"""
        # Create group box for this column
        group_box = QGroupBox(f"Column {len(self.column_editors) + 1}")
        group_layout = QVBoxLayout(group_box)
        
        # Create column editor
        editor = ColumnEditor(column_def)
        editor.column_changed.connect(lambda: self.update_group_title(group_box, editor))
        group_layout.addWidget(editor)
        
        # Add to scroll layout
        self.scroll_layout.addWidget(group_box)
        self.column_editors.append((group_box, editor))
        
        # Update group title
        self.update_group_title(group_box, editor)
        
    def update_group_title(self, group_box: QGroupBox, editor: ColumnEditor):
        """Update the group box title based on column name"""
        col_def = editor.get_column_definition()
        if col_def.display_name:
            group_box.setTitle(col_def.display_name)
        else:
            group_box.setTitle(f"Column {self.column_editors.index((group_box, editor)) + 1}")
    
    def remove_selected_column(self):
        """Remove the last column editor"""
        if len(self.column_editors) > 1:  # Keep at least one column
            group_box, editor = self.column_editors.pop()
            group_box.setParent(None)
            group_box.deleteLater()
        else:
            QMessageBox.warning(self, "Warning", "You must have at least one column!")
    
    def show_presets(self):
        """Show preset column configurations"""
        presets = {
            "Basic Inventory": [
                ColumnDefinition("name", "Item Name", "text", required=True),
                ColumnDefinition("quantity", "Quantity", "number", default_value="0"),
                ColumnDefinition("location", "Storage Location", "text"),
                ColumnDefinition("notes", "Notes", "text")
            ],
            "Crafting Components": [
                ColumnDefinition("name", "Component Name", "text", required=True),
                ColumnDefinition("category", "Category", "text"),
                ColumnDefinition("quantity", "Quantity", "number", default_value="0"),
                ColumnDefinition("unit", "Unit", "text", default_value="pieces"),
                ColumnDefinition("cost_per_unit", "Cost per Unit", "decimal", default_value="0.00"),
                ColumnDefinition("supplier", "Supplier", "text"),
                ColumnDefinition("location", "Storage Location", "text"),
                ColumnDefinition("notes", "Notes", "text")
            ],
            "Book Collection": [
                ColumnDefinition("title", "Book Title", "text", required=True),
                ColumnDefinition("author", "Author", "text"),
                ColumnDefinition("genre", "Genre", "text"),
                ColumnDefinition("isbn", "ISBN", "text"),
                ColumnDefinition("publication_year", "Publication Year", "number"),
                ColumnDefinition("rating", "Rating", "number"),
                ColumnDefinition("read_status", "Read Status", "text", default_value="Unread"),
                ColumnDefinition("notes", "Notes", "text")
            ],
            "Tool Inventory": [
                ColumnDefinition("tool_name", "Tool Name", "text", required=True),
                ColumnDefinition("brand", "Brand", "text"),
                ColumnDefinition("model", "Model", "text"),
                ColumnDefinition("purchase_date", "Purchase Date", "date"),
                ColumnDefinition("purchase_price", "Purchase Price", "decimal"),
                ColumnDefinition("condition", "Condition", "text", default_value="Good"),
                ColumnDefinition("location", "Storage Location", "text"),
                ColumnDefinition("notes", "Notes", "text")
            ]
        }
        
        # Create preset selection dialog
        preset_dialog = QDialog(self)
        preset_dialog.setWindowTitle("Choose Preset")
        preset_dialog.setModal(True)
        preset_dialog.resize(400, 300)
        
        layout = QVBoxLayout(preset_dialog)
        
        layout.addWidget(QLabel("Choose a preset configuration:"))
        
        preset_list = QListWidget()
        for preset_name in presets.keys():
            preset_list.addItem(preset_name)
        layout.addWidget(preset_list)
        
        buttons = QHBoxLayout()
        load_btn = QPushButton("Load Preset")
        cancel_btn = QPushButton("Cancel")
        
        def load_preset():
            current_item = preset_list.currentItem()
            if current_item:
                preset_name = current_item.text()
                self.load_preset_columns(presets[preset_name])
                preset_dialog.accept()
        
        load_btn.clicked.connect(load_preset)
        cancel_btn.clicked.connect(preset_dialog.reject)
        
        buttons.addStretch()
        buttons.addWidget(load_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        preset_dialog.exec()
    
    def load_preset_columns(self, columns: List[ColumnDefinition]):
        """Load preset columns, replacing current ones"""
        # Clear existing columns
        for group_box, editor in self.column_editors:
            group_box.setParent(None)
            group_box.deleteLater()
        self.column_editors.clear()
        
        # Add preset columns
        for col_def in columns:
            self.add_column_editor(col_def)
    
    def create_catalogue(self):
        """Validate and create the catalogue"""
        # Validate catalogue name
        catalogue_name = self.catalogue_name_input.text().strip()
        if not catalogue_name:
            QMessageBox.warning(self, "Warning", "Please enter a catalogue name!")
            return
        
        # Validate columns
        columns = []
        column_names = set()
        
        for group_box, editor in self.column_editors:
            if not editor.is_valid():
                QMessageBox.warning(self, "Warning", f"Please complete all fields for {group_box.title()}!")
                return
            
            col_def = editor.get_column_definition()
            
            # Check for duplicate column names
            if col_def.name in column_names:
                QMessageBox.warning(self, "Warning", f"Duplicate column name: {col_def.name}!")
                return
            
            column_names.add(col_def.name)
            columns.append(col_def)
        
        # Ensure at least one required column
        if not any(col.required for col in columns):
            reply = QMessageBox.question(
                self, "No Required Fields", 
                "You don't have any required fields. This means entries can be completely empty. Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Store the configuration
        self.catalogue_name = catalogue_name
        self.catalogue_columns = columns
        
        self.accept()
    
    def get_catalogue_config(self) -> Dict:
        """Get the catalogue configuration"""
        return {
            'name': self.catalogue_name,
            'columns': [col.to_dict() for col in self.catalogue_columns]
        }
