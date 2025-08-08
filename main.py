#!/usr/bin/env python3
"""
Crafting Components Catalogue
A desktop application for managing crafting components inventory

Author: Created with Cascade AI
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from src.gui.dynamic_main_window import DynamicMainWindow

def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Dynamic Catalogue Manager")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("DynamicCatalogue")
    
    # Create and show main window
    window = DynamicMainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
