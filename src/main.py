import customtkinter as ctk
import os

class BluetoothProgramApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Bluetooth BLE")
        self.geometry("1200x700")
        ctk.set_appearance_mode("light")
        
        # Colores
        self.BG_COLOR = "#F0F0F0"
        self.BEAM_COLOR = "#FFFFFF" 
        self.PANEL_COLOR = "#E0E0E0"
        
        self.configure(fg_color=self.BG_COLOR)
        
        # Variables
        self.sequence = []
        self.is_running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Configurar grid principal
        self.grid_rowconfigure(0, weight=0)   # Header
        self.grid_rowconfigure(1, weight=1)   # Contenido principal  
        self.grid_rowconfigure(2, weight=0)   # Paleta de bloques
        self.grid_columnconfigure(0, weight=3) # Área principal
        self.grid_columnconfigure(1, weight=1) # Panel lateral
        
        self.create_header()
        self.create_sequence_beam()
        self.create_control_panel()
        self.create_block_palette()
    
    def create_header(self):
        """Crea el header de la aplicación"""
        header_frame = ctk.CTkFrame(self, height=60, fg_color="#E0E0E0", corner_radius=0)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_frame.grid_propagate(False)
        
        # Título
        title_label = ctk.CTkLabel(header_frame, text="JPM", 
                                 font=("Arial", 20, "bold"), 
                                 text_color="#5A5A5A")
        title_label.pack(side="left", padx=20, pady=10)
        
        # Estado
        self.status_label = ctk.CTkLabel(header_frame, text="Modo Simulación", 
                                       font=("Arial", 12),
                                       text_color="#5A5A5A")
        self.status_label.pack(side="right", padx=20, pady=10)
    
    def create_sequence_beam(self):
        """Crea la viga de secuencia principal"""
        beam_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", 
                                border_width=2, border_color="#CCCCCC",
                                corner_radius=10)
        beam_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Título
        ctk.CTkLabel(beam_frame, text="Secuencia de Comandos",
                   font=("Arial", 16, "bold"),
                   text_color="#333333").pack(pady=10)
        
        # Área de la viga (scrollable horizontal)
        self.beam_area = ctk.CTkScrollableFrame(beam_frame, orientation="horizontal",
                                              fg_color="#F8F8F8", height=120)
        self.beam_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Indicador de inicio
        start_frame = ctk.CTkFrame(self.beam_area, width=60, height=80,
                                 fg_color="#6A9F37", corner_radius=8)
        start_frame.pack(side="left", padx=5, pady=10)
        ctk.CTkLabel(start_frame, text="▶", font=("Arial", 24, "bold"),
                   text_color="white").pack(expand=True)
        
        # Área para bloques de secuencia
        self.sequence_frame = ctk.CTkFrame(self.beam_area, fg_color="transparent")
        self.sequence_frame.pack(side="left", fill="both", expand=True)
        
        # Mensaje inicial
        self.empty_label = ctk.CTkLabel(self.sequence_frame, 
                                      text="Arrastra bloques aquí para crear una secuencia",
                                      font=("Arial", 12),
                                      text_color="#888888")
        self.empty_label.pack(expand=True)
    
    def create_control_panel(self):
        """Crea el panel de control lateral"""
        panel_frame = ctk.CTkFrame(self, fg_color="#E8E8E8", 
                                 corner_radius=10, border_width=2,
                                 border_color="#CCCCCC")
        panel_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Título
        ctk.CTkLabel(panel_frame, text="Controles", 
                   font=("Arial", 16, "bold")).pack(pady=15)
        
        # Botones de ejecución
        self.create_execution_buttons(panel_frame)
        
        # Estado
        self.create_status_display(panel_frame)
        
        # Controles de dispositivo
        self.create_device_controls(panel_frame)
    
    def create_execution_buttons(self, parent):
        """Crea los botones de ejecución"""
        exec_frame = ctk.CTkFrame(parent, fg_color="transparent")
        exec_frame.pack(pady=10)
        
        # Botón Play
        self.play_btn = ctk.CTkButton(exec_frame, text="▶ Ejecutar", 
                                    width=120, height=50,
                                    fg_color="#43A047",
                                    hover_color="#388E3C",
                                    font=("Arial", 14, "bold"),
                                    command=self.execute_sequence)
        self.play_btn.pack(pady=5)
        
        # Botón Stop
        self.stop_btn = ctk.CTkButton(exec_frame, text="⏹ Detener", 
                                    width=120, height=40,
                                    fg_color="#E53935",
                                    hover_color="#C62828",
                                    font=("Arial", 12, "bold"),
                                    command=self.stop_sequence,
                                    state="disabled")
        self.stop_btn.pack(pady=5)
        
        # Botón Limpiar
        ctk.CTkButton(exec_frame, text="🗑 Limpiar", 
                     width=120, height=35,
                     fg_color="#78909C",
                     hover_color="#546E7A",
                     font=("Arial", 12),
                     command=self.clear_sequence).pack(pady=5)
    
    def create_status_display(self, parent):
        """Crea el display de estado"""
        separator = ctk.CTkFrame(parent, height=2, fg_color="#CCCCCC")
        separator.pack(fill="x", padx=20, pady=10)
        
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(status_frame, text="Estado:", 
                    font=("Arial", 12, "bold")).pack(anchor="w")
        
        self.status_text = ctk.CTkTextbox(status_frame, height=60, 
                                        font=("Arial", 11))
        self.status_text.pack(fill="x", pady=5)
        self.status_text.insert("1.0", "Secuencia lista.\nArrastra bloques para comenzar.")
        self.status_text.configure(state="disabled")
    
    def create_device_controls(self, parent):
        """Crea controles de dispositivo"""
        separator = ctk.CTkFrame(parent, height=2, fg_color="#CCCCCC")
        separator.pack(fill="x", padx=20, pady=10)
        
        device_frame = ctk.CTkFrame(parent, fg_color="transparent")
        device_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(device_frame, text="Dispositivo:", 
                    font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Botón de conexión
        self.connect_btn = ctk.CTkButton(device_frame, text="🔗 Conectar Dispositivo",
                                       fg_color="#007ACC",
                                       hover_color="#1565C0",
                                       command=self.simulate_connection)
        self.connect_btn.pack(fill="x", pady=5)
        
        # Estado de conexión
        self.connection_status = ctk.CTkLabel(device_frame, 
                                            text="Desconectado",
                                            text_color="#E53935",
                                            font=("Arial", 10))
        self.connection_status.pack(anchor="w")
    
    def create_block_palette(self):
        """Crea la paleta de bloques en la parte inferior"""
        palette_frame = ctk.CTkFrame(self, height=150, fg_color="#D8D8D8")
        palette_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        palette_frame.grid_propagate(False)
        
        ctk.CTkLabel(palette_frame, text="Bloques de Comando", 
                    font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame para los bloques
        blocks_frame = ctk.CTkFrame(palette_frame, fg_color="transparent")
        blocks_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Definir bloques disponibles
        blocks = [
            {"name": "Adelante", "color": "#8CC63F", "icon": "▲", "type": "motor"},
            {"name": "Atrás", "color": "#8CC63F", "icon": "▼", "type": "motor"},
            {"name": "Izquierda", "color": "#8CC63F", "icon": "◀", "type": "motor"},
            {"name": "Derecha", "color": "#8CC63F", "icon": "▶", "type": "motor"},
            {"name": "Detener", "color": "#E53935", "icon": "⏹", "type": "control"},
            {"name": "Esperar", "color": "#FFC107", "icon": "⏱", "type": "control"},
            {"name": "Velocidad", "color": "#007ACC", "icon": "⚡", "type": "config"},
        ]
        
        # Crear bloques
        for block in blocks:
            self.create_block(blocks_frame, block)
    
    def create_block(self, parent, block):
        """Crea un bloque individual en la paleta"""
        block_frame = ctk.CTkFrame(parent, width=80, height=80, 
                                 fg_color=block["color"],
                                 corner_radius=8,
                                 border_width=2,
                                 border_color=self.darken_color(block["color"]))
        block_frame.pack(side="left", padx=5, pady=5)
        block_frame.pack_propagate(False)
        
        # Icono
        icon_label = ctk.CTkLabel(block_frame, text=block["icon"],
                                font=("Arial", 24, "bold"),
                                text_color="white")
        icon_label.pack(expand=True)
        
        # Nombre
        name_label = ctk.CTkLabel(block_frame, text=block["name"],
                                font=("Arial", 10),
                                text_color="white")
        name_label.pack(expand=True)
        
        # Hacer arrastrable
        for widget in [block_frame, icon_label, name_label]:
            widget.bind("<ButtonPress-1>", lambda e, b=block: self.start_drag(e, b))
    
    def start_drag(self, event, block):
        """Inicia el arrastre de un bloque"""
        print(f"Arrastrando: {block['name']}")
        # Aquí iría la lógica de arrastre visual
    
    def execute_sequence(self):
        """Ejecuta la secuencia"""
        if not self.sequence:
            self.update_status("Error: No hay secuencia para ejecutar")
            return
            
        self.is_running = True
        self.play_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.update_status("Ejecutando secuencia...")
    
    def stop_sequence(self):
        """Detiene la secuencia"""
        self.is_running = False
        self.play_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.update_status("Secuencia detenida")
    
    def clear_sequence(self):
        """Limpia la secuencia"""
        self.sequence = []
        # Limpiar visualmente la viga
        for widget in self.sequence_frame.winfo_children():
            widget.destroy()
        self.empty_label.pack(expand=True)
        self.update_status("Secuencia limpiada")
    
    def simulate_connection(self):
        """Simula conexión de dispositivo"""
        self.connect_btn.configure(state="disabled", text="Conectando...")
        self.connection_status.configure(text="Conectando...", text_color="#FF9800")
        
        # Simular conexión después de 2 segundos
        self.after(2000, self.finish_connection)
    
    def finish_connection(self):
        """Finaliza la simulación de conexión"""
        self.connect_btn.configure(state="normal", text="🔗 Conectar Dispositivo")
        self.connection_status.configure(text="Conectado (Simulación)", text_color="#43A047")
        self.update_status("Dispositivo conectado en modo simulación")
    
    def update_status(self, message):
        """Actualiza el display de estado"""
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.insert("1.0", message)
        self.status_text.configure(state="disabled")
    
    def darken_color(self, hex_color, factor=0.8):
        """Oscurece un color hexadecimal"""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
        except:
            return hex_color

if __name__ == "__main__":
    app = BluetoothProgramApp()
    app.mainloop()