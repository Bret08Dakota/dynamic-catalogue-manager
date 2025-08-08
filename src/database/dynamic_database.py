"""
Dynamic database module for managing custom catalogue structures
"""

import sqlite3
import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from src.gui.setup_wizard import ColumnDefinition

class DynamicDatabaseManager:
    """Manages SQLite database operations for dynamic catalogue structures"""
    
    def __init__(self, db_path: str = "data/dynamic_catalogue.db"):
        """Initialize dynamic database manager
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.catalogue_config = None
        self._ensure_data_directory()
        self._initialize_database()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def _initialize_database(self):
        """Create metadata tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create catalogue configuration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS catalogue_config (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    columns_json TEXT NOT NULL,
                    created_date TEXT,
                    modified_date TEXT
                )
            ''')
            
            conn.commit()
    
    def create_catalogue_structure(self, config: Dict) -> bool:
        """Create a new catalogue structure
        
        Args:
            config: Dictionary containing catalogue name and column definitions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            catalogue_name = config['name']
            columns = [ColumnDefinition.from_dict(col) for col in config['columns']]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Store catalogue configuration
                current_time = datetime.now().isoformat()
                cursor.execute('''
                    INSERT OR REPLACE INTO catalogue_config 
                    (id, name, columns_json, created_date, modified_date)
                    VALUES (1, ?, ?, ?, ?)
                ''', (catalogue_name, json.dumps(config['columns']), current_time, current_time))
                
                # Drop existing items table if it exists
                cursor.execute('DROP TABLE IF EXISTS catalogue_items')
                
                # Create dynamic items table
                table_sql = self._generate_table_sql(columns)
                cursor.execute(table_sql)
                
                conn.commit()
                
            self.catalogue_config = config
            return True
            
        except Exception as e:
            print(f"Error creating catalogue structure: {e}")
            return False
    
    def _generate_table_sql(self, columns: List[ColumnDefinition]) -> str:
        """Generate SQL for creating the dynamic items table
        
        Args:
            columns: List of column definitions
            
        Returns:
            SQL CREATE TABLE statement
        """
        sql_parts = ["CREATE TABLE catalogue_items ("]
        sql_parts.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
        
        for column in columns:
            sql_type = self._get_sql_type(column.data_type)
            null_constraint = "NOT NULL" if column.required else ""
            default_constraint = f"DEFAULT '{column.default_value}'" if column.default_value else ""
            
            sql_parts.append(f"    {column.name} {sql_type} {null_constraint} {default_constraint},")
        
        # Add metadata columns
        sql_parts.append("    created_date TEXT,")
        sql_parts.append("    modified_date TEXT")
        sql_parts.append(")")
        
        return "\n".join(sql_parts)
    
    def _get_sql_type(self, data_type: str) -> str:
        """Convert column data type to SQL type
        
        Args:
            data_type: Column data type
            
        Returns:
            SQL data type
        """
        type_mapping = {
            'text': 'TEXT',
            'number': 'INTEGER',
            'decimal': 'REAL',
            'date': 'TEXT',
            'boolean': 'INTEGER'
        }
        return type_mapping.get(data_type, 'TEXT')
    
    def load_catalogue_config(self) -> Optional[Dict]:
        """Load the current catalogue configuration
        
        Returns:
            Configuration dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name, columns_json FROM catalogue_config WHERE id = 1')
                row = cursor.fetchone()
                
                if row:
                    name, columns_json = row
                    columns = json.loads(columns_json)
                    config = {
                        'name': name,
                        'columns': columns
                    }
                    self.catalogue_config = config
                    return config
                
        except Exception as e:
            print(f"Error loading catalogue config: {e}")
        
        return None
    
    def add_item(self, item_data: Dict) -> int:
        """Add a new item to the catalogue
        
        Args:
            item_data: Dictionary containing item information
            
        Returns:
            ID of the newly created item
        """
        if not self.catalogue_config:
            raise Exception("No catalogue structure defined")
        
        current_time = datetime.now().isoformat()
        columns = [ColumnDefinition.from_dict(col) for col in self.catalogue_config['columns']]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare column names and values
            column_names = [col.name for col in columns] + ['created_date', 'modified_date']
            placeholders = ['?' for _ in column_names]
            
            # Prepare values with type conversion
            values = []
            for col in columns:
                raw_value = item_data.get(col.name, col.default_value)
                converted_value = self._convert_value(raw_value, col.data_type)
                values.append(converted_value)
            
            values.extend([current_time, current_time])
            
            # Execute insert
            sql = f"INSERT INTO catalogue_items ({', '.join(column_names)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(sql, values)
            
            return cursor.lastrowid
    
    def get_all_items(self) -> List[Dict]:
        """Retrieve all items from the catalogue
        
        Returns:
            List of item dictionaries
        """
        if not self.catalogue_config:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM catalogue_items ORDER BY id')
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_item_by_id(self, item_id: int) -> Optional[Dict]:
        """Get a specific item by ID
        
        Args:
            item_id: ID of the item
            
        Returns:
            Item dictionary or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM catalogue_items WHERE id = ?', (item_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
    
    def update_item(self, item_id: int, item_data: Dict) -> bool:
        """Update an existing item
        
        Args:
            item_id: ID of the item to update
            item_data: Dictionary containing updated item information
            
        Returns:
            True if update was successful, False otherwise
        """
        if not self.catalogue_config:
            return False
        
        current_time = datetime.now().isoformat()
        columns = [ColumnDefinition.from_dict(col) for col in self.catalogue_config['columns']]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare update statement
            set_clauses = []
            values = []
            
            for col in columns:
                if col.name in item_data:
                    set_clauses.append(f"{col.name} = ?")
                    raw_value = item_data[col.name]
                    converted_value = self._convert_value(raw_value, col.data_type)
                    values.append(converted_value)
            
            set_clauses.append("modified_date = ?")
            values.append(current_time)
            values.append(item_id)
            
            sql = f"UPDATE catalogue_items SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(sql, values)
            
            return cursor.rowcount > 0
    
    def delete_item(self, item_id: int) -> bool:
        """Delete an item from the catalogue
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM catalogue_items WHERE id = ?', (item_id,))
            return cursor.rowcount > 0
    
    def search_items(self, search_term: str) -> List[Dict]:
        """Search items across all text columns
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching item dictionaries
        """
        if not self.catalogue_config:
            return []
        
        columns = [ColumnDefinition.from_dict(col) for col in self.catalogue_config['columns']]
        text_columns = [col.name for col in columns if col.data_type == 'text']
        
        if not text_columns:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build search query for text columns
            search_conditions = []
            search_params = []
            
            for col_name in text_columns:
                search_conditions.append(f"{col_name} LIKE ?")
                search_params.append(f"%{search_term}%")
            
            sql = f"SELECT * FROM catalogue_items WHERE {' OR '.join(search_conditions)} ORDER BY id"
            cursor.execute(sql, search_params)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_column_values(self, column_name: str) -> List[str]:
        """Get all unique values for a specific column
        
        Args:
            column_name: Name of the column
            
        Returns:
            List of unique values
        """
        if not self.catalogue_config:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(f'SELECT DISTINCT {column_name} FROM catalogue_items WHERE {column_name} IS NOT NULL AND {column_name} != "" ORDER BY {column_name}')
                rows = cursor.fetchall()
                return [row[0] for row in rows]
            except sqlite3.OperationalError:
                return []
    
    def _convert_value(self, value: Any, data_type: str) -> Any:
        """Convert value to appropriate type for database storage
        
        Args:
            value: Raw value
            data_type: Target data type
            
        Returns:
            Converted value
        """
        if value is None or value == '':
            return None
        
        try:
            if data_type == 'number':
                return int(value)
            elif data_type == 'decimal':
                return float(value)
            elif data_type == 'boolean':
                if isinstance(value, bool):
                    return 1 if value else 0
                elif isinstance(value, str):
                    return 1 if value.lower() in ('true', '1', 'yes', 'on') else 0
                else:
                    return 1 if value else 0
            else:  # text, date
                return str(value)
        except (ValueError, TypeError):
            return value  # Return original value if conversion fails
    
    def get_table_info(self) -> List[Dict]:
        """Get information about the current table structure
        
        Returns:
            List of column information dictionaries
        """
        if not self.catalogue_config:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("PRAGMA table_info(catalogue_items)")
                rows = cursor.fetchall()
                
                return [{
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': row[3],
                    'dflt_value': row[4],
                    'pk': row[5]
                } for row in rows]
            except sqlite3.OperationalError:
                return []
