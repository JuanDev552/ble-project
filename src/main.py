import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import threading
import time
import serial
import serial.tools.list_ports

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BlockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Control Bluetooth")
        self.geometry("1000x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # ---------------- VARIABLES ----------------
        self.serial_port = None
        self.selected_port = None
        self._stop_execution = threading.Event()
        self.blocks = []
        self.drag_data = {"widget": None, "x": 0, "y": 0}
        self.bluetooth_visible = False
        self.block_width = 120
        self.block_height = 160  # AUMENTADO: Más altura para separar mejor los elementos
        self.block_spacing = 8

        # ---------------- ICONOS ----------------
        self.icons = {
            "up": ctk.CTkImage(light_image=Image.open("icons/up.png"), size=(40, 40)),
            "down": ctk.CTkImage(light_image=Image.open("icons/down.png"), size=(40, 40)),
            "left": ctk.CTkImage(light_image=Image.open("icons/left.png"), size=(40, 40)),
            "right": ctk.CTkImage(light_image=Image.open("icons/right.png"), size=(40, 40)),
            "stop": ctk.CTkImage(light_image=Image.open("icons/stop.png"), size=(45, 45)),
            "time": ctk.CTkImage(light_image=Image.open("icons/time.png"), size=(45, 45)),
            "speed": ctk.CTkImage(light_image=Image.open("icons/speed.png"), size=(45, 45)),
            "bluetooth": ctk.CTkImage(light_image=Image.open("icons/bluetooth.png"), size=(25, 25)),
            "start": ctk.CTkImage(light_image=Image.open("icons/start.png"), size=(35, 35)),
            "stopbtn": ctk.CTkImage(light_image=Image.open("icons/stopbtn.png"), size=(35, 35)),
            "trash": ctk.CTkImage(light_image=Image.open("icons/trash.png"), size=(35, 35)),
        }

        # ---------------- PANEL IZQUIERDO (BLOQUES DISPONIBLES) ----------------
        self.block_palette = ctk.CTkFrame(self, width=180, fg_color="#111317")
        self.block_palette.pack(side="left", fill="y", padx=8, pady=8)

        ctk.CTkLabel(
            self.block_palette, text="Bloques disponibles", font=("Arial", 16, "bold")
        ).pack(pady=15)

        self.available_blocks = [
            ("Adelante", "move_forward", self.icons["up"]),
            ("Atrás", "move_backward", self.icons["down"]),
            ("Izquierda", "move_left", self.icons["left"]),
            ("Derecha", "move_right", self.icons["right"]),
            ("Detener", "stop", self.icons["stop"]),
            ("Esperar", "time", self.icons["time"]),
            ("Velocidad", "speed", self.icons["speed"]),
        ]

        for name, block_type, icon in self.available_blocks:
            btn = ctk.CTkButton(
                self.block_palette,
                text="",
                image=icon,
                fg_color="#1a1d29",
                hover_color="#2b2f3d",
                height=60,
                width=60,
                corner_radius=12,
            )
            btn.pack(pady=8)
            btn.bind("<ButtonPress-1>", lambda e, n=name, t=block_type, i=icon: self.start_drag(e, n, t, i))

        # ---------------- ÁREA DE TRABAJO LIBRE ----------------
        self.workspace = ctk.CTkFrame(self, fg_color="#1a1d29")
        self.workspace.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        # ---------------- BOTONES DE CONTROL ----------------
        control_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        control_frame.pack(side="bottom", fill="x", pady=10)

        self.run_button = ctk.CTkButton(
            control_frame, 
            text="Ejecutar",
            image=self.icons["start"],
            command=self.start_execution,
            width=120,
            height=50,
            fg_color="#1e6b30",
            hover_color="#2a8c44",
            corner_radius=12
        )
        self.run_button.pack(side="left", padx=8)

        self.stop_button = ctk.CTkButton(
            control_frame,
            text="Detener",
            image=self.icons["stopbtn"],
            command=self.stop_execution,
            width=120,
            height=50,
            fg_color="#b22c2c",
            hover_color="#d13434",
            corner_radius=12
        )
        self.stop_button.pack(side="left", padx=8)

        self.clear_button = ctk.CTkButton(
            control_frame, 
            text="Limpiar",
            image=self.icons["trash"],
            command=self.clear_all_blocks,
            width=120,
            height=50,
            fg_color="#d35400",
            hover_color="#e67e22",
            corner_radius=12
        )
        self.clear_button.pack(side="left", padx=8)

        # ---------------- PANEL BLUETOOTH ----------------
        self.bluetooth_panel = ctk.CTkFrame(self, width=500)
        self.bluetooth_panel.pack_propagate(False)
        
        ctk.CTkLabel(self.bluetooth_panel, text="Conexión Bluetooth", 
                    font=("Arial", 16, "bold")).pack(pady=12)
        
        self.frame_devices = ctk.CTkScrollableFrame(self.bluetooth_panel, height=250)
        self.frame_devices.pack(fill="both", padx=12, pady=6)
        
        ctk.CTkButton(self.bluetooth_panel, text="Buscar puertos COM", 
                     command=self.scan_ports, height=35).pack(fill="x", padx=12, pady=(4, 8))
        
        self.connection_info = ctk.CTkLabel(self.bluetooth_panel, text="No conectado", 
                                          text_color="red", wraplength=350)
        self.connection_info.pack(pady=8)
        
        buttons_frame = ctk.CTkFrame(self.bluetooth_panel)
        buttons_frame.pack(pady=8)
        
        self.connect_button = ctk.CTkButton(buttons_frame, text="Conectar", 
                                          fg_color="#1e6b30", command=self.connect_serial,
                                  width=120, height=35)
        self.connect_button.grid(row=0, column=0, padx=8)
        
        self.disconnect_button = ctk.CTkButton(buttons_frame, text="Desconectar", 
                                             fg_color="#b22c2c", command=self.disconnect_serial)
        self.disconnect_button.grid(row=0, column=1, padx=8)

        # Botón Bluetooth flotante
        self.bluetooth_button = ctk.CTkButton(
            self.workspace,
            text="",
            image=self.icons["bluetooth"],
            width=35,
            height=35,
            fg_color="#1e2130",
            hover_color="#2c3245",
            corner_radius=8,
            command=self.toggle_bluetooth_panel,
        )
        self.bluetooth_button.place(relx=0.98, rely=0.02, anchor="ne")

    # =========================
    # SISTEMA DE ARRASTRE Y CONEXIÓN MEJORADO
    # =========================
    def start_drag(self, event, name, block_type, icon):
        """Inicia el arrastre de un bloque desde la paleta"""
        drag_block = ctk.CTkLabel(self, image=icon, text="", fg_color="#2c2f3b", corner_radius=10)
        drag_block.place(x=event.x_root - 30, y=event.y_root - 30)
        drag_block.lift()
        
        self.drag_data = {
            "widget": drag_block, 
            "name": name, 
            "type": block_type, 
            "icon": icon,
            "start_x": event.x_root,
            "start_y": event.y_root,
            "is_new": True
        }
        
        self.bind("<Motion>", self.do_drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)

    def do_drag(self, event):
        """Mueve el bloque durante el arrastre"""
        if self.drag_data["widget"]:
            self.drag_data["widget"].place(x=event.x_root - 30, y=event.y_root - 30)

    def stop_drag(self, event):
        """Termina el arrastre y coloca el bloque donde se soltó"""
        if self.drag_data["widget"]:
            x, y = self.workspace.winfo_rootx(), self.workspace.winfo_rooty()
            width, height = self.workspace.winfo_width(), self.workspace.winfo_height()
            
            if (x <= event.x_root <= x + width and 
                y <= event.y_root <= y + height):
                
                rel_x = event.x_root - x - self.block_width // 2
                rel_y = event.y_root - y - self.block_height // 2
                
                # Para bloques nuevos, buscar posición al lado de otros
                if self.drag_data["is_new"]:
                    snapped_x, snapped_y = self.find_snap_position(rel_x, rel_y)
                    rel_x, rel_y = snapped_x, snapped_y
                
                self.add_block(
                    self.drag_data["name"], 
                    self.drag_data["type"], 
                    self.drag_data["icon"],
                    rel_x,
                    rel_y
                )
            
            self.drag_data["widget"].destroy()
            self.drag_data = {"widget": None, "x": 0, "y": 0}
        
        self.unbind("<Motion>")
        self.unbind("<ButtonRelease-1>")

    def find_snap_position(self, x, y):
        """Encuentra la mejor posición para pegar el bloque al lado de otros"""
        if not self.blocks:
            # Si no hay bloques, poner en posición inicial
            return 20, 20
        
        # Buscar el bloque más cercano
        closest_block = None
        min_distance = float('inf')
        
        for block in self.blocks:
            # Calcular distancia entre centros
            block_center_x = block["x"] + self.block_width // 2
            block_center_y = block["y"] + self.block_height // 2
            current_center_x = x + self.block_width // 2
            current_center_y = y + self.block_height // 2
            
            distance = ((block_center_x - current_center_x) ** 2 + 
                       (block_center_y - current_center_y) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_block = block
        
        if closest_block and min_distance < 120:
            # Pegar al lado derecho del bloque más cercano con menos espacio
            new_x = closest_block["x"] + self.block_width + self.block_spacing
            new_y = closest_block["y"]
            return new_x, new_y
        
        # Si no hay bloques cercanos, mantener posición
        return x, y

    def add_block(self, name, block_type, icon, x, y):
        """Añade un bloque en una posición específica"""
        block_frame = ctk.CTkFrame(
            self.workspace, 
            corner_radius=12,
            fg_color="#22252e",
            border_width=2,
            border_color="#2a2e3a",
            width=self.block_width,
            height=self.block_height
        )
        block_frame.place(x=x, y=y)
        
        # Contenido del bloque - Ajustar padding para mejor distribución
        content_frame = ctk.CTkFrame(block_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=10, pady=20)
        
        # Icono centrado arriba con más espacio
        img_label = ctk.CTkLabel(content_frame, image=icon, text="")
        img_label.pack(expand=True, pady=(20, 9))
        
        # Configuración - mover más hacia abajo
        entry = None
        if block_type in ["move_forward", "move_backward", "move_left", "move_right", "time"]:
            config_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            config_frame.pack(fill="x", pady=(10, 0))
            
            entry = ctk.CTkEntry(config_frame, width=70, placeholder_text="1.0", height=24)
            entry.insert(0, "1.0")
            entry.pack(pady=2)
            
        elif block_type == "speed":
            config_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            config_frame.pack(fill="x", pady=(10, 0))
            
            entry = ctk.CTkEntry(config_frame, width=70, placeholder_text="100", height=24)
            entry.insert(0, "100")
            entry.pack(pady=2)
        
        # Botón eliminar - MOVER MÁS ABAJO
        del_btn = ctk.CTkButton(
            block_frame,
            text="×", 
            width=20,
            height=20,
            fg_color="#a22424",
            hover_color="#b93a3a",
            font=("Arial", 10, "bold"),
            corner_radius=10
        )
        del_btn.place(relx=0.5, rely=0.95, anchor="center")

        # Información del bloque
        block_info = {
            "frame": block_frame,
            "type": block_type,
            "name": name,
            "icon": icon,
            "x": x,
            "y": y,
            "config": {"time": 1.0, "speed": 100},
        }
        
        if entry:
            block_info["entry"] = entry
            entry.bind("<KeyRelease>", lambda e, b=block_info: self.update_block_config(b))
        
        # Configurar arrastre MEJORADO
        self.setup_block_drag(block_frame, block_info)
        
        del_btn.configure(command=lambda b=block_info: self.remove_block(b))
        
        self.blocks.append(block_info)

    def setup_block_drag(self, frame, block_info):
        """Configura el arrastre del bloque de manera robusta"""
        def on_press(event):
            # Guardar posición inicial relativa
            frame.start_x = event.x
            frame.start_y = event.y
            frame.lift()
            frame.configure(fg_color="#2a2e3a")  # Resaltar al agarrar

        def on_drag(event):
            if hasattr(frame, 'start_x'):
                # Calcular nueva posición absoluta
                new_x = frame.winfo_x() + (event.x - frame.start_x)
                new_y = frame.winfo_y() + (event.y - frame.start_y)
                
                # Mover el bloque
                frame.place(x=new_x, y=new_y)
                block_info["x"] = new_x
                block_info["y"] = new_y

        def on_release(event):
            if hasattr(frame, 'start_x'):
                # Buscar posición de snap al soltar
                snapped_x, snapped_y = self.find_snap_position(block_info["x"], block_info["y"])
                
                # Mover a posición final
                frame.place(x=snapped_x, y=snapped_y)
                block_info["x"] = snapped_x
                block_info["y"] = snapped_y
                
                frame.configure(fg_color="#22252e")  # Quitar resaltado

        # Asignar eventos a TODO el frame y sus hijos
        frame.bind("<ButtonPress-1>", on_press)
        frame.bind("<B1-Motion>", on_drag)
        frame.bind("<ButtonRelease-1>", on_release)
        
        # También hacer arrastrables los elementos hijos
        for child in frame.winfo_children():
            child.bind("<ButtonPress-1>", on_press)
            child.bind("<B1-Motion>", on_drag)
            child.bind("<ButtonRelease-1>", on_release)

    def update_block_config(self, block):
        """Actualiza la configuración del bloque"""
        if "entry" in block:
            text = block["entry"].get().strip()
            try:
                if block["type"] == "speed":
                    block["config"]["speed"] = int(text) if text else 100
                else:
                    block["config"]["time"] = float(text) if text else 1.0
            except ValueError:
                if block["type"] == "speed":
                    block["config"]["speed"] = 100
                else:
                    block["config"]["time"] = 1.0

    def remove_block(self, block):
        """Elimina un bloque del workspace"""
        if block in self.blocks:
            block["frame"].destroy()
            self.blocks.remove(block)

    def clear_all_blocks(self):
        """Elimina todos los bloques del workspace"""
        for block in self.blocks[:]:
            self.remove_block(block)

    # =========================
    # EJECUCIÓN (ORDEN POR POSICIÓN)
    # =========================
    def start_execution(self):
        if not self.blocks:
            messagebox.showwarning("Sin bloques", "No hay bloques en el área de trabajo.")
            return
            
        if not self.serial_port:
            messagebox.showwarning("Sin conexión", "No hay dispositivo conectado.")
            return
            
        self._stop_execution.clear()
        threading.Thread(target=self.execute_thread, daemon=True).start()

    def stop_execution(self):
        self._stop_execution.set()

    def execute_thread(self):
        """Ejecuta los bloques en orden natural"""
        # Ordenar por posición (arriba a abajo, izquierda a derecha)
        sorted_blocks = sorted(self.blocks, key=lambda b: (b["y"], b["x"]))
        
        command_map = {
            "move_forward": "F",
            "move_backward": "B", 
            "move_left": "L",
            "move_right": "R",
            "stop": "S",
            "time": "T",
            "speed": "V"
        }
        
        for block in sorted_blocks:
            if self._stop_execution.is_set():
                break
                
            command = block["type"]
            duration = block["config"].get("time", 1.0)
            speed = block["config"].get("speed", 100)
            code = command_map.get(command, "?")
            
            if command == "speed":
                msg = f"{code}{speed}\n"
            elif command == "time":
                msg = f"{code}{int(duration * 1000)}\n"
            else:
                msg = f"{code}\n"
                
            self.send_serial(msg)
            
            self.after(0, lambda b=block: self.highlight_block(b))
            
            if command in ["move_forward", "move_backward", "move_left", "move_right"]:
                time.sleep(duration)
            elif command == "time":
                time.sleep(duration)
            
            self.after(0, lambda b=block: self.unhighlight_block(b))
            
            if not self._stop_execution.is_set():
                time.sleep(0.3)
            
        if not self._stop_execution.is_set():
            self.send_serial("S\n")
            self.after(0, lambda: messagebox.showinfo("Completado", "Secuencia terminada"))

    def highlight_block(self, block):
        block["frame"].configure(fg_color="#355a9a", border_color="#4a72c4")

    def unhighlight_block(self, block):
        block["frame"].configure(fg_color="#22252e", border_color="#2a2e3a")

    # =========================
    # BLUETOOTH (MANTIENE CÓDIGO ORIGINAL)
    # =========================
    def toggle_bluetooth_panel(self):
        if self.bluetooth_panel.winfo_ismapped():
            self.bluetooth_panel.pack_forget()
            self.bluetooth_visible = False
        else:
            self.bluetooth_panel.pack(side="right", fill="y", padx=8, pady=8)
            self.bluetooth_visible = True

    def scan_ports(self):
        for widget in self.frame_devices.winfo_children():
            widget.destroy()
            
        ports = serial.tools.list_ports.comports()
        for port in ports:
            frame = ctk.CTkFrame(self.frame_devices)
            frame.pack(fill="x", padx=6, pady=4)
            
            label = ctk.CTkLabel(frame, text=f"{port.description} ({port.device})", anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=6)
            
            ctk.CTkButton(frame, text="Seleccionar", width=100,
                        command=lambda p=port.device: self.select_port(p)).pack(side="right", padx=6)

    def select_port(self, port):
        self.selected_port = port
        self.connection_info.configure(text=f"Seleccionado: {port}", text_color="blue")
        print(f"Puerto seleccionado: {port}")

    def connect_serial(self):
        if not self.selected_port:
            self.connection_info.configure(text="Seleccione un puerto", text_color="red")
            return
        
        try:
            print(f"Conectando a {self.selected_port}...")
            self.serial_port = serial.Serial(
                port=self.selected_port,
                baudrate=9600,
                timeout=1,
                write_timeout=1
            )
        
            print("Esperando inicialización del Arduino...")
            time.sleep(2)
        
            # Leer mensaje de bienvenida
            print("Buscando ROBOT_CONECTADO...")
            initial_responses = []
            start_time = time.time()
            while time.time() - start_time < 3:
                if self.serial_port.in_waiting > 0:
                    try:
                        line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            initial_responses.append(line)
                            print(f"ARDUINO: {line}")
                            if "ROBOT_CONECTADO" in line:
                                print("ROBOT DETECTADO Y CONECTADO!")
                    except Exception as e:
                        print(f"Error leyendo: {e}")
                time.sleep(0.1)
        
            self.connection_info.configure(text=f"Conectado a {self.selected_port}", text_color="green")
            self.bluetooth_button.configure(fg_color="#1e6b30", hover_color="#2a8c44")
            print("CONEXIÓN BLUETOOTH ESTABLECIDA")
        
        except Exception as e:
            self.connection_info.configure(text=f"Error: {e}", text_color="red")
            print(f"ERROR: {e}")

    def disconnect_serial(self):
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
            self.connection_info.configure(text="No conectado", text_color="red")
            self.bluetooth_button.configure(fg_color="#1e2130", hover_color="#2c3245")
            print("Desconectado")

    def send_serial(self, msg):
        try:
            if self.serial_port and self.serial_port.is_open:
                print(f"ENVIANDO: '{msg.strip()}'")
            
                # Limpiar buffer antes de enviar
                self.serial_port.reset_input_buffer()
            
                # Enviar comando
                self.serial_port.write(msg.encode())
                self.serial_port.flush()
            
                # Esperar y leer respuestas
                time.sleep(0.5)
                responses = []
                start_time = time.time()
                while time.time() - start_time < 2:
                    if self.serial_port.in_waiting > 0:
                        try:
                            line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                            if line:
                                responses.append(line)
                                print(f"RESPUESTA: '{line}'")
                        except Exception as e:
                            print(f"Error decodificando: {e}")
                    time.sleep(0.1)
            
                if not responses:
                    print("No hubo respuesta")
                else:
                    print(f"Comando ejecutado - Respuestas: {len(responses)}")
                
            else:
                print("Puerto no conectado")
        except Exception as e:
            print(f"Error enviando: {e}")

    def on_close(self):
        if self.serial_port:
            self.serial_port.close()
        self.destroy()

if __name__ == "__main__":
    app = BlockApp()
    app.mainloop()