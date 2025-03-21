# Main launcher file
import tkinter as tk
from password_manager_gui import RetrowavePasswordManagerGUI

def main():
    # Create the main window
    root = tk.Tk()
    
    # Create the app
    app = RetrowavePasswordManagerGUI(root)
    
    # Start the main event loop
    root.mainloop()

# Run the application when this file is executed directly
if __name__ == "__main__":
    main()