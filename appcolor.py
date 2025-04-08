import cv2
import numpy as np
import tkinter as tk
from tkinter import Scale, Label, Button, Frame, StringVar, OptionMenu, IntVar, Checkbutton, ttk, colorchooser, messagebox
from PIL import Image, ImageTk
import time # For FPS calculation
import traceback # For detailed error printing

class ColorFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Filtro de Cores Avançado com OpenCV (Estilo Simples)")
        # Start maximized for better viewing
        try:
            self.root.state('zoomed') # Windows
        except tk.TclError:
            try:
                self.root.attributes('-zoomed', True) # Linux (some WMs)
            except tk.TclError:
                self.root.geometry("1280x720") # Fallback

        self.root.protocol("WM_DELETE_WINDOW", self.quit) # Handle window close button

        # --- Camera Initialization (Simplified like the example) ---
        self.camera_index = 0 # Keep track, but initialize directly
        # Try with CAP_DSHOW first, fallback if needed
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
             print(f"Aviso: Falha ao abrir câmera {self.camera_index} com CAP_DSHOW, tentando sem...")
             self.cap = cv2.VideoCapture(self.camera_index) # Fallback
             if not self.cap.isOpened():
                  messagebox.showerror("Erro de Câmera", f"Não foi possível abrir a câmera com índice {self.camera_index}.")
                  self.root.destroy()
                  return

        print(f"Câmera {self.camera_index} iniciada.")
        # Get initial actual resolution for display sizing reference if needed
        # actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        # actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # print(f"Resolução da câmera: {int(actual_width)}x{int(actual_height)}")


        # --- Tkinter Variables ---
        # Basic HSV / Color Space Ranges
        self.ch1_min_var = tk.IntVar(value=0)
        self.ch1_max_var = tk.IntVar(value=179) # Default HSV Hue max
        self.ch2_min_var = tk.IntVar(value=50) # Default decent Saturation min
        self.ch2_max_var = tk.IntVar(value=255)
        self.ch3_min_var = tk.IntVar(value=50) # Default decent Value min
        self.ch3_max_var = tk.IntVar(value=255)

        # Advanced Options
        self.erosion_size = IntVar(value=1)
        self.dilation_size = IntVar(value=2)
        self.blur_size = IntVar(value=3)  # Start with a small blur
        self.min_contour_area = IntVar(value=500) # Adjusted default
        self.show_contours = IntVar(value=1)
        self.show_bounding_boxes = IntVar(value=1) # Default on is often useful
        self.show_object_center = IntVar(value=1) # Default on
        self.color_space = StringVar(value="HSV") # Still useful for processing logic
        # self.camera_resolution = StringVar(value="640x480") # Removed resolution control for simplicity
        self.multi_color_mode = IntVar(value=0)

        # Multi-Color Management
        self.color_presets = []
        self.current_color_name = StringVar(value="Cor Atual")
        self.preset_name_var = StringVar(value="Minha Cor")

        # Performance / Display
        # Use a fixed size or calculate based on a desired width
        self.display_width = 480
        # We will calculate height based on aspect ratio in update
        self.fps = 0
        self.last_update_time = time.time()
        self.frame_count = 0

        # Attributes to store PhotoImage references (crucial!)
        self.original_tk = None
        self.mask_tk = None
        self.result_tk = None

        # --- GUI Setup ---
        self.setup_gui() # This method remains largely the same

        # --- Start Update Loop ---
        self.update()


    def setup_gui(self):
        """Sets up the Tkinter interface."""
        # Main frame
        main_frame = Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Control Frame (Right)
        control_panel = Frame(main_frame, width=400) # Fixed width for controls
        control_panel.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        control_panel.pack_propagate(False) # Prevent control panel from resizing

        control_notebook = ttk.Notebook(control_panel)
        control_notebook.pack(fill=tk.BOTH, expand=True)

        basic_tab = Frame(control_notebook)
        advanced_tab = Frame(control_notebook)
        multi_color_tab = Frame(control_notebook)

        control_notebook.add(basic_tab, text=" Cor Única ")
        control_notebook.add(advanced_tab, text=" Avançado ")
        control_notebook.add(multi_color_tab, text=" Multi-Cor ")

        # Image Frame (Left)
        image_frame = Frame(main_frame)
        image_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)

        Label(image_frame, text="Original").grid(row=0, column=0, pady=(0,5))
        self.original_label = Label(image_frame, borderwidth=1, relief="sunken")
        self.original_label.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        Label(image_frame, text="Máscara").grid(row=0, column=1, pady=(0,5))
        self.mask_label = Label(image_frame, borderwidth=1, relief="sunken")
        self.mask_label.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        Label(image_frame, text="Resultado Filtrado").grid(row=2, column=0, columnspan=2, pady=(10,5))
        self.result_label = Label(image_frame, borderwidth=1, relief="sunken")
        self.result_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Configure image frame resizing behavior
        image_frame.grid_rowconfigure(1, weight=1)
        image_frame.grid_rowconfigure(3, weight=1)
        image_frame.grid_columnconfigure(0, weight=1)
        image_frame.grid_columnconfigure(1, weight=1)


        # Status bar (Bottom)
        status_frame = Frame(self.root, bd=1, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = Label(status_frame, text="Pronto", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
        self.fps_label = Label(status_frame, text="FPS: 0", anchor=tk.E)
        self.fps_label.pack(side=tk.RIGHT, padx=5)

        # --- Populate Basic Tab ---
        Label(basic_tab, text="Ajuste os Valores:", font=("Arial", 11, "bold")).pack(pady=(10, 5), anchor=tk.W)

        # Use labels that change with color space
        self.ch1_label_var = StringVar(value="H - Matiz")
        self.ch2_label_var = StringVar(value="S - Saturação")
        self.ch3_label_var = StringVar(value="V - Valor")

        # Pass the correct range for H slider (0-179)
        self.create_slider_set(basic_tab, self.ch1_label_var, 0, 179, self.ch1_min_var, self.ch1_max_var)
        self.create_slider_set(basic_tab, self.ch2_label_var, 0, 255, self.ch2_min_var, self.ch2_max_var)
        self.create_slider_set(basic_tab, self.ch3_label_var, 0, 255, self.ch3_min_var, self.ch3_max_var)

        # Color Picker and Presets
        Label(basic_tab, text="Seleção Rápida:", font=("Arial", 11, "bold")).pack(pady=(15, 5), anchor=tk.W)
        picker_frame = Frame(basic_tab)
        picker_frame.pack(pady=5, fill=tk.X)
        Button(picker_frame, text="Selecionar Cor", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        Label(picker_frame, textvariable=self.current_color_name, fg="blue").pack(side=tk.LEFT, padx=5)

        Label(basic_tab, text="Cores pré-definidas:").pack(pady=(10,2), anchor=tk.W)
        self.create_preset_buttons(basic_tab) # This helper should still work

        # Save Current Color
        Label(basic_tab, text="Salvar Cor Atual:", font=("Arial", 11, "bold")).pack(pady=(15, 5), anchor=tk.W)
        save_frame = Frame(basic_tab)
        save_frame.pack(pady=5, fill=tk.X)
        ttk.Entry(save_frame, textvariable=self.preset_name_var, width=20).pack(side=tk.LEFT, padx=(5,2))
        Button(save_frame, text="Salvar", command=self.save_current_color).pack(side=tk.LEFT, padx=2)
        Button(save_frame, text="Adicionar a Multi", command=self.add_current_color_to_multi).pack(side=tk.LEFT, padx=2)

        # Exit Button
        Button(basic_tab, text="Sair", command=self.quit, bg="#FF5733", fg="white", width=10).pack(pady=(20, 10))


        # --- Populate Advanced Tab ---
        Label(advanced_tab, text="Opções de Processamento:", font=("Arial", 11, "bold")).pack(pady=(10, 5), anchor=tk.W)

        # Color Space
        space_frame = Frame(advanced_tab)
        space_frame.pack(pady=5, fill=tk.X, padx=5)
        Label(space_frame, text="Espaço de Cor:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        color_spaces = ["HSV", "BGR", "RGB", "Lab", "YCrCb"] # Added BGR
        OptionMenu(space_frame, self.color_space, *color_spaces, command=self.change_color_space).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Morphology
        morph_frame = Frame(advanced_tab)
        morph_frame.pack(pady=5, fill=tk.X, padx=5)
        Label(morph_frame, text="Erosão:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        Scale(morph_frame, from_=0, to=15, orient=tk.HORIZONTAL, variable=self.erosion_size, length=150).pack(side=tk.LEFT, fill=tk.X, expand=True)

        morph_frame2 = Frame(advanced_tab)
        morph_frame2.pack(pady=5, fill=tk.X, padx=5)
        Label(morph_frame2, text="Dilatação:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        Scale(morph_frame2, from_=0, to=15, orient=tk.HORIZONTAL, variable=self.dilation_size, length=150).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Blur
        blur_frame = Frame(advanced_tab)
        blur_frame.pack(pady=5, fill=tk.X, padx=5)
        Label(blur_frame, text="Suavização:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        Scale(blur_frame, from_=0, to=25, orient=tk.HORIZONTAL, variable=self.blur_size, length=150).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Contour Area
        contour_frame = Frame(advanced_tab)
        contour_frame.pack(pady=5, fill=tk.X, padx=5)
        Label(contour_frame, text="Área Mínima:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        Scale(contour_frame, from_=10, to=10000, orient=tk.HORIZONTAL, variable=self.min_contour_area, length=150).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Visualization Options
        Label(advanced_tab, text="Opções de Visualização:", font=("Arial", 11, "bold")).pack(pady=(15, 5), anchor=tk.W)
        viz_frame = Frame(advanced_tab, padx=5)
        viz_frame.pack(pady=5, fill=tk.X)
        Checkbutton(viz_frame, text="Mostrar Contornos", variable=self.show_contours).pack(anchor=tk.W)
        Checkbutton(viz_frame, text="Mostrar Caixas Delimitadoras", variable=self.show_bounding_boxes).pack(anchor=tk.W)
        Checkbutton(viz_frame, text="Mostrar Centro dos Objetos", variable=self.show_object_center).pack(anchor=tk.W)

        # Camera Options - Removed for simplicity based on the example
        # Label(advanced_tab, text="Opções da Câmera:", font=("Arial", 11, "bold")).pack(pady=(15, 5), anchor=tk.W)
        # cam_frame = Frame(advanced_tab, padx=5)
        # cam_frame.pack(pady=5, fill=tk.X)
        # # Resolution dropdown removed
        # # Toggle camera button removed


        # --- Populate Multi-Color Tab ---
        Label(multi_color_tab, text="Detecção de Múltiplas Cores", font=("Arial", 11, "bold")).pack(pady=10, anchor=tk.W)

        Checkbutton(multi_color_tab, text="Ativar Modo Multi-Cor", variable=self.multi_color_mode,
                    command=self.toggle_multi_color_mode).pack(anchor=tk.W, pady=5)

        Label(multi_color_tab, text="Cores Salvas:").pack(anchor=tk.W, pady=(10,2))

        # Frame for the list with scrollbar
        list_container = Frame(multi_color_tab)
        list_container.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.color_list_canvas = tk.Canvas(list_container, yscrollcommand=scrollbar.set, borderwidth=0, highlightthickness=0)
        self.color_list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.color_list_canvas.yview)

        # This frame goes INSIDE the canvas
        self.color_list_frame = Frame(self.color_list_canvas)
        self.color_list_canvas.create_window((0,0), window=self.color_list_frame, anchor="nw")

        # Update scrollregion when list frame size changes
        self.color_list_frame.bind("<Configure>", lambda e: self.color_list_canvas.configure(scrollregion=self.color_list_canvas.bbox("all")))

        # Buttons for managing colors
        color_manage_frame = Frame(multi_color_tab)
        color_manage_frame.pack(fill=tk.X, pady=10)
        Button(color_manage_frame, text="Adicionar Cor Atual", command=self.add_current_color_to_multi).pack(side=tk.LEFT, padx=5)
        Button(color_manage_frame, text="Limpar Todas", command=self.clear_all_colors).pack(side=tk.LEFT, padx=5)

        # Initialize list
        self.update_color_list()
        self.change_color_space() # Set initial labels/ranges correctly

    # --- Helper methods like create_slider_set, create_preset_buttons remain the same ---
    def create_slider_set(self, parent, label_var, min_val, max_val, min_tk_var, max_tk_var):
        """Helper to create a labeled Min/Max slider pair."""
        frame = Frame(parent, pady=2)
        frame.pack(fill=tk.X, padx=5)

        Label(frame, textvariable=label_var, width=12, anchor=tk.W).pack(side=tk.LEFT)

        sub_frame = Frame(frame)
        sub_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Find the Scale widgets associated with the IntVars to configure range
        scale_min = Scale(sub_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=min_tk_var, length=100, showvalue=True)
        scale_min.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        scale_max = Scale(sub_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=max_tk_var, length=100, showvalue=True)
        scale_max.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Store references if needed for dynamic range update (though simplified now)
        # if label_var == self.ch1_label_var: # Example
        #     self.ch1_scale_min = scale_min
        #     self.ch1_scale_max = scale_max
        # etc.

        # Labels for Min/Max under sliders
        label_frame = Frame(frame)
        label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True) # Place it under the sub_frame in layout
        Label(label_frame, text="Min", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=(14, 5), fill=tk.X, expand=True)
        Label(label_frame, text="Max", width=10, anchor=tk.E).pack(side=tk.LEFT, fill=tk.X, expand=True)


    def create_preset_buttons(self, parent):
        """Helper to create preset color buttons in rows."""
        button_colors = [
            ("Vermelho", "red", "white"), ("Verde", "green", "white"), ("Azul", "blue", "white"),
            ("Amarelo", "yellow", "black"),("Laranja", "orange", "black"), ("Ciano", "cyan", "black"),
            ("Roxo", "purple", "white"), ("Rosa", "pink", "black"), ("Marrom", "brown", "white"),
            ("Preto", "black", "white"), ("Cinza", "gray", "white"), ("Branco", "white", "black")
        ]
        max_per_row = 3
        button_frame = Frame(parent)
        button_frame.pack(pady=5, fill=tk.X, padx=5)

        current_row = Frame(button_frame)
        current_row.pack(fill=tk.X)
        for i, (name, bg, fg) in enumerate(button_colors):
            if i > 0 and i % max_per_row == 0:
                 current_row = Frame(button_frame)
                 current_row.pack(fill=tk.X, pady=(2,0))

            preset_name = name.lower().replace("ê", "e").replace("á", "a").replace("ã", "a").replace("ç","c") # Normalize name
            # Use lambda with default argument to capture current preset_name
            btn = Button(current_row, text=name, bg=bg, fg=fg, width=10,
                         command=lambda p=preset_name: self.set_preset(p))
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

    # --- Color Management Methods (get_color_presets, set_preset, choose_color, save_current_color, etc.) ---
    # --- These remain largely the same as in your advanced version                  ---
    # --- Make sure set_preset checks/sets color_space to HSV                       ---
    # --- Make sure choose_color uses the current color_space                       ---
    # --- Make sure save_current_color saves the current color_space                ---
    # --- Make sure load_color sets the correct color_space before loading values   ---

    def get_color_presets(self):
        """Defines HSV presets. Can be extended for other spaces."""
        presets = {
            "vermelho": {"h_min": 0, "h_max": 10, "s_min": 100, "s_max": 255, "v_min": 70, "v_max": 255},
            "vermelho_wrap": {"h_min": 170, "h_max": 179, "s_min": 100, "s_max": 255, "v_min": 70, "v_max": 255},
            "verde": {"h_min": 40, "h_max": 85, "s_min": 50, "s_max": 255, "v_min": 50, "v_max": 255},
            "azul": {"h_min": 95, "h_max": 130, "s_min": 80, "s_max": 255, "v_min": 50, "v_max": 255},
            "amarelo": {"h_min": 20, "h_max": 35, "s_min": 100, "s_max": 255, "v_min": 100, "v_max": 255},
            "laranja": {"h_min": 10, "h_max": 25, "s_min": 120, "s_max": 255, "v_min": 120, "v_max": 255},
            "ciano": {"h_min": 85, "h_max": 100, "s_min": 100, "s_max": 255, "v_min": 100, "v_max": 255},
            "roxo": {"h_min": 130, "h_max": 160, "s_min": 80, "s_max": 255, "v_min": 50, "v_max": 255},
            "rosa": {"h_min": 160, "h_max": 175, "s_min": 80, "s_max": 255, "v_min": 100, "v_max": 255},
            "marrom": {"h_min": 10, "h_max": 25, "s_min": 80, "s_max": 255, "v_min": 20, "v_max": 120},
            "preto": {"h_min": 0, "h_max": 179, "s_min": 0, "s_max": 255, "v_min": 0, "v_max": 40},
            "cinza": {"h_min": 0, "h_max": 179, "s_min": 0, "s_max": 50, "v_min": 40, "v_max": 180},
            "branco": {"h_min": 0, "h_max": 179, "s_min": 0, "s_max": 30, "v_min": 200, "v_max": 255},
        }
        name_map = {
            "Vermelho": "vermelho", "Verde": "verde", "Azul": "azul", "Amarelo": "amarelo",
            "Laranja": "laranja", "Ciano": "ciano", "Roxo": "roxo", "Rosa": "rosa",
            "Marrom": "marrom", "Preto": "preto", "Cinza": "cinza", "Branco": "branco"
        }
        return presets, name_map

    def set_preset(self, color_key):
        """Sets sliders based on a preset color key."""
        if self.color_space.get() != "HSV":
            self.color_space.set("HSV")
            self.change_color_space()

        presets, name_map = self.get_color_presets()
        preset = presets.get(color_key)

        if preset:
            self.ch1_min_var.set(preset["h_min"])
            self.ch1_max_var.set(preset["h_max"])
            self.ch2_min_var.set(preset["s_min"])
            self.ch2_max_var.set(preset["s_max"])
            self.ch3_min_var.set(preset["v_min"])
            self.ch3_max_var.set(preset["v_max"])

            display_name = next((name for name, key in name_map.items() if key == color_key), "Preset")
            self.current_color_name.set(display_name)
            self.update_status(f"Preset '{display_name}' aplicado.")
            # Handle red wrap for multi-color mode
            if color_key == "vermelho" and self.multi_color_mode.get():
                 red_wrap_preset = presets.get("vermelho_wrap")
                 if red_wrap_preset:
                     wrap_color = {**red_wrap_preset, "name": "Vermelho (Wrap)", "space": "HSV"}
                     if not any(c['name'] == wrap_color['name'] for c in self.color_presets):
                         self.color_presets.append(wrap_color)
                         self.update_color_list()
                         self.update_status(f"Preset '{display_name}' aplicado. Adicionado range extra para vermelho.")
        else:
            self.update_status(f"Preset '{color_key}' não encontrado.")

    def choose_color(self):
        """Opens a color picker and sets sliders (attempts conversion)."""
        result = colorchooser.askcolor(title="Escolha uma cor")
        if result and result[1]:
            rgb_color = result[0]
            if rgb_color:
                r, g, b = int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2])
                pixel_bgr = np.uint8([[[b, g, r]]])
                try:
                    space = self.color_space.get()
                    # ... [Rest of the conversion logic from previous advanced version] ...
                    if space == "HSV":
                        converted_pixel = cv2.cvtColor(pixel_bgr, cv2.COLOR_BGR2HSV)
                        ch1, ch2, ch3 = converted_pixel[0][0]
                        h_tol, s_tol, v_tol = 10, 50, 50
                        self.ch1_min_var.set(max(0, ch1 - h_tol))
                        self.ch1_max_var.set(min(179, ch1 + h_tol))
                        # ... set s and v ...
                        self.ch2_min_var.set(max(0, ch2 - s_tol))
                        self.ch2_max_var.set(min(255, ch2 + s_tol))
                        self.ch3_min_var.set(max(0, ch3 - v_tol))
                        self.ch3_max_var.set(min(255, ch3 + v_tol))
                    elif space == "BGR":
                        b_ch, g_ch, r_ch = pixel_bgr[0][0] # Corrected variable names
                        tol = 25
                        self.ch1_min_var.set(max(0, b_ch - tol)) # B
                        self.ch1_max_var.set(min(255, b_ch + tol))
                        self.ch2_min_var.set(max(0, g_ch - tol)) # G
                        self.ch2_max_var.set(min(255, g_ch + tol))
                        self.ch3_min_var.set(max(0, r_ch - tol)) # R
                        self.ch3_max_var.set(min(255, r_ch + tol))
                    elif space == "RGB":
                        r_ch, g_ch, b_ch = pixel_bgr[0][0, ::-1] # Corrected variable names
                        tol = 25
                        self.ch1_min_var.set(max(0, r_ch - tol)) # R
                        self.ch1_max_var.set(min(255, r_ch + tol))
                        self.ch2_min_var.set(max(0, g_ch - tol)) # G
                        self.ch2_max_var.set(min(255, g_ch + tol))
                        self.ch3_min_var.set(max(0, b_ch - tol)) # B
                        self.ch3_max_var.set(min(255, b_ch + tol))
                    elif space == "Lab":
                        converted_pixel = cv2.cvtColor(pixel_bgr, cv2.COLOR_BGR2Lab)
                        l, a, b_lab = converted_pixel[0][0]
                        l_tol, a_tol, b_tol = 10, 20, 20
                        self.ch1_min_var.set(max(0, l - l_tol))
                        self.ch1_max_var.set(min(255, l + l_tol))
                        # ... set a and b ...
                        self.ch2_min_var.set(max(0, a - a_tol))
                        self.ch2_max_var.set(min(255, a + a_tol))
                        self.ch3_min_var.set(max(0, b_lab - b_tol))
                        self.ch3_max_var.set(min(255, b_lab + b_tol))
                    elif space == "YCrCb":
                        converted_pixel = cv2.cvtColor(pixel_bgr, cv2.COLOR_BGR2YCrCb)
                        y, cr, cb = converted_pixel[0][0]
                        y_tol, cr_tol, cb_tol = 20, 20, 20
                        self.ch1_min_var.set(max(0, y - y_tol))
                        self.ch1_max_var.set(min(255, y + y_tol))
                         # ... set Cr and Cb ...
                        self.ch2_min_var.set(max(0, cr - cr_tol))
                        self.ch2_max_var.set(min(255, cr + cr_tol))
                        self.ch3_min_var.set(max(0, cb - cb_tol))
                        self.ch3_max_var.set(min(255, cb + cb_tol))

                    self.current_color_name.set("Cor Escolhida")
                    self.update_status(f"Cor RGB({r},{g},{b}) definida para espaço {space}.")
                except Exception as e:
                     self.update_status(f"Erro ao converter cor: {e}")

    def save_current_color(self):
        """Saves the current slider settings for the multi-color list."""
        name = self.preset_name_var.get().strip() or f"Cor {len(self.color_presets) + 1}"

        if any(c['name'] == name for c in self.color_presets):
            if messagebox.askyesno("Sobrescrever Cor?", f"Já existe '{name}'. Sobrescrever?"):
                 self.color_presets = [c for c in self.color_presets if c['name'] != name]
            else:
                return

        current_color = {
            "name": name, "space": self.color_space.get(),
            "ch1_min": self.ch1_min_var.get(), "ch1_max": self.ch1_max_var.get(),
            "ch2_min": self.ch2_min_var.get(), "ch2_max": self.ch2_max_var.get(),
            "ch3_min": self.ch3_min_var.get(), "ch3_max": self.ch3_max_var.get()
        }
        self.color_presets.append(current_color)
        self.update_color_list()
        self.update_status(f"Cor '{name}' salva para modo Multi-Cor.")
        if not self.multi_color_mode.get():
            self.update_status(f"Cor '{name}' salva. Ative 'Modo Multi-Cor' para usá-la.")

    def add_current_color_to_multi(self):
        self.save_current_color()

    def clear_all_colors(self):
        if messagebox.askyesno("Limpar Tudo?", "Remover todas as cores salvas?"):
            self.color_presets = []
            self.update_color_list()
            self.update_status("Lista Multi-Cor limpa.")

    def update_color_list(self):
        """Updates the visual list of saved colors."""
        for widget in self.color_list_frame.winfo_children():
            widget.destroy()
        if not self.color_presets:
             Label(self.color_list_frame, text="Nenhuma cor salva.").pack(padx=10, pady=10)
        else:
             for i, color_data in enumerate(self.color_presets):
                # ... [Rest of the list update logic from previous advanced version] ...
                color_frame = Frame(self.color_list_frame, borderwidth=1, relief="groove")
                color_frame.pack(fill=tk.X, pady=2, padx=2)
                swatch_canvas = tk.Canvas(color_frame, width=25, height=25, bg="white", highlightthickness=0)
                swatch_canvas.pack(side=tk.LEFT, padx=5, pady=5)
                hex_color = self.get_approx_hex_color(color_data)
                swatch_canvas.create_rectangle(2, 2, 23, 23, fill=hex_color, outline="black", width=1)
                info_frame = Frame(color_frame)
                info_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                Label(info_frame, text=f"{color_data['name']} ({color_data['space']})", anchor=tk.W, font=("Arial", 9, "bold")).pack(fill=tk.X)
                details = (f"Ch1:{color_data['ch1_min']}-{color_data['ch1_max']}, "
                           f"Ch2:{color_data['ch2_min']}-{color_data['ch2_max']}, "
                           f"Ch3:{color_data['ch3_min']}-{color_data['ch3_max']}")
                Label(info_frame, text=details, anchor=tk.W, font=("Arial", 8)).pack(fill=tk.X)
                button_frame = Frame(color_frame)
                button_frame.pack(side=tk.RIGHT, padx=5)
                Button(button_frame, text="Usar", width=5, command=lambda c=color_data: self.load_color(c)).pack(side=tk.TOP, pady=1)
                Button(button_frame, text="X", width=3, fg="red", command=lambda idx=i: self.remove_color(idx)).pack(side=tk.TOP, pady=1)

        self.color_list_canvas.update_idletasks()
        self.color_list_canvas.config(scrollregion=self.color_list_canvas.bbox("all"))

    def get_approx_hex_color(self, color_data):
         # ... [Logic from previous advanced version] ...
        try:
            ch1 = (color_data['ch1_min'] + color_data['ch1_max']) // 2
            ch2 = (color_data['ch2_min'] + color_data['ch2_max']) // 2
            ch3 = (color_data['ch3_min'] + color_data['ch3_max']) // 2
            space = color_data['space']
            pixel = np.uint8([[[ch1, ch2, ch3]]])
            bgr = None
            if space == "HSV":
                ch2 = max(100, ch2); ch3 = max(100, ch3)
                pixel = np.uint8([[[ch1, ch2, ch3]]])
                bgr = cv2.cvtColor(pixel, cv2.COLOR_HSV2BGR)
            elif space == "BGR": bgr = pixel
            elif space == "RGB": r, g, b = ch1, ch2, ch3; bgr = np.uint8([[[b, g, r]]])
            elif space == "Lab":
                 pixel[0,0,0]=np.clip(pixel[0,0,0],0,255); pixel[0,0,1]=np.clip(pixel[0,0,1],0,255); pixel[0,0,2]=np.clip(pixel[0,0,2],0,255)
                 bgr = cv2.cvtColor(pixel, cv2.COLOR_Lab2BGR)
            elif space == "YCrCb": bgr = cv2.cvtColor(pixel, cv2.COLOR_YCrCb2BGR)
            else: return "#808080"
            if bgr is not None:
                b, g, r = bgr[0,0]; r, g, b = [np.clip(c, 0, 255) for c in (r, g, b)]
                return f'#{r:02x}{g:02x}{b:02x}'
        except Exception: pass
        return "#808080"

    def load_color(self, color_data):
        """Loads a saved color into the main controls."""
        target_space = color_data['space']
        if self.color_space.get() != target_space:
            self.color_space.set(target_space)
            self.change_color_space()
        self.ch1_min_var.set(color_data["ch1_min"]); self.ch1_max_var.set(color_data["ch1_max"])
        self.ch2_min_var.set(color_data["ch2_min"]); self.ch2_max_var.set(color_data["ch2_max"])
        self.ch3_min_var.set(color_data["ch3_min"]); self.ch3_max_var.set(color_data["ch3_max"])
        self.current_color_name.set(f"Carregado: {color_data['name']}")
        self.update_status(f"Cor '{color_data['name']}' ({target_space}) carregada.")
        if self.multi_color_mode.get():
            self.multi_color_mode.set(0)
            self.toggle_multi_color_mode()

    def remove_color(self, index):
        if 0 <= index < len(self.color_presets):
            name = self.color_presets[index]["name"]
            if messagebox.askyesno("Remover Cor?", f"Remover '{name}'?"):
                del self.color_presets[index]
                self.update_color_list()
                self.update_status(f"Cor '{name}' removida.")

    def toggle_multi_color_mode(self):
        if self.multi_color_mode.get():
            status = f"Modo Multi-Cor ativado ({len(self.color_presets)} cores)."
            if not self.color_presets: status = "Modo Multi-Cor ativado (sem cores salvas)."
            self.update_status(status)
        else:
            self.update_status("Modo Multi-Cor desativado.")

    # --- Camera and Processing Methods ---

    def change_color_space(self, *args):
        """Updates slider ranges and labels based on the selected color space."""
        space = self.color_space.get()
        self.update_status(f"Alterando espaço de cor para {space}")

        ranges = {
            "HSV":   [ (0, 179), (0, 255), (0, 255), ("H - Matiz", "S - Saturação", "V - Valor") ],
            "BGR":   [ (0, 255), (0, 255), (0, 255), ("B - Azul", "G - Verde", "R - Vermelho") ],
            "RGB":   [ (0, 255), (0, 255), (0, 255), ("R - Vermelho", "G - Verde", "B - Azul") ],
            "Lab":   [ (0, 255), (0, 255), (0, 255), ("L - Luminosidade", "a - Verde-Vermelho", "b - Azul-Amarelo") ],
            "YCrCb": [ (0, 255), (0, 255), (0, 255), ("Y - Luma", "Cr - Dif. Vermelho", "Cb - Dif. Azul") ]
        }

        if space in ranges:
            range1, range2, range3, labels = ranges[space]
            self.ch1_label_var.set(labels[0])
            self.ch2_label_var.set(labels[1])
            self.ch3_label_var.set(labels[2])

            # Reset values to defaults for the space
            # Ideally, reconfigure Scale widgets' 'from_'/'to_', but resetting values is simpler
            # Note: This requires finding the Scale widgets or storing references (see create_slider_set)
            # For now, just setting the variables:
            if space == "HSV":
                 self.ch1_min_var.set(0); self.ch1_max_var.set(179)
                 self.ch2_min_var.set(50); self.ch2_max_var.set(255)
                 self.ch3_min_var.set(50); self.ch3_max_var.set(255)
            # Add default value resets for other spaces if desired...
            elif space in ["BGR", "RGB", "YCrCb", "Lab"]:
                 self.ch1_min_var.set(0); self.ch1_max_var.set(255)
                 self.ch2_min_var.set(0); self.ch2_max_var.set(255)
                 self.ch3_min_var.set(0); self.ch3_max_var.set(255)

            self.current_color_name.set("Ajuste Manual")
        else:
            self.update_status(f"Espaço de cor desconhecido: {space}")

    # Resolution and toggle camera methods removed for simplicity

    def update(self):
        """Core loop: Reads frame, processes, and updates the display (Simple Example Style)."""
        if not self.cap or not self.cap.isOpened():
            self.update_status("Erro: Câmera indisponível.", error=True)
            self.root.after(1000, self.update) # Try again
            return

        ret, frame = self.cap.read()

        if not ret or frame is None:
            self.update_status("Erro ao ler frame.", error=True)
            self.root.after(100, self.update) # Try again soon
            return

        # --- Frame Processing (Keep advanced logic) ---
        try:
            process_start_time = time.time()
            result_frame_for_drawing = frame.copy() # Keep for drawing contours etc.

            # 1. Color Space Conversion
            space = self.color_space.get()
            try:
                if space == "HSV": converted_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                elif space == "RGB": converted_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                elif space == "Lab": converted_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
                elif space == "YCrCb": converted_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
                elif space == "BGR": converted_frame = frame
                else: converted_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV); space="HSV"
            except cv2.error as e:
                 self.update_status(f"Erro conversão cor: {e}", error=True)
                 converted_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV); space="HSV"

            # 2. Optional Blur
            blur_ksize = self.blur_size.get()
            processed_frame = converted_frame # Start with converted (or original if no blur)
            if blur_ksize > 0:
                if blur_ksize % 2 == 0: blur_ksize += 1
                processed_frame = cv2.GaussianBlur(converted_frame, (blur_ksize, blur_ksize), 0)

            # 3. Mask Generation (Handles single/multi and red wrap)
            final_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            # ... [ Mask generation logic remains the same as advanced version ] ...
            if self.multi_color_mode.get() and self.color_presets:
                # Multi-Color Mode
                for color_data in self.color_presets:
                    if color_data['space'] == space: # Only process if space matches
                        lower = np.array([color_data["ch1_min"], color_data["ch2_min"], color_data["ch3_min"]])
                        upper = np.array([color_data["ch1_max"], color_data["ch2_max"], color_data["ch3_max"]])
                        # Handle Red Wrap specifically for HSV
                        if space == "HSV" and lower[0] > upper[0]:
                             # 0 to Max Hue
                             lower1 = np.array([0, lower[1], lower[2]])
                             upper1 = np.array([upper[0], upper[1], upper[2]])
                             mask1 = cv2.inRange(processed_frame, lower1, upper1)
                             # Min Hue to 179
                             lower2 = np.array([lower[0], lower[1], lower[2]])
                             upper2 = np.array([179, upper[1], upper[2]])
                             mask2 = cv2.inRange(processed_frame, lower2, upper2)
                             mask = cv2.bitwise_or(mask1, mask2)
                        else:
                             mask = cv2.inRange(processed_frame, lower, upper)
                        final_mask = cv2.bitwise_or(final_mask, mask)
                    # Add logic here if you want multi-color to work across different spaces simultaneously (more complex)

            else:
                 # Single Color Mode
                lower = np.array([self.ch1_min_var.get(), self.ch2_min_var.get(), self.ch3_min_var.get()])
                upper = np.array([self.ch1_max_var.get(), self.ch2_max_var.get(), self.ch3_max_var.get()])
                if space == "HSV" and lower[0] > upper[0] : # Wrap-around case for Hue
                    lower1 = np.array([0, lower[1], lower[2]]); upper1 = np.array([upper[0], upper[1], upper[2]])
                    mask1 = cv2.inRange(processed_frame, lower1, upper1)
                    lower2 = np.array([lower[0], lower[1], lower[2]]); upper2 = np.array([179, upper[1], upper[2]])
                    mask2 = cv2.inRange(processed_frame, lower2, upper2)
                    final_mask = cv2.bitwise_or(mask1, mask2)
                else:
                    final_mask = cv2.inRange(processed_frame, lower, upper)

            # 4. Morphological Operations
            erode_ksize = self.erosion_size.get()
            dilate_ksize = self.dilation_size.get()
            if erode_ksize > 0:
                erode_kernel = np.ones((erode_ksize, erode_ksize), np.uint8)
                final_mask = cv2.erode(final_mask, erode_kernel, iterations=1)
            if dilate_ksize > 0:
                dilate_kernel = np.ones((dilate_ksize, dilate_ksize), np.uint8)
                final_mask = cv2.dilate(final_mask, dilate_kernel, iterations=1) # Usually 1 iteration is enough after erode

            # 5. Find and Filter Contours
            contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            min_area = self.min_contour_area.get()
            detected_objects = 0
            filtered_contours = []
            if contours:
                filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
                detected_objects = len(filtered_contours)

                # 6. Draw Visualizations on result_frame_for_drawing
                if filtered_contours:
                    if self.show_contours.get():
                        cv2.drawContours(result_frame_for_drawing, filtered_contours, -1, (0, 255, 0), 2)
                    for cnt in filtered_contours:
                        if self.show_bounding_boxes.get():
                            x, y, w, h = cv2.boundingRect(cnt)
                            cv2.rectangle(result_frame_for_drawing, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        if self.show_object_center.get():
                            M = cv2.moments(cnt)
                            if M["m00"] != 0:
                                cX = int(M["m10"] / M["m00"]); cY = int(M["m01"] / M["m00"])
                                cv2.circle(result_frame_for_drawing, (cX, cY), 5, (0, 0, 255), -1)
                                # cv2.putText(result_frame_for_drawing, f"({cX},{cY})", ...) # Optional text

            # 7. Apply Mask to Original Frame for Result View
            result_masked = cv2.bitwise_and(frame, frame, mask=final_mask)
            process_time = time.time() - process_start_time

            # --- Update GUI Images (Directly like simple example) ---
            # Decide which frame to show as "Original" (raw 'frame' or 'result_frame_for_drawing')
            original_display_frame = result_frame_for_drawing # Show frame with drawings

            # Convert colors for PIL/Tkinter
            original_img_rgb = cv2.cvtColor(original_display_frame, cv2.COLOR_BGR2RGB)
            mask_img_rgb = cv2.cvtColor(final_mask, cv2.COLOR_GRAY2RGB) # Mask needs RGB conversion for PIL
            result_img_rgb = cv2.cvtColor(result_masked, cv2.COLOR_BGR2RGB)

            # Calculate display size based on aspect ratio
            h, w = original_img_rgb.shape[:2]
            aspect_ratio = w / h
            display_height = int(self.display_width / aspect_ratio)
            display_size = (self.display_width, display_height)

            # Resize images
            original_img_resized = cv2.resize(original_img_rgb, display_size, interpolation=cv2.INTER_LINEAR)
            mask_img_resized = cv2.resize(mask_img_rgb, display_size, interpolation=cv2.INTER_LINEAR)
            result_img_resized = cv2.resize(result_img_rgb, display_size, interpolation=cv2.INTER_LINEAR)

            # Convert to PIL format
            original_pil = Image.fromarray(original_img_resized)
            mask_pil = Image.fromarray(mask_img_resized)
            result_pil = Image.fromarray(result_img_resized)

            # Convert to Tkinter format (Store in self attributes!)
            self.original_tk = ImageTk.PhotoImage(image=original_pil)
            self.mask_tk = ImageTk.PhotoImage(image=mask_pil)
            self.result_tk = ImageTk.PhotoImage(image=result_pil)

            # Update labels and keep references
            self.original_label.config(image=self.original_tk)
            self.original_label.image = self.original_tk
            self.mask_label.config(image=self.mask_tk)
            self.mask_label.image = self.mask_tk
            self.result_label.config(image=self.result_tk)
            self.result_label.image = self.result_tk


            # --- Update Status and FPS ---
            self.frame_count += 1
            now = time.time()
            elapsed = now - self.last_update_time
            if elapsed >= 1.0:
                self.fps = self.frame_count / elapsed
                self.fps_label.config(text=f"FPS: {self.fps:.1f}")
                self.last_update_time = now
                self.frame_count = 0

            status_msg = f"{detected_objects} objeto(s)."
            if self.multi_color_mode.get(): status_msg += f" (Multi: {len(self.color_presets)})"
            else: status_msg += f" ({self.current_color_name.get()})"
            self.update_status(status_msg)

        except Exception as e:
            self.update_status(f"Erro no processamento: {e}", error=True)
            print(f"Erro detalhado no loop update:")
            traceback.print_exc() # Print stack trace to console


        # --- Schedule Next Update ---
        delay = 15 # Aim for ~60 FPS loop
        self.root.after(delay, self.update)


    # update_image_label method is removed

    def update_status(self, message, error=False):
        """Updates the status bar text."""
        self.status_label.config(text=message, fg="red" if error else "black")


    def quit(self):
        """Releases camera and closes the application."""
        print("Encerrando aplicação...")
        if self.cap and self.cap.isOpened():
            print("Liberando câmera...")
            self.cap.release()
        print("Destruindo janela...")
        self.root.destroy()


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ColorFilterApp(root)
    # Ensure quit is called on window close even if __init__ failed partially
    root.protocol("WM_DELETE_WINDOW", app.quit)
    # Check if app initialization was successful before starting mainloop
    if hasattr(root, 'children') and root.children: # Basic check if GUI was built
         root.mainloop()
    else:
         print("Falha na inicialização da aplicação.")