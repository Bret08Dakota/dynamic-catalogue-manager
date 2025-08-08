"""
Dynamic PDF export functionality for custom catalogue structures
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import List, Dict, Any
from datetime import datetime
from src.gui.setup_wizard import ColumnDefinition

class DynamicPDFExporter:
    """Handles PDF export operations for dynamic catalogues"""
    
    def __init__(self, catalogue_config: Dict):
        """Initialize PDF exporter with catalogue configuration
        
        Args:
            catalogue_config: Dictionary containing catalogue name and column definitions
        """
        self.catalogue_config = catalogue_config
        self.columns = [ColumnDefinition.from_dict(col) for col in catalogue_config['columns']]
        self.styles = getSampleStyleSheet()
        
    def export_to_pdf(self, items: List[Dict], file_path: str, 
                     title: str = None, include_summary: bool = True):
        """Export items to PDF file
        
        Args:
            items: List of item dictionaries
            file_path: Path where to save the PDF file
            title: Custom title for the PDF document
            include_summary: Whether to include summary statistics
            
        Raises:
            Exception: If PDF cannot be created
        """
        try:
            # Use catalogue name as default title
            if not title:
                title = self.catalogue_config['name']
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4, 
                                  leftMargin=0.75*inch, rightMargin=0.75*inch,
                                  topMargin=1*inch, bottomMargin=0.75*inch)
            story = []
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=1,  # Center alignment
                textColor=colors.darkblue
            )
            story.append(Paragraph(title, title_style))
            
            # Add generation date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=1,  # Center alignment
                spaceAfter=20,
                textColor=colors.grey
            )
            current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            story.append(Paragraph(f"Generated on {current_date}", date_style))
            
            # Add summary if requested
            if include_summary and items:
                self._add_summary_section(story, items)
            
            # Add main table
            if not items:
                story.append(Paragraph("No items found in the catalogue.", self.styles['Normal']))
            else:
                self._add_main_table(story, items)
            
            # Add detailed sections for text-heavy columns
            text_columns = [col for col in self.columns if col.data_type == 'text' and 
                          ('note' in col.name.lower() or 'description' in col.name.lower() or 
                           'comment' in col.name.lower())]
            
            if text_columns and any(item.get(col.name) for item in items for col in text_columns):
                story.append(PageBreak())
                self._add_detailed_section(story, items, text_columns)
            
            # Build PDF
            doc.build(story)
            
        except Exception as e:
            raise Exception(f"Error creating PDF: {str(e)}")
    
    def _add_summary_section(self, story: List, items: List[Dict]):
        """Add summary statistics section
        
        Args:
            story: PDF story elements list
            items: List of item dictionaries
        """
        # Summary section
        summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            leftIndent=20,
            rightIndent=20
        )
        
        total_items = len(items)
        
        # Calculate statistics for numeric columns
        numeric_stats = {}
        for column in self.columns:
            if column.data_type in ['number', 'decimal']:
                values = []
                for item in items:
                    value = item.get(column.name)
                    if value is not None:
                        try:
                            values.append(float(value))
                        except (ValueError, TypeError):
                            pass
                
                if values:
                    numeric_stats[column.display_name] = {
                        'total': sum(values),
                        'average': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values)
                    }
        
        # Build summary text
        summary_parts = [f"<b>Catalogue Summary:</b><br/>"]
        summary_parts.append(f"Total Items: {total_items}<br/>")
        
        # Add numeric summaries
        for col_name, stats in numeric_stats.items():
            if col_name.lower() in ['cost', 'price', 'value']:
                summary_parts.append(f"Total {col_name}: ${stats['total']:.2f}<br/>")
                summary_parts.append(f"Average {col_name}: ${stats['average']:.2f}<br/>")
            elif col_name.lower() in ['quantity', 'count', 'amount']:
                summary_parts.append(f"Total {col_name}: {stats['total']:,.0f}<br/>")
                summary_parts.append(f"Average {col_name}: {stats['average']:.1f}<br/>")
            else:
                summary_parts.append(f"Total {col_name}: {stats['total']:.2f}<br/>")
        
        # Add category breakdown if there's a category-like column
        category_columns = [col for col in self.columns if 
                          'category' in col.name.lower() or 'type' in col.name.lower() or 
                          'group' in col.name.lower()]
        
        if category_columns:
            cat_col = category_columns[0]
            categories = {}
            for item in items:
                cat_value = item.get(cat_col.name, 'Uncategorized')
                if cat_value:
                    categories[cat_value] = categories.get(cat_value, 0) + 1
            
            if len(categories) > 1:
                summary_parts.append(f"<br/><b>{cat_col.display_name} Breakdown:</b><br/>")
                for cat, count in sorted(categories.items()):
                    percentage = (count / total_items) * 100
                    summary_parts.append(f"• {cat}: {count} items ({percentage:.1f}%)<br/>")
        
        summary_text = "".join(summary_parts)
        story.append(Paragraph(summary_text, summary_style))
        story.append(Spacer(1, 20))
    
    def _add_main_table(self, story: List, items: List[Dict]):
        """Add main data table
        
        Args:
            story: PDF story elements list
            items: List of item dictionaries
        """
        # Determine which columns to include in main table
        # Exclude very long text columns (notes, descriptions)
        table_columns = []
        for column in self.columns:
            if column.data_type == 'text' and ('note' in column.name.lower() or 
                                             'description' in column.name.lower() or
                                             'comment' in column.name.lower()):
                # Skip long text columns - they'll go in detailed section
                continue
            table_columns.append(column)
        
        if not table_columns:
            table_columns = self.columns[:4]  # Show first 4 columns if all are text
        
        # Create table data
        table_data = []
        
        # Table headers
        headers = [col.display_name for col in table_columns]
        table_data.append(headers)
        
        # Add item data
        for item in items:
            row = []
            for column in table_columns:
                value = item.get(column.name, '')
                formatted_value = self._format_value_for_pdf(value, column)
                
                # Truncate long values for table display
                if len(str(formatted_value)) > 30:
                    formatted_value = str(formatted_value)[:27] + "..."
                
                row.append(formatted_value)
            table_data.append(row)
        
        # Calculate column widths based on content and page width
        available_width = 7 * inch  # Page width minus margins
        col_widths = self._calculate_column_widths(table_data, available_width)
        
        # Create table
        table = Table(table_data, colWidths=col_widths)
        
        # Style the table
        table_style = TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ])
        
        # Right-align numeric columns
        for col_idx, column in enumerate(table_columns):
            if column.data_type in ['number', 'decimal']:
                table_style.add('ALIGN', (col_idx, 1), (col_idx, -1), 'RIGHT')
        
        table.setStyle(table_style)
        story.append(table)
    
    def _add_detailed_section(self, story: List, items: List[Dict], text_columns: List[ColumnDefinition]):
        """Add detailed section for long text fields
        
        Args:
            story: PDF story elements list
            items: List of item dictionaries
            text_columns: List of text columns to include
        """
        story.append(Paragraph("Detailed Information", self.styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Find a good identifier column (first column or name-like column)
        id_column = self.columns[0]
        for col in self.columns:
            if 'name' in col.name.lower() or 'title' in col.name.lower():
                id_column = col
                break
        
        for i, item in enumerate(items, 1):
            # Check if this item has any detailed text
            has_details = any(item.get(col.name) for col in text_columns)
            if not has_details:
                continue
            
            # Item header
            item_id = item.get(id_column.name, f'Item {i}')
            header_style = ParagraphStyle(
                'ItemHeader',
                parent=self.styles['Heading3'],
                fontSize=12,
                spaceAfter=8,
                textColor=colors.darkblue,
                leftIndent=10
            )
            story.append(Paragraph(f"{i}. {item_id}", header_style))
            
            # Add detailed text fields
            for column in text_columns:
                value = item.get(column.name)
                if value and str(value).strip():
                    detail_style = ParagraphStyle(
                        'DetailStyle',
                        parent=self.styles['Normal'],
                        fontSize=10,
                        spaceAfter=6,
                        leftIndent=20,
                        rightIndent=10
                    )
                    
                    detail_text = f"<b>{column.display_name}:</b> {str(value)}"
                    story.append(Paragraph(detail_text, detail_style))
            
            story.append(Spacer(1, 10))
    
    def _format_value_for_pdf(self, value: Any, column: ColumnDefinition) -> str:
        """Format value for PDF display
        
        Args:
            value: Raw value
            column: Column definition
            
        Returns:
            Formatted string
        """
        if value is None or value == '':
            return ''
        
        if column.data_type == 'boolean':
            if isinstance(value, bool):
                return 'Yes' if value else 'No'
            elif isinstance(value, (int, str)):
                return 'Yes' if bool(value) else 'No'
            else:
                return 'No'
        elif column.data_type == 'decimal':
            try:
                num_value = float(value)
                if 'cost' in column.name.lower() or 'price' in column.name.lower():
                    return f"${num_value:.2f}"
                else:
                    return f"{num_value:.2f}"
            except (ValueError, TypeError):
                return str(value)
        elif column.data_type == 'number':
            try:
                return f"{int(value):,}"  # Add thousands separators
            except (ValueError, TypeError):
                return str(value)
        else:
            return str(value)
    
    def _calculate_column_widths(self, table_data: List[List], available_width: float) -> List[float]:
        """Calculate optimal column widths
        
        Args:
            table_data: Table data including headers
            available_width: Available width for the table
            
        Returns:
            List of column widths
        """
        if not table_data or not table_data[0]:
            return []
        
        num_cols = len(table_data[0])
        
        # Calculate content-based widths
        col_max_lengths = []
        for col_idx in range(num_cols):
            max_length = 0
            for row in table_data:
                if col_idx < len(row):
                    cell_length = len(str(row[col_idx]))
                    max_length = max(max_length, cell_length)
            col_max_lengths.append(max_length)
        
        # Convert to proportional widths
        total_chars = sum(col_max_lengths)
        if total_chars == 0:
            # Equal widths if no content
            return [available_width / num_cols] * num_cols
        
        # Calculate proportional widths with min/max constraints
        col_widths = []
        min_width = available_width * 0.1  # Minimum 10% of available width
        max_width = available_width * 0.4   # Maximum 40% of available width
        
        for max_length in col_max_lengths:
            proportion = max_length / total_chars
            width = available_width * proportion
            width = max(min_width, min(width, max_width))
            col_widths.append(width)
        
        # Adjust if total exceeds available width
        total_width = sum(col_widths)
        if total_width > available_width:
            scale_factor = available_width / total_width
            col_widths = [w * scale_factor for w in col_widths]
        
        return col_widths
    
    def export_category_summary_pdf(self, items: List[Dict], file_path: str):
        """Export category summary to PDF
        
        Args:
            items: List of item dictionaries
            file_path: Path where to save the PDF file
        """
        # Find category-like columns
        category_columns = [col for col in self.columns if 
                          'category' in col.name.lower() or 'type' in col.name.lower() or 
                          'group' in col.name.lower()]
        
        if not category_columns:
            raise Exception("No category column found for summary")
        
        category_column = category_columns[0]
        
        # Group items by category
        categories = {}
        for item in items:
            category = item.get(category_column.name, 'Uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'SummaryTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                spaceAfter=20,
                alignment=1,
                textColor=colors.darkblue
            )
            story.append(Paragraph(f"{self.catalogue_config['name']} - Summary by {category_column.display_name}", title_style))
            
            # Generation date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=1,
                spaceAfter=30,
                textColor=colors.grey
            )
            current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            story.append(Paragraph(f"Generated on {current_date}", date_style))
            
            # Category summaries
            for category, category_items in sorted(categories.items()):
                # Category header
                category_style = ParagraphStyle(
                    'CategoryHeader',
                    parent=self.styles['Heading2'],
                    fontSize=14,
                    spaceAfter=10,
                    textColor=colors.darkgreen
                )
                story.append(Paragraph(f"{category_column.display_name}: {category}", category_style))
                
                # Category statistics
                total_items = len(category_items)
                
                # Calculate numeric totals for this category
                numeric_totals = {}
                for column in self.columns:
                    if column.data_type in ['number', 'decimal']:
                        total = 0
                        for item in category_items:
                            value = item.get(column.name, 0)
                            try:
                                total += float(value) if value is not None else 0
                            except (ValueError, TypeError):
                                pass
                        numeric_totals[column.display_name] = total
                
                stats_parts = [f"Items: {total_items}"]
                for col_name, total in numeric_totals.items():
                    if total > 0:
                        if 'cost' in col_name.lower() or 'price' in col_name.lower():
                            stats_parts.append(f"Total {col_name}: ${total:.2f}")
                        else:
                            stats_parts.append(f"Total {col_name}: {total:,.0f}")
                
                stats_text = " | ".join(stats_parts)
                story.append(Paragraph(stats_text, self.styles['Normal']))
                story.append(Spacer(1, 10))
                
                # Create mini table for this category
                self._add_category_table(story, category_items)
                story.append(Spacer(1, 20))
            
            doc.build(story)
            
        except Exception as e:
            raise Exception(f"Error creating category summary PDF: {str(e)}")
    
    def _add_category_table(self, story: List, items: List[Dict]):
        """Add a table for a specific category
        
        Args:
            story: PDF story elements list
            items: List of item dictionaries for this category
        """
        # Use first few columns for category table
        display_columns = self.columns[:min(4, len(self.columns))]
        
        table_data = []
        headers = [col.display_name for col in display_columns]
        table_data.append(headers)
        
        for item in items:
            row = []
            for column in display_columns:
                value = item.get(column.name, '')
                formatted_value = self._format_value_for_pdf(value, column)
                
                # Truncate for category table
                if len(str(formatted_value)) > 25:
                    formatted_value = str(formatted_value)[:22] + "..."
                
                row.append(formatted_value)
            table_data.append(row)
        
        # Create smaller table
        available_width = 6 * inch
        col_widths = self._calculate_column_widths(table_data, available_width)
        
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
