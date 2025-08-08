"""
PDF export functionality for crafting components catalogue
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import List, Dict
from datetime import datetime

class PDFExporter:
    """Handles PDF export operations for the catalogue"""
    
    def __init__(self):
        """Initialize PDF exporter"""
        self.styles = getSampleStyleSheet()
        
    def export_to_pdf(self, components: List[Dict], file_path: str, title: str = "Crafting Components Catalogue"):
        """Export components to PDF file
        
        Args:
            components: List of component dictionaries
            file_path: Path where to save the PDF file
            title: Title for the PDF document
            
        Raises:
            Exception: If PDF cannot be created
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph(title, title_style))
            
            # Add generation date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=1,  # Center alignment
                spaceAfter=20
            )
            current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            story.append(Paragraph(f"Generated on {current_date}", date_style))
            
            # Add summary
            summary_style = ParagraphStyle(
                'SummaryStyle',
                parent=self.styles['Normal'],
                fontSize=12,
                spaceAfter=20
            )
            total_components = len(components)
            total_quantity = sum(comp.get('quantity', 0) for comp in components)
            total_value = sum(comp.get('quantity', 0) * comp.get('cost_per_unit', 0) for comp in components)
            
            summary_text = f"""
            <b>Catalogue Summary:</b><br/>
            Total Components: {total_components}<br/>
            Total Items: {total_quantity}<br/>
            Total Estimated Value: ${total_value:.2f}
            """
            story.append(Paragraph(summary_text, summary_style))
            story.append(Spacer(1, 20))
            
            if not components:
                story.append(Paragraph("No components found in the catalogue.", self.styles['Normal']))
            else:
                # Create table data
                table_data = []
                
                # Table headers
                headers = ['Name', 'Category', 'Qty', 'Unit', 'Cost/Unit', 'Total Value', 'Supplier', 'Location']
                table_data.append(headers)
                
                # Add component data
                for component in components:
                    quantity = component.get('quantity', 0)
                    cost_per_unit = component.get('cost_per_unit', 0.0)
                    total_value = quantity * cost_per_unit
                    
                    row = [
                        component.get('name', '')[:20],  # Truncate long names
                        component.get('category', '')[:15],
                        str(quantity),
                        component.get('unit', '')[:10],
                        f"${cost_per_unit:.2f}",
                        f"${total_value:.2f}",
                        component.get('supplier', '')[:15],
                        component.get('location', '')[:15]
                    ]
                    table_data.append(row)
                
                # Create table
                table = Table(table_data)
                
                # Style the table
                table_style = TableStyle([
                    # Header row styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    
                    # Data rows styling
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (2, 1), (5, -1), 'RIGHT'),  # Right align numeric columns
                    
                    # Grid styling
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Alternating row colors
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.lightgrey])
                ])
                
                table.setStyle(table_style)
                story.append(table)
                
                # Add detailed descriptions if available
                if any(comp.get('description') or comp.get('notes') for comp in components):
                    story.append(Spacer(1, 30))
                    story.append(Paragraph("Component Details", self.styles['Heading2']))
                    story.append(Spacer(1, 10))
                    
                    for component in components:
                        if component.get('description') or component.get('notes'):
                            name = component.get('name', 'Unknown')
                            description = component.get('description', '')
                            notes = component.get('notes', '')
                            
                            detail_text = f"<b>{name}</b><br/>"
                            if description:
                                detail_text += f"Description: {description}<br/>"
                            if notes:
                                detail_text += f"Notes: {notes}<br/>"
                            
                            story.append(Paragraph(detail_text, self.styles['Normal']))
                            story.append(Spacer(1, 10))
            
            # Build PDF
            doc.build(story)
            
        except Exception as e:
            raise Exception(f"Error creating PDF: {str(e)}")
    
    def export_component_details_pdf(self, components: List[Dict], file_path: str):
        """Export detailed component information to PDF
        
        Args:
            components: List of component dictionaries
            file_path: Path where to save the PDF file
        """
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'DetailTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                alignment=1
            )
            story.append(Paragraph("Detailed Component Information", title_style))
            
            # Generation date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=1,
                spaceAfter=30
            )
            current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            story.append(Paragraph(f"Generated on {current_date}", date_style))
            
            # Component details
            for i, component in enumerate(components, 1):
                # Component header
                header_style = ParagraphStyle(
                    'ComponentHeader',
                    parent=self.styles['Heading3'],
                    fontSize=14,
                    spaceAfter=10,
                    textColor=colors.darkblue
                )
                story.append(Paragraph(f"{i}. {component.get('name', 'Unknown Component')}", header_style))
                
                # Component details table
                details_data = [
                    ['Category:', component.get('category', 'N/A')],
                    ['Quantity:', f"{component.get('quantity', 0)} {component.get('unit', 'pieces')}"],
                    ['Cost per Unit:', f"${component.get('cost_per_unit', 0.0):.2f}"],
                    ['Total Value:', f"${component.get('quantity', 0) * component.get('cost_per_unit', 0.0):.2f}"],
                    ['Supplier:', component.get('supplier', 'N/A')],
                    ['Location:', component.get('location', 'N/A')]
                ]
                
                details_table = Table(details_data, colWidths=[2*inch, 4*inch])
                details_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                story.append(details_table)
                
                # Description and notes
                if component.get('description'):
                    story.append(Spacer(1, 10))
                    story.append(Paragraph(f"<b>Description:</b> {component['description']}", self.styles['Normal']))
                
                if component.get('notes'):
                    story.append(Spacer(1, 5))
                    story.append(Paragraph(f"<b>Notes:</b> {component['notes']}", self.styles['Normal']))
                
                # Add space between components
                story.append(Spacer(1, 20))
            
            doc.build(story)
            
        except Exception as e:
            raise Exception(f"Error creating detailed PDF: {str(e)}")
    
    def export_category_summary_pdf(self, components: List[Dict], file_path: str):
        """Export category summary to PDF
        
        Args:
            components: List of component dictionaries
            file_path: Path where to save the PDF file
        """
        try:
            # Group components by category
            categories = {}
            for component in components:
                category = component.get('category', 'Uncategorized')
                if category not in categories:
                    categories[category] = []
                categories[category].append(component)
            
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'SummaryTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                alignment=1
            )
            story.append(Paragraph("Component Summary by Category", title_style))
            
            # Generation date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=1,
                spaceAfter=30
            )
            current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            story.append(Paragraph(f"Generated on {current_date}", date_style))
            
            # Category summaries
            for category, category_components in sorted(categories.items()):
                # Category header
                category_style = ParagraphStyle(
                    'CategoryHeader',
                    parent=self.styles['Heading2'],
                    fontSize=14,
                    spaceAfter=10,
                    textColor=colors.darkgreen
                )
                story.append(Paragraph(f"Category: {category}", category_style))
                
                # Category statistics
                total_items = len(category_components)
                total_quantity = sum(comp.get('quantity', 0) for comp in category_components)
                total_value = sum(comp.get('quantity', 0) * comp.get('cost_per_unit', 0) for comp in category_components)
                
                stats_text = f"Components: {total_items} | Total Items: {total_quantity} | Total Value: ${total_value:.2f}"
                story.append(Paragraph(stats_text, self.styles['Normal']))
                story.append(Spacer(1, 10))
                
                # Components table for this category
                table_data = [['Name', 'Quantity', 'Unit', 'Cost/Unit', 'Total Value']]
                
                for component in sorted(category_components, key=lambda x: x.get('name', '')):
                    quantity = component.get('quantity', 0)
                    cost_per_unit = component.get('cost_per_unit', 0.0)
                    total_comp_value = quantity * cost_per_unit
                    
                    row = [
                        component.get('name', '')[:30],
                        str(quantity),
                        component.get('unit', '')[:10],
                        f"${cost_per_unit:.2f}",
                        f"${total_comp_value:.2f}"
                    ]
                    table_data.append(row)
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
            
            doc.build(story)
            
        except Exception as e:
            raise Exception(f"Error creating category summary PDF: {str(e)}")
