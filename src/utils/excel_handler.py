"""
Excel import/export functionality for crafting components
"""

import pandas as pd
from typing import List, Dict
import os

class ExcelHandler:
    """Handles Excel import and export operations"""
    
    def __init__(self):
        """Initialize Excel handler"""
        pass
    
    def import_from_excel(self, file_path: str) -> List[Dict]:
        """Import components from Excel file
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            List of component dictionaries
            
        Raises:
            Exception: If file cannot be read or format is invalid
        """
        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Expected columns (case-insensitive)
            expected_columns = {
                'name': ['name', 'component name', 'item name'],
                'category': ['category', 'type', 'group'],
                'description': ['description', 'desc', 'details'],
                'quantity': ['quantity', 'qty', 'amount', 'count'],
                'unit': ['unit', 'units', 'measurement'],
                'cost_per_unit': ['cost per unit', 'cost/unit', 'price', 'unit cost', 'cost'],
                'supplier': ['supplier', 'vendor', 'source'],
                'location': ['location', 'storage', 'place'],
                'notes': ['notes', 'comments', 'remarks']
            }
            
            # Normalize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Map columns to standard names
            column_mapping = {}
            for standard_name, possible_names in expected_columns.items():
                for col in df.columns:
                    if col in possible_names:
                        column_mapping[col] = standard_name
                        break
            
            # Rename columns
            df = df.rename(columns=column_mapping)
            
            # Ensure required columns exist
            if 'name' not in df.columns:
                raise Exception("Excel file must contain a 'name' or 'component name' column")
            
            # Fill missing columns with default values
            for standard_name in expected_columns.keys():
                if standard_name not in df.columns:
                    if standard_name == 'quantity':
                        df[standard_name] = 0
                    elif standard_name == 'unit':
                        df[standard_name] = 'pieces'
                    elif standard_name == 'cost_per_unit':
                        df[standard_name] = 0.0
                    else:
                        df[standard_name] = ''
            
            # Clean and validate data
            df = df.fillna('')  # Replace NaN with empty strings
            df['name'] = df['name'].astype(str).str.strip()
            df['category'] = df['category'].astype(str).str.strip()
            df['description'] = df['description'].astype(str).str.strip()
            df['unit'] = df['unit'].astype(str).str.strip()
            df['supplier'] = df['supplier'].astype(str).str.strip()
            df['location'] = df['location'].astype(str).str.strip()
            df['notes'] = df['notes'].astype(str).str.strip()
            
            # Convert numeric columns
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
            df['cost_per_unit'] = pd.to_numeric(df['cost_per_unit'], errors='coerce').fillna(0.0)
            
            # Filter out rows with empty names
            df = df[df['name'].str.len() > 0]
            
            # Convert to list of dictionaries
            components = []
            for _, row in df.iterrows():
                component = {
                    'name': row['name'],
                    'category': row['category'] if row['category'] else '',
                    'description': row['description'] if row['description'] else '',
                    'quantity': int(row['quantity']),
                    'unit': row['unit'] if row['unit'] else 'pieces',
                    'cost_per_unit': float(row['cost_per_unit']),
                    'supplier': row['supplier'] if row['supplier'] else '',
                    'location': row['location'] if row['location'] else '',
                    'notes': row['notes'] if row['notes'] else ''
                }
                components.append(component)
            
            return components
            
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def export_to_excel(self, components: List[Dict], file_path: str):
        """Export components to Excel file
        
        Args:
            components: List of component dictionaries
            file_path: Path where to save the Excel file
            
        Raises:
            Exception: If file cannot be written
        """
        try:
            # Create DataFrame from components
            df = pd.DataFrame(components)
            
            # Select and order columns for export
            export_columns = [
                'name', 'category', 'description', 'quantity', 'unit',
                'cost_per_unit', 'supplier', 'location', 'notes'
            ]
            
            # Filter to only include existing columns
            available_columns = [col for col in export_columns if col in df.columns]
            df_export = df[available_columns]
            
            # Rename columns for better readability
            column_names = {
                'name': 'Component Name',
                'category': 'Category',
                'description': 'Description',
                'quantity': 'Quantity',
                'unit': 'Unit',
                'cost_per_unit': 'Cost per Unit',
                'supplier': 'Supplier',
                'location': 'Location',
                'notes': 'Notes'
            }
            
            df_export = df_export.rename(columns=column_names)
            
            # Create Excel writer with formatting
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_export.to_excel(writer, sheet_name='Components', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Components']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Format header row
                from openpyxl.styles import Font, PatternFill
                
                header_font = Font(bold=True)
                header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                
                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
            
        except Exception as e:
            raise Exception(f"Error writing Excel file: {str(e)}")
    
    def validate_excel_format(self, file_path: str) -> Dict[str, any]:
        """Validate Excel file format and return information about it
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Dictionary with validation results
        """
        try:
            df = pd.read_excel(file_path)
            
            result = {
                'valid': True,
                'rows': len(df),
                'columns': list(df.columns),
                'has_name_column': False,
                'errors': []
            }
            
            # Check for name column
            df.columns = df.columns.str.lower().str.strip()
            name_columns = ['name', 'component name', 'item name']
            
            for col in df.columns:
                if col in name_columns:
                    result['has_name_column'] = True
                    break
            
            if not result['has_name_column']:
                result['valid'] = False
                result['errors'].append("Missing required 'name' or 'component name' column")
            
            return result
            
        except Exception as e:
            return {
                'valid': False,
                'rows': 0,
                'columns': [],
                'has_name_column': False,
                'errors': [f"Error reading file: {str(e)}"]
            }
