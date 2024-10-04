import tkinter as tk
from tkinter import ttk
import platform  # Used to detect the operating system

from .import_dss_tab import create_tab1
from .get_weather_events_tab import create_tab2
from .format_weather_tab import create_tab3
from .find_extreme_tab import create_tab4
from .generate_weather_impact_tab import create_tab5
from .generate_outage_map_tab import create_tab6

def maximize_window(root):
    """Maximizes the window based on the operating system."""
    current_os = platform.system()
    
    if current_os == "Windows":
        # Maximize on Windows
        root.state('zoomed')
    elif current_os == "Darwin":  # macOS
        # macOS doesn't support '-zoomed', so we set fullscreen or large size manually
        root.attributes('-fullscreen', True)
        root.bind("<Escape>", lambda event: root.attributes('-fullscreen', False))  # Allow exiting fullscreen with Escape
    else:
        # For Linux or other systems
        try:
            root.attributes('-zoomed', True)  # Try to zoom (maximize) the window
        except:
            # If '-zoomed' is not supported, manually set window size to full screen dimensions
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.geometry(f"{screen_width}x{screen_height}")

def main():
    root = tk.Tk()
    root.title("Outage Map GUI")

    # Maximize the window based on the operating system
    maximize_window(root)

    # Create a notebook (tabs container)
    notebook = ttk.Notebook(root)

    # Create tabs using the imported functions
    create_tab1(notebook)
    create_tab2(notebook)
    create_tab3(notebook)
    create_tab4(notebook)
    create_tab5(notebook)
    create_tab6(notebook)

    # Pack the notebook to make it visible
    notebook.pack(expand=True, fill='both')

    root.mainloop()

if __name__ == "__main__":
    main()
