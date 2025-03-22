import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
import password_manager_core as pm
import os
import pygame as pg
import numpy as np
from math import pi, sin, cos
from PIL import Image, ImageTk  # Add this import

# Initialize pygame for the Earth visualization
pg.init()
# Disable sound to prevent audio conflicts
pg.mixer.quit()

class SpinningEarth:
    def __init__(self, width=150, height=150):
        # Set dimensions for the Earth visualization
        self.width = width
        self.height = height
        
        # Create a surface for rendering the Earth
        self.surface = pg.Surface((width, height))
        
        # Set constants
        self.FPS = 30
        self.R = width // 4  # Radius scaled to the surface size
        self.MAP_WIDTH = 139
        self.MAP_HEIGHT = 34
        
        # Initialize font
        self.my_font = pg.font.SysFont('arial', 6)  # Smaller font for the corner display
        
        # Load the Earth ASCII art
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'earth_W140_H35.txt')
        
        try:
            with open(file_path, 'r') as file:
                data = [file.read().replace('\n', '')]
                
            # Process ASCII characters
            self.ascii_chars = []
            for line in data:
                for char in line:
                    self.ascii_chars.append(char)
            
            self.inverted_ascii_chars = self.ascii_chars[::-1]
            
            # Create 3D coordinates
            self.xyz = []
            for i in range(self.MAP_HEIGHT + 1):
                lat = (pi / self.MAP_HEIGHT) * i
                for j in range(self.MAP_WIDTH + 1):
                    lon = (2 * pi / self.MAP_WIDTH) * j
                    x = round(self.R * sin(lat) * cos(lon), 2)
                    y = round(self.R * sin(lat) * sin(lon), 2)
                    z = round(self.R * cos(lat), 2)
                    self.xyz.append((x, y, z))
            
            # Initialize spin angle
            self.spin = 0
            self.loaded = True
            
        except FileNotFoundError:
            print(f"Earth file not found at: {file_path}")
            # Create a simple placeholder file
            self.create_placeholder_earth_file(file_path)
            self.loaded = False
    
    def create_placeholder_earth_file(self, file_path):
        """Create a simple placeholder Earth ASCII art file"""
        try:
            with open(file_path, 'w') as file:
                # Basic ASCII Earth
                earth_art = []
                width, height = 139, 34
                
                for y in range(height):
                    line = ""
                    for x in range(width):
                        dx, dy = x - width // 2, y - height // 2
                        distance = (dx**2 + dy**2)**0.5
                        
                        if distance < width // 4:
                            if (x + y) % 7 == 0:
                                line += "#"  # Continents
                            else:
                                line += "~"  # Oceans
                        else:
                            line += " "
                    earth_art.append(line)
                
                file.write('\n'.join(earth_art))
            print(f"Created placeholder {file_path} file.")
            
            # Now that we created the file, load it
            with open(file_path, 'r') as file:
                data = [file.read().replace('\n', '')]
                
            # Process ASCII characters
            self.ascii_chars = []
            for line in data:
                for char in line:
                    self.ascii_chars.append(char)
            
            self.inverted_ascii_chars = self.ascii_chars[::-1]
            
            # Create 3D coordinates
            self.xyz = []
            for i in range(self.MAP_HEIGHT + 1):
                lat = (pi / self.MAP_HEIGHT) * i
                for j in range(self.MAP_WIDTH + 1):
                    lon = (2 * pi / self.MAP_WIDTH) * j
                    x = round(self.R * sin(lat) * cos(lon), 2)
                    y = round(self.R * sin(lat) * sin(lon), 2)
                    z = round(self.R * cos(lat), 2)
                    self.xyz.append((x, y, z))
                    
            self.loaded = True
            
        except Exception as e:
            print(f"Error creating placeholder Earth file: {e}")
    
    def update(self):
        # Increment the spin angle
        self.spin += 0.05
    
    def render(self):
        if not self.loaded:
            # If the Earth file couldn't be loaded, draw a placeholder
            self.surface.fill((10, 10, 60))
            text = self.my_font.render("Earth file not found", True, (255, 255, 255))
            self.surface.blit(text, (10, self.height // 2))
            return self.surface
        
        # Clear the surface
        self.surface.fill((0, 0, 50))
        
        # Create projection
        pv = self.Projection(self.width, self.height, self.surface)
        
        # Create and render the globe
        globe = self.Object()
        globe_nodes = [i for i in self.xyz]
        globe.addNodes(np.array(globe_nodes))
        pv.addSurface('globe', globe)
        pv.rotateAll(self.spin)
        pv.display(self.inverted_ascii_chars, self.my_font, self.MAP_WIDTH, self.MAP_HEIGHT)
        
        return self.surface
    
    def get_tk_image(self):
        """Convert pygame surface to a tkinter-compatible image"""
        # Render the Earth to a pygame surface
        earth_surface = self.render()
        
        # Get the raw pixel data
        raw_str = pg.image.tostring(earth_surface, 'RGB')
        
        # Create a PIL Image from the raw pixel data
        image = Image.frombytes('RGB', (self.width, self.height), raw_str)
        
        # Convert PIL Image to Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(image)
        
        return tk_image
    
    class Projection:
        def __init__(self, width, height, surface):
            self.width = width
            self.height = height
            self.surface = surface
            self.background = (10, 10, 60)
            self.surfaces = {}

        def addSurface(self, name, surface):
            self.surfaces[name] = surface

        def display(self, inverted_ascii_chars, font, MAP_WIDTH, MAP_HEIGHT):
            i = 0
            for surface in self.surfaces.values():
                for node in surface.nodes:
                    text = inverted_ascii_chars[i]
                    text_surface = font.render(text, False, (0, 255, 0))
                    if i > MAP_WIDTH - 1 and i < (MAP_WIDTH * MAP_HEIGHT - MAP_WIDTH) and node[1] > 0:
                        self.surface.blit(text_surface, (self.width / 2 + int(node[0]), self.height / 2 + int(node[2])))
                    i += 1

        def rotateAll(self, theta):
            for surface in self.surfaces.values():
                center = surface.findCentre()

                c = np.cos(theta)
                s = np.sin(theta)

                # Rotating about Z - axis
                matrix = np.array([[c, -s, 0, 0],
                                  [s, c, 0, 0],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]])

                surface.rotate(center, matrix)
    
    class Object:
        def __init__(self):
            self.nodes = np.zeros((0, 4))

        def addNodes(self, node_array):
            ones_column = np.ones((len(node_array), 1))
            ones_added = np.hstack((node_array, ones_column))
            self.nodes = np.vstack((self.nodes, ones_added))

        def findCentre(self):
            mean = self.nodes.mean(axis=0)
            return mean

        def rotate(self, center, matrix):
            for i, node in enumerate(self.nodes):
                self.nodes[i] = center + np.matmul(matrix, node - center)


class RetrowavePasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("R3TR0 PWMANAGER v1.0")
        self.root.geometry("800x600")
        self.root.configure(bg="#000033")
        
        # Try to load custom fonts for retrowave look
        try:
            # If you have these fonts installed, they'll be used
            self.title_font = font.Font(family="VCR OSD Mono", size=18, weight="bold")
            self.button_font = font.Font(family="VCR OSD Mono", size=11)
            self.text_font = font.Font(family="MS Sans Serif", size=10)
        except:
            # Fallback to system fonts
            self.title_font = font.Font(size=18, weight="bold")
            self.button_font = font.Font(size=11)
            self.text_font = font.Font(size=10)
        
        # Configure style for a retro look
        self.style = ttk.Style()
        
        # Try to load a theme that looks more like old Windows
        try:
            self.style.theme_use('clam')
        except:
            pass
        
        # Configure colors for a retrowave aesthetic
        self.style.configure("TFrame", background="#000033")
        self.style.configure("TButton", 
                            background="#ff00ff", 
                            foreground="#ffffff",
                            font=self.button_font)
        self.style.map("TButton",
                       background=[('active', '#00ccff'), ('pressed', '#0099cc')])
        
        self.style.configure("TLabel", 
                           background="#000033", 
                           foreground="#00ccff",
                           font=self.text_font)
        
        self.style.configure("Header.TLabel", 
                           background="#000033", 
                           foreground="#ff00ff",
                           font=self.title_font)
        
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a header frame with space for Earth in top-right
        header_frame = ttk.Frame(self.main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Left side for ASCII art in header
        header_left = ttk.Frame(header_frame, style="TFrame")
        header_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Right side for Earth in header
        header_right = ttk.Frame(header_frame, style="TFrame", width=150, height=150)
        header_right.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # ASCII art header for the retro feel
        ascii_art = """
   ╔════════════════════════════════════════════╗
   ║  ██████╗ ██╗    ██╗██████╗ ███╗   ███╗ █████╗ ███╗   ██╗ ║
   ║  ██╔══██╗██║    ██║██╔══██╗████╗ ████║██╔══██╗████╗  ██║ ║
   ║  ██████╔╝██║ █╗ ██║██║  ██║██╔████╔██║███████║██╔██╗ ██║ ║
   ║  ██╔═══╝ ██║███╗██║██║  ██║██║╚██╔╝██║██╔══██║██║╚██╗██║ ║
   ║  ██║     ╚███╔███╔╝██████╔╝██║ ╚═╝ ██║██║  ██║██║ ╚████║ ║
   ║  ╚═╝      ╚══╝╚══╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ║
   ╚════════════════════════════════════════════╝
"""
        header_label = tk.Label(header_left, 
                               text=ascii_art, 
                               bg="#000033", 
                               fg="#ff00ff",
                               font=("Courier", 10))
        header_label.pack(pady=5)
        
        slogan_label = ttk.Label(header_left, 
                                text="your passwords are safe...    kinda.", 
                                style="Header.TLabel")
        slogan_label.pack(pady=5)
        
        # Initialize the spinning Earth in the header_right frame
        self.earth = SpinningEarth(width=150, height=150)
        self.earth_label = tk.Label(header_right, bg="#000033")
        self.earth_label.pack(side=tk.RIGHT)
        
        # Buttons in a grid with neon colors
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(pady=10)
        
        # Create custom button style - making them look like old Windows buttons with neon text
        button_style = {
            'relief': 'raised',
            'borderwidth': 2,
            'bg': '#303030',
            'fg': '#00ffff',
            'activebackground': '#505050',
            'activeforeground': '#ff00ff',
            'font': self.button_font,
            'width': 20,
            'height': 2
        }
        
        # Instead of ttk buttons, use tk buttons for more retro styling
        self.add_button = tk.Button(buttons_frame, 
                                  text="ADD CREDENTIAL", 
                                  command=self.add_credential, 
                                  **button_style)
        self.add_button.grid(row=0, column=0, padx=10, pady=10)
        
        self.view_button = tk.Button(buttons_frame, 
                                   text="VIEW CREDENTIALS", 
                                   command=self.view_credentials, 
                                   **button_style)
        self.view_button.grid(row=0, column=1, padx=10, pady=10)
        
        self.search_button = tk.Button(buttons_frame, 
                                     text="SEARCH CREDENTIALS", 
                                     command=self.search_credentials, 
                                     **button_style)
        self.search_button.grid(row=1, column=0, padx=10, pady=10)
        
        self.delete_button = tk.Button(buttons_frame, 
                                     text="DELETE CREDENTIAL", 
                                     command=self.delete_credential, 
                                     **button_style)
        self.delete_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Create a retro-styled display frame
        self.display_frame = tk.Frame(self.main_frame, 
                                    bg="#000000", 
                                    highlightbackground="#00ccff", 
                                    highlightthickness=2)
        self.display_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollable text area with retrowave colors
        self.display_text = tk.Text(self.display_frame, 
                                  wrap=tk.WORD, 
                                  padx=10, 
                                  pady=10, 
                                  bg="#000000", 
                                  fg="#00ffcc", 
                                  insertbackground="#ff00ff",
                                  font=("Consolas", 10),
                                  relief="sunken",
                                  borderwidth=2)
        self.display_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Retro scrollbar
        scrollbar = tk.Scrollbar(self.display_frame, command=self.display_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.display_text.config(yscrollcommand=scrollbar.set)
        
        # Set display text as read-only
        self.display_text.config(state=tk.DISABLED)
        
        # 90s-style status bar
        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM READY...")
        self.status_bar = tk.Label(self.root, 
                                 textvariable=self.status_var, 
                                 bd=1, 
                                 relief=tk.SUNKEN, 
                                 anchor=tk.W,
                                 bg="#303030",
                                 fg="#00ffff",
                                 font=("MS Sans Serif", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Setup periodic Earth update
        self.running = True
        self.update_earth()
    
    def update_earth(self):
        """Update the spinning Earth visualization"""
        if self.running:
            try:
                # Update Earth rotation
                self.earth.update()
                
                # Get the new image
                tk_image = self.earth.get_tk_image()
                
                # Keep a reference to prevent garbage collection
                self.current_earth_image = tk_image
                
                # Update the label
                self.earth_label.configure(image=self.current_earth_image)
                
                # Schedule next update (30 fps = ~33ms)
                self.root.after(33, self.update_earth)
            except Exception as e:
                print(f"Error updating Earth: {e}")
                # Try again in 100ms if there was an error
                self.root.after(100, self.update_earth)

    def update_display_text(self, text):
        """Update the display text area with the given text"""
        self.display_text.config(state=tk.NORMAL)
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, text)
        self.display_text.config(state=tk.DISABLED)
    
    def create_retro_toplevel(self, title, size="400x300"):
        """Create a retro-styled toplevel window"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(size)
        window.configure(bg="#000033")
        window.transient(self.root)
        window.grab_set()
        
        # Center the window relative to the main window
        window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        return window
    
    def add_credential(self):
        """Open a dialog to add a new credential"""
        add_window = self.create_retro_toplevel("ADD NEW CREDENTIAL", "450x350")
        
        # Create inner frame
        frame = tk.Frame(add_window, bg="#000033", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields with retro styling
        tk.Label(frame, text="USERNAME:", bg="#000033", fg="#00ccff", font=self.text_font).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        username_var = tk.StringVar()
        username_entry = tk.Entry(frame, textvariable=username_var, width=30, 
                                bg="#000000", fg="#00ffcc", insertbackground="#ff00ff",
                                relief="sunken", bd=2)
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        username_entry.focus_set()
        
        tk.Label(frame, text="PASSWORD:", bg="#000033", fg="#00ccff", font=self.text_font).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        password_var = tk.StringVar()
        password_entry = tk.Entry(frame, textvariable=password_var, width=30, show="*", 
                                bg="#000000", fg="#00ffcc", insertbackground="#ff00ff",
                                relief="sunken", bd=2)
        password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(frame, text="RESOURCE/WEBSITE:", bg="#000033", fg="#00ccff", font=self.text_font).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        resource_var = tk.StringVar()
        resource_entry = tk.Entry(frame, textvariable=resource_var, width=30, 
                                bg="#000000", fg="#00ffcc", insertbackground="#ff00ff",
                                relief="sunken", bd=2)
        resource_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(frame, text="CATEGORY:", bg="#000033", fg="#00ccff", font=self.text_font).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        category_var = tk.StringVar()
        
        # Make a retro dropdown menu (old Windows style)
        category_options = ['Personal', 'Work', 'Finance', 'Social', 'Shopping', 'Other']
        category_menu = tk.OptionMenu(frame, category_var, *category_options)
        category_menu.config(bg="#303030", fg="#00ffcc", activebackground="#505050", 
                           activeforeground="#ff00ff", font=self.text_font, width=25)
        category_menu["menu"].config(bg="#000000", fg="#00ffcc", activebackground="#505050", 
                                   activeforeground="#ff00ff", font=self.text_font)
        category_menu.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Add buttons with retro styling
        def save_and_close():
            username = username_var.get().strip()
            password = password_var.get()
            resource = resource_var.get().strip()
            category = category_var.get().strip()
            
            if not username:
                messagebox.showerror("ERROR", "Username cannot be empty")
                return
            
            if not resource:
                messagebox.showerror("ERROR", "Resource/Website cannot be empty")
                return
            
            # Call core function to add credential
            result = pm.add_credential(username, password, resource, category)
            
            if result:
                messagebox.showinfo("SUCCESS", "Credential added successfully")
                add_window.destroy()
                
                # Update status with retro vibe
                self.status_var.set("NEW CREDENTIAL ADDED SUCCESSFULLY")
            else:
                messagebox.showerror("ERROR", "Failed to save credential")
        
        button_frame = tk.Frame(frame, bg="#000033")
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        save_button = tk.Button(button_frame, text="SAVE", command=save_and_close,
                              relief="raised", borderwidth=2, width=10,
                              bg="#303030", fg="#00ffff",
                              activebackground="#505050", activeforeground="#ff00ff",
                              font=self.button_font)
        save_button.pack(side=tk.LEFT, padx=10)
        
        cancel_button = tk.Button(button_frame, text="CANCEL", command=add_window.destroy,
                                relief="raised", borderwidth=2, width=10,
                                bg="#303030", fg="#00ffff",
                                activebackground="#505050", activeforeground="#ff00ff",
                                font=self.button_font)
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def view_credentials(self):
        """Display all credentials in the text area"""
        categories = pm.get_credentials_by_category()
        
        if not categories:
            self.update_display_text("[ NO CREDENTIALS STORED YET ]")
            return
        
        # Format the display text
        display_text = ""
        total_count = 0
        
        for category, creds in categories.items():
            display_text += f"\n== {category.upper()} ==\n"
            display_text += "═" * (len(category) + 6) + "\n\n"
            total_count += len(creds)
            
            for i, cred in enumerate(creds, 1):
                display_text += f"#{i} Resource: {cred['resource']}\n"
                display_text += f"   Username: {cred['username']}\n"
                display_text += f"   Password: {cred['password']}\n"
                display_text += f"   Added on: {cred.get('date_added', 'Unknown')}\n"
                display_text += f"   --------------------------------\n\n"
        
        self.update_display_text(display_text)
        self.status_var.set(f"DISPLAYING {total_count} CREDENTIALS...")
    
    def search_credentials(self):
        """Search for credentials based on user input"""
        search_window = self.create_retro_toplevel("SEARCH DATABASE", "400x150")
        
        frame = tk.Frame(search_window, bg="#000033", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="SEARCH TERM:", bg="#000033", fg="#00ccff", font=self.text_font).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        search_var = tk.StringVar()
        search_entry = tk.Entry(frame, textvariable=search_var, width=30, 
                              bg="#000000", fg="#00ffcc", insertbackground="#ff00ff",
                              relief="sunken", bd=2)
        search_entry.grid(row=0, column=1, padx=10, pady=10)
        search_entry.focus_set()
        
        def execute_search():
            search_term = search_var.get().strip()
            if not search_term:
                messagebox.showwarning("WARNING", "Search term cannot be empty")
                return
            
            # Call core function to search
            matches = pm.search_credentials(search_term)
            
            # Display results
            if matches:
                display_text = f"[ FOUND {len(matches)} MATCHING CREDENTIALS ]\n\n"
                
                for i, cred in enumerate(matches, 1):
                    display_text += f"#{i} Resource: {cred['resource']}\n"
                    display_text += f"   Username: {cred['username']}\n"
                    display_text += f"   Password: {cred['password']}\n"
                    display_text += f"   Category: {cred.get('category', 'Uncategorized')}\n"
                    display_text += f"   --------------------------------\n\n"
                
                self.update_display_text(display_text)
                self.status_var.set(f"FOUND {len(matches)} MATCHING CREDENTIALS")
            else:
                self.update_display_text("[ NO MATCHING CREDENTIALS FOUND ]")
                self.status_var.set("SEARCH COMPLETE - NO MATCHES FOUND")
            
            search_window.destroy()
        
        button_frame = tk.Frame(frame, bg="#000033")
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        search_button = tk.Button(button_frame, text="SEARCH", command=execute_search,
                                relief="raised", borderwidth=2, width=10,
                                bg="#303030", fg="#00ffff",
                                activebackground="#505050", activeforeground="#ff00ff",
                                font=self.button_font)
        search_button.pack(side=tk.LEFT, padx=10)
        
        cancel_button = tk.Button(button_frame, text="CANCEL", command=search_window.destroy,
                                relief="raised", borderwidth=2, width=10,
                                bg="#303030", fg="#00ffff",
                                activebackground="#505050", activeforeground="#ff00ff",
                                font=self.button_font)
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def delete_credential(self):
        """Delete a credential selected by the user"""
        credentials_list = pm.load_credentials()
        
        if not credentials_list:
            messagebox.showinfo("INFO", "No credentials stored yet.")
            return
        
        # Create a retro-styled dialog to select which credential to delete
        delete_window = self.create_retro_toplevel("DELETE CREDENTIAL", "500x350")
        
        frame = tk.Frame(delete_window, bg="#000033", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="SELECT A CREDENTIAL TO DELETE:", 
               bg="#000033", fg="#00ccff", font=self.text_font).pack(pady=10)
        
        listbox_frame = tk.Frame(frame, bg="#000033")
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Retro-styled listbox
        listbox = tk.Listbox(listbox_frame, width=60, height=10,
                           bg="#000000", fg="#00ffcc",
                           selectbackground="#ff00ff", selectforeground="#ffffff",
                           font=("Consolas", 10),
                           relief="sunken", bd=2)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate the listbox with old-school formatting
        for i, cred in enumerate(credentials_list):
            listbox.insert(tk.END, f"{i+1}. {cred['resource']} - {cred['username']}")
        
        # Button actions with warning dialog
        def delete_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("WARNING", "Please select a credential to delete")
                return
            
            index = selection[0]
            
            # Show warning dialog with yes/no buttons (Windows 95 style)
            confirm = messagebox.askquestion("CONFIRM DELETION", 
                                         "Are you sure you want to delete this credential?\nThis action cannot be undone!",
                                         icon='warning')
            
            if confirm == 'yes':
                deleted_cred = pm.delete_credential(index)
                
                if deleted_cred:
                    messagebox.showinfo("SUCCESS", f"Credential for {deleted_cred['resource']} has been DELETED")
                    delete_window.destroy()
                    
                    # Update display
                    self.view_credentials()
                    self.status_var.set("CREDENTIAL DELETED SUCCESSFULLY")
        
        button_frame = tk.Frame(frame, bg="#000033")
        button_frame.pack(pady=10)
        
        delete_button = tk.Button(button_frame, text="DELETE", command=delete_selected,
                                relief="raised", borderwidth=2, width=10,
                                bg="#FF0000", fg="#FFFFFF",  # RED for delete button
                                activebackground="#AA0000", activeforeground="#FFFFFF",
                                font=self.button_font)
        delete_button.pack(side=tk.LEFT, padx=10)
        
        cancel_button = tk.Button(button_frame, text="CANCEL", command=delete_window.destroy,
                                relief="raised", borderwidth=2, width=10,
                                bg="#303030", fg="#00ffff",
                                activebackground="#505050", activeforeground="#ff00ff",
                                font=self.button_font)
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def on_closing(self):
        """Clean up resources when the application is closing"""
        # Stop the Earth animation
        self.running = False
        
        # Destroy the root window
        self.root.destroy()

# Main application entry point
def main():
    root = tk.Tk()
    app = RetrowavePasswordManagerGUI(root)
    
    # Set up the close handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()