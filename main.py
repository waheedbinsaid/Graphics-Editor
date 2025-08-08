# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase

# Import from our new modules
from styles import STYLESHEET
from main_window import ProfessionalEditor

def main():
    """Main function to initialize and run the application."""
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    # Load the custom Urdu font
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
    except NameError:
        # Fallback for environments where __file__ is not defined
        script_dir = os.getcwd()

    font_path = os.path.join(script_dir, "Jameel Noori Nastaleeq Regular.ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)
    else:
        print(f"Warning: Font 'Jameel Noori Nastaleeq Regular.ttf' not found at {font_path}")

    # Create and show the main window
    editor = ProfessionalEditor()
    editor.show()

    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
