import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import serial
import serial.tools.list_ports
import time 

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
        self.blocks = []
        self.drag_data = {"widget": None, "x": 0, "y": 0}
        self.bluetooth_visible = False
        self.block_width = 120
        self.block_height = 160
        self.block_spacing = 8
        self.current_executing_block = None

        # ---------------- ICONOS ----------------
        self.icons = {
            "up": ctk.CTkImage(light_image=Image.open("icons/up.png"), size=(40, 40)),
            "down": ctk.CTkImage(light_image=Image.open("icons/down.png"), size=(40, 40)),
            "left": ctk.CTkImage(light_image=Image.open("icons/left.png"), size=(40, 40)),
            "right": ctk.CTkImage(light_image=Image.open("icons/right.png"), size=(40, 40)),
            "time": ctk.CTkImage(light_image=Image.open("icons/time.png"), size=(45, 45)),
            "speed": ctk.CTkImage(light_image=Image.open("icons/speed.png"), size=(45, 45)),
            "bluetooth": ctk.CTkImage(light_image=Image.open("icons/bluetooth.png"), size=(25, 25)),
            "start": ctk.CTkImage(light_image=Image.open("icons/start.png"), size=(35, 35)),
            "stopbtn": ctk.CTkImage(light_image=Image.open("icons/stopbtn.png"), size=(35, 35)),
            "trash": ctk.CTkImage(light_image=Image.open("icons/trash.png"), size=(35, 35)),
        }

        # ---------------- PANEL IZQUIERDO ----------------
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

        # ---------------- ÁREA DE TRABAJO ----------------
        self.workspace = ctk.CTkFrame(self, fg_color="#1a1d29")
        self.workspace.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        # ---------------- BOTONES ----------------
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
            corner_radius=12,
            state="normal"
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
        self.bluetooth_panel = ctk.CTkFrame(self, width=400)
        self.bluetooth_panel.pack_propagate(False)
        
        ctk.CTkLabel(self.bluetooth_panel, text="Conexión Bluetooth", 
                    font=("Arial", 16, "bold")).pack(pady=12)
        
        self.frame_devices = ctk.CTkScrollableFrame(self.bluetooth_panel, height=250)
        self.frame_devices.pack(fill="both", padx=12, pady=6)
        
        ctk.CTkButton(self.bluetooth_panel, text="Buscar dispositivos", 
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

    # ======================================================
    # SISTEMA DE ARRASTRE 
    # ======================================================
    def start_drag(self, event, name, block_type, icon):
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
        if self.drag_data["widget"]:
            self.drag_data["widget"].place(x=event.x_root - 30, y=event.y_root - 30)

    def stop_drag(self, event):
        if self.drag_data["widget"]:
            x, y = self.workspace.winfo_rootx(), self.workspace.winfo_rooty()
            width, height = self.workspace.winfo_width(), self.workspace.winfo_height()
            
            if (x <= event.x_root <= x + width and 
                y <= event.y_root <= y + height):
                
                rel_x = event.x_root - x - self.block_width // 2
                rel_y = event.y_root - y - self.block_height // 2
                
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
        if not self.blocks:
            return 20, 20
        
        closest_block = None
        min_distance = float('inf')
        
        for block in self.blocks:
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
            new_x = closest_block["x"] + self.block_width + self.block_spacing
            new_y = closest_block["y"]
            return new_x, new_y
        
        return x, y

    def add_block(self, name, block_type, icon, x, y):
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
        
        content_frame = ctk.CTkFrame(block_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=10, pady=20)
        
        img_label = ctk.CTkLabel(content_frame, image=icon, text="")
        img_label.pack(expand=True, pady=(20, 9))
        
        entry = None
        if block_type in ["move_forward", "move_backward", "time"]:
            config_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            config_frame.pack(fill="x", pady=(10, 0))
            
            entry = ctk.CTkEntry(config_frame, width=70, placeholder_text="0", height=24)
            entry.insert(0, "0")
            entry.pack(pady=2)
            
        elif block_type in ["move_left", "move_right"]:
            config_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            config_frame.pack(fill="x", pady=(10, 0))
            
            # ComboBox para grados específicos
            entry = ctk.CTkComboBox(
                config_frame, 
                values=["45", "90", "180", "360"],
                width=70, 
                height=24,
                state="readonly"
            )
            entry.set("90")
            entry.pack(pady=2)
            
        elif block_type == "speed":
            config_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            config_frame.pack(fill="x", pady=(10, 0))
            
            entry = ctk.CTkComboBox(
                config_frame, 
                values=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
                width=70, 
                height=24,
                state="readonly"
            )
            entry.set("5")
            entry.pack(pady=2)
        
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

        block_info = {
            "frame": block_frame,
            "type": block_type,
            "name": name,
            "icon": icon,
            "x": x,
            "y": y,
            "entry": entry,
        }
        
        self.setup_block_drag(block_frame, block_info)
        del_btn.configure(command=lambda b=block_info: self.remove_block(b))
        self.blocks.append(block_info)

    def setup_block_drag(self, frame, block_info):
        def on_press(event):
            frame.start_x = event.x
            frame.start_y = event.y
            frame.lift()
            frame.configure(fg_color="#2a2e3a")

        def on_drag(event):
            if hasattr(frame, 'start_x'):
                new_x = frame.winfo_x() + (event.x - frame.start_x)
                new_y = frame.winfo_y() + (event.y - frame.start_y)
                frame.place(x=new_x, y=new_y)
                block_info["x"] = new_x
                block_info["y"] = new_y

        def on_release(event):
            if hasattr(frame, 'start_x'):
                snapped_x, snapped_y = self.find_snap_position(block_info["x"], block_info["y"])
                frame.place(x=snapped_x, y=snapped_y)
                block_info["x"] = snapped_x
                block_info["y"] = snapped_y
                frame.configure(fg_color="#22252e")

        frame.bind("<ButtonPress-1>", on_press)
        frame.bind("<B1-Motion>", on_drag)
        frame.bind("<ButtonRelease-1>", on_release)
        
        for child in frame.winfo_children():
            child.bind("<ButtonPress-1>", on_press)
            child.bind("<B1-Motion>", on_drag)
            child.bind("<ButtonRelease-1>", on_release)

    def remove_block(self, block):
        if block in self.blocks:
            block["frame"].destroy()
            self.blocks.remove(block)

    def clear_all_blocks(self):
        for block in self.blocks[:]:
            self.remove_block(block)

    # ======================================================
    # EJECUCIÓN 
    # ======================================================
    def start_execution(self):
        if not self.blocks:
            messagebox.showwarning("Sin bloques", "No hay bloques en el área de trabajo.")
            return
            
        if not self.serial_port:
            messagebox.showwarning("Sin conexión", "No hay dispositivo conectado.")
            return

        self.run_button.configure(state="disabled")
        
        sorted_blocks = sorted(self.blocks, key=lambda b: (b["y"], b["x"]))
        velocidad = 200 
        
        self._execute_blocks_async(sorted_blocks, 0, velocidad)

    def _execute_blocks_async(self, blocks, index, velocidad):
        if index >= len(blocks):
            self.run_button.configure(state="normal")
            self.send_serial("S\n")
            self.after(0, lambda: messagebox.showinfo("Completado", "Secuencia terminada"))
            return

        block = blocks[index]
        command = block["type"]
        
        param_value = 1
        if "entry" in block and block["entry"]:
            try:
                texto = block["entry"].get().strip()
                if texto:
                    param_value = float(texto)
            except:
                param_value = 1

        self.after(0, lambda b=block: self.highlight_block(b))
        self.update()

        if command == "speed":
            velocidad_escala = max(1, min(9, int(param_value)))
            velocidad = int((velocidad_escala - 1) / 8 * 227 + 28)
            delay = 500
            
        elif command == "time":
            msg = f"T{int(param_value * 1000)}\n"
            self.send_serial(msg)
            delay = int(param_value * 1000)
            
        elif command in ["move_left", "move_right"]:
            letra = "L" if command == "move_left" else "R"
            
            # Leer correctamente el ComboBox
            if "entry" in block and block["entry"]:
                try:
                    texto = block["entry"].get().strip()
                    if texto:
                        grados_configurados = int(texto)
                    else:
                        grados_configurados = 90
                except:
                    grados_configurados = 90
            else:
                grados_configurados = 90
            
            # ✅ PRUEBA: 4x los grados
            grados_enviar = grados_configurados * 8
            
            msg = f"{letra}{grados_enviar}\n"
            self.send_serial(msg)

            print(f"Giro enviado: {msg.strip()}  ({grados_configurados} config -> {grados_enviar} sent)")

            # Delay proporcional
            delay = int((grados_configurados / 90.0) * 800)
            delay = max(delay, 200)

            print(f"Delay calculado: {delay} ms")

        elif command in ["move_forward", "move_backward"]:
            letra = "F" if command == "move_forward" else "B"
            msg = f"{letra}{velocidad}\n"
            self.send_serial(msg)
            delay = int(param_value * 1000) if param_value > 0 else 1000
            
        else:
            delay = 500

        self.after(delay + 50, lambda: self._finish_block_async(blocks, index, velocidad, block))

    def _finish_block_async(self, blocks, index, velocidad, block):
        self.after(0, lambda b=block: self.unhighlight_block(b))
        self.update()
        
        command = block["type"]
        if command in ["move_forward", "move_backward", "move_left", "move_right"]:
            self.send_serial("S\n")
            self.after(100, lambda: self._execute_blocks_async(blocks, index + 1, velocidad))
        else:
            self._execute_blocks_async(blocks, index + 1, velocidad)

    def stop_execution(self):
        print("Deteniendo ejecución...")
        
        self.run_button.configure(state="normal")
        
        if getattr(self, 'current_executing_block', None):
            self.unhighlight_block(self.current_executing_block)
        
        for after_id in self.tk.eval('after info').split():
            self.after_cancel(after_id)
        
        self.send_serial("S\n")
        messagebox.showinfo("Detenido", "Ejecución cancelada")

    def highlight_block(self, block):
        block["frame"].configure(
            fg_color="#355a9a", 
            border_color="#4a72c4",
            border_width=3
        )
        self.current_executing_block = block
        block["frame"].update_idletasks()

    def unhighlight_block(self, block):
        block["frame"].configure(
            fg_color="#22252e", 
            border_color="#2a2e3a",
            border_width=2
        )
        block["frame"].update_idletasks()
        self.current_executing_block = None

    # ======================================================
    # BLUETOOTH 
    # ======================================================
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
        
        if not ports:
            label = ctk.CTkLabel(self.frame_devices, text="No se encontraron dispositivos", 
                               text_color="gray", font=("Arial", 12))
            label.pack(pady=20)
            return
        
        for port in ports:
            frame = ctk.CTkFrame(self.frame_devices)
            frame.pack(fill="x", padx=6, pady=4)
            
            device_info = self.detect_device_info(port)
            
            label = ctk.CTkLabel(frame, text=device_info, anchor="w", font=("Arial", 11))
            label.pack(side="left", fill="x", expand=True, padx=8, pady=6)
            
            ctk.CTkButton(frame, text="Seleccionar", width=100, height=28,
                         command=lambda p=port.device, n=device_info: self.select_port(p, n)).pack(side="right", padx=6)

    def detect_device_info(self, port):
        description = port.description.upper() if port.description else ""
        manufacturer = port.manufacturer.upper() if port.manufacturer else ""
        product = port.product.upper() if port.product else ""
        
        if "LMB" in description or "LMB" in manufacturer or "LMB" in product:
            return f"LMB Robot BLE ({port.device})"
        
        if "BLUETOOTH" in description or "BLE" in description:
            if "SERIAL" in description:
                return f"Dispositivo BLE Serial ({port.device})"
            else:
                return f"Dispositivo BLE ({port.device})"
        
        if "ARDUINO" in description or "CH340" in description or "CP210" in description:
            return f"Arduino ({port.device})"
        
        return f"{port.description} ({port.device})"

    def select_port(self, port, device_info=None):
        self.selected_port = port
        display_text = f"Seleccionado: {device_info}" if device_info else f"Seleccionado: {port}"
        
        self.connection_info.configure(text=display_text, text_color="blue")
        print(f"Dispositivo seleccionado: {device_info}")

    def connect_serial(self):
        if not self.selected_port:
            self.connection_info.configure(text="Seleccione un dispositivo", text_color="red")
            return
        
        try:
            device_name = "Dispositivo"
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if port.device == self.selected_port:
                    device_name = self.detect_device_info(port)
                    break
            
            print(f"Conectando a {device_name}...")
            self.connection_info.configure(text=f"Conectando a {device_name}...", text_color="orange")
            
            self.serial_port = serial.Serial(
                port=self.selected_port,
                baudrate=9600,
                timeout=1,
                write_timeout=1
            )
        
            print("Esperando inicialización del Arduino...")
            time.sleep(2)
        
            print("Buscando ROBOT_CONECTADO...")
            start_time = time.time()
            while time.time() - start_time < 3:
                if self.serial_port.in_waiting > 0:
                    try:
                        line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            print(f"ARDUINO: {line}")
                    except Exception as e:
                        print(f"Error leyendo: {e}")
                time.sleep(0.1)
        
            self.connection_info.configure(text=f"Conectado: {device_name}", text_color="green")
            self.bluetooth_button.configure(fg_color="#1e6b30", hover_color="#2a8c44")
            print("CONEXION ESTABLECIDA")
        
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
            
                self.serial_port.reset_input_buffer()
                self.serial_port.write(msg.encode())
                self.serial_port.flush()
            
                time.sleep(0.3)
                start_time = time.time()
                while time.time() - start_time < 1.5:
                    if self.serial_port.in_waiting > 0:
                        try:
                            line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                            if line:
                                print(f"RESPUESTA: '{line}'")
                        except Exception as e:
                            print(f"Error decodificando: {e}")
                    time.sleep(0.1)
            
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