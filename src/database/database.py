"""
Database module for managing crafting components data
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class DatabaseManager:
    """Manages SQLite database operations for crafting components"""
    
    def __init__(self, db_path: str = "data/crafting_catalogue.db"):
        """Initialize database manager
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_directory()
        self._initialize_database()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def _initialize_database(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create components table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS components (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    quantity INTEGER DEFAULT 0,
                    unit TEXT DEFAULT 'pieces',
                    cost_per_unit REAL DEFAULT 0.0,
                    supplier TEXT,
                    location TEXT,
                    notes TEXT,
                    created_date TEXT,
                    modified_date TEXT
                )
            ''')
            
            # Create categories table for better organization
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_date TEXT
                )
            ''')
            
            conn.commit()
    
    def add_component(self, component_data: Dict) -> int:
        """Add a new component to the database
        
        Args:
            component_data: Dictionary containing component information
            
        Returns:
            ID of the newly created component
        """
        current_time = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO components (
                    name, category, description, quantity, unit, 
                    cost_per_unit, supplier, location, notes, 
                    created_date, modified_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                component_data.get('name', ''),
                component_data.get('category', ''),
                component_data.get('description', ''),
                component_data.get('quantity', 0),
                component_data.get('unit', 'pieces'),
                component_data.get('cost_per_unit', 0.0),
                component_data.get('supplier', ''),
                component_data.get('location', ''),
                component_data.get('notes', ''),
                current_time,
                current_time
            ))
            
            return cursor.lastrowid
    
    def get_all_components(self) -> List[Dict]:
        """Retrieve all components from the database
        
        Returns:
            List of component dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM components ORDER BY name')
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_component_by_id(self, component_id: int) -> Optional[Dict]:
        """Get a specific component by ID
        
        Args:
            component_id: ID of the component
            
        Returns:
            Component dictionary or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM components WHERE id = ?', (component_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
    
    def update_component(self, component_id: int, component_data: Dict) -> bool:
        """Update an existing component
        
        Args:
            component_id: ID of the component to update
            component_data: Dictionary containing updated component information
            
        Returns:
            True if update was successful, False otherwise
        """
        current_time = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE components SET
                    name = ?, category = ?, description = ?, quantity = ?,
                    unit = ?, cost_per_unit = ?, supplier = ?, location = ?,
                    notes = ?, modified_date = ?
                WHERE id = ?
            ''', (
                component_data.get('name', ''),
                component_data.get('category', ''),
                component_data.get('description', ''),
                component_data.get('quantity', 0),
                component_data.get('unit', 'pieces'),
                component_data.get('cost_per_unit', 0.0),
                component_data.get('supplier', ''),
                component_data.get('location', ''),
                component_data.get('notes', ''),
                current_time,
                component_id
            ))
            
            return cursor.rowcount > 0
    
    def delete_component(self, component_id: int) -> bool:
        """Delete a component from the database
        
        Args:
            component_id: ID of the component to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM components WHERE id = ?', (component_id,))
            return cursor.rowcount > 0
    
    def search_components(self, search_term: str) -> List[Dict]:
        """Search components by name, category, or description
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching component dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            cursor.execute('''
                SELECT * FROM components 
                WHERE name LIKE ? OR category LIKE ? OR description LIKE ?
                ORDER BY name
            ''', (search_pattern, search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories from components
        
        Returns:
            List of category names
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT category FROM components WHERE category IS NOT NULL AND category != "" ORDER BY category')
            rows = cursor.fetchall()
            return [row[0] for row in rows]
    
    def get_components_by_category(self, category: str) -> List[Dict]:
        """Get all components in a specific category
        
        Args:
            category: Category name
            
        Returns:
            List of component dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM components WHERE category = ? ORDER BY name', (category,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
