import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from ble_manager import BLEManager
import asyncio
import threading

ble = BLEManager()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BlockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Control Bluetooth - Bloques Configurables")
        self.geometry("1000x700")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # ---------------- ICONOS ----------------
        self.icons = {
            "up": ctk.CTkImage(light_image=Image.open("icons/up.png"), size=(40, 40)),
            "down": ctk.CTkImage(light_image=Image.open("icons/down.png"), size=(40, 40)),
            "left": ctk.CTkImage(light_image=Image.open("icons/left.png"), size=(40, 40)),
            "right": ctk.CTkImage(light_image=Image.open("icons/right.png"), size=(40, 40)),
            #"rotate": ctk.CTkImage(light_image=Image.open("icons/rotate.png"), size=(45, 45)),
            "stop": ctk.CTkImage(light_image=Image.open("icons/stop.png"), size=(45, 45)),
            "time": ctk.CTkImage(light_image=Image.open("icons/time.png"), size=(45, 45)),
            "speed": ctk.CTkImage(light_image=Image.open("icons/speed.png"), size=(45, 45)),
            "bluetooth": ctk.CTkImage(light_image=Image.open("icons/bluetooth.png"), size=(25, 25)),
            "start": ctk.CTkImage(light_image=Image.open("icons/start.png"), size=(35, 35)),
            "stopbtn": ctk.CTkImage(light_image=Image.open("icons/stopbtn.png"), size=(35, 35)),
            "trash": ctk.CTkImage(light_image=Image.open("icons/trash.png"), size=(35, 35)),
        }

        # ---------------- PANEL IZQUIERDO ----------------
        self.block_frame = ctk.CTkFrame(self, width=250, fg_color="#111317")
        self.block_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(
            self.block_frame, text="Bloques disponibles", font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.available_blocks = [
            ("Adelante", "move_forward", self.icons["up"]),
            ("Atrás", "move_backward", self.icons["down"]),
            ("Izquierda", "move_left", self.icons["left"]),
            ("Derecha", "move_right", self.icons["right"]),
            #("Girar", "rotate", self.icons["rotate"]),
            ("Detener", "stop", self.icons["stop"]),
            ("Esperar", "time", self.icons["time"]),
            ("Velocidad", "speed", self.icons["speed"]),
        ]

        for name, block_type, icon in self.available_blocks:
            btn = ctk.CTkButton(
                self.block_frame,
                text="",
                image=icon,
                fg_color="#1a1d29",
                hover_color="#2b2f3d",
                height=60,
                width=60,
                corner_radius=15,
            )
            btn.pack(pady=6)
            btn.bind("<ButtonPress-1>", lambda e, n=name, t=block_type, i=icon: self.start_drag(e, n, t, i))

        # ---------------- PANEL CENTRAL ----------------
        self.sequence_frame = ctk.CTkFrame(self, fg_color="#15171c")
        self.sequence_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.sequence_label = ctk.CTkLabel(
            self.sequence_frame, text="Secuencia de comandos", font=("Arial", 16, "bold")
        )
        self.sequence_label.pack(pady=5)

        self.block_container = ctk.CTkFrame(self.sequence_frame, fg_color="#1a1d29", corner_radius=10)
        self.block_container.pack(fill="both", expand=True, pady=10, padx=20)

        # ---------------- BOTONES DE CONTROL ----------------
        control_frame = ctk.CTkFrame(self.sequence_frame, fg_color="transparent")
        control_frame.pack(side="bottom", pady=10)

        # Botón EJECUTAR (start.png)
        self.run_button = ctk.CTkButton(
            control_frame, 
            text="",
            image=self.icons["start"],
            command=self.start_sequence,
            width=55,
            height=55,
            fg_color="#1e6b30",
            hover_color="#2a8c44",
            corner_radius=12
        )
        self.run_button.grid(row=0, column=0, padx=8)

        # Botón DETENER (stopbtn.png)
        self.stop_button = ctk.CTkButton(
            control_frame,
            text="",
            image=self.icons["stopbtn"],
            command=self.stop_sequence,
            width=55,
            height=55,
            fg_color="#b22c2c",
            hover_color="#d13434",
            corner_radius=12
        )
        self.stop_button.grid(row=0, column=1, padx=8)

        # Botón LIMPIAR (trash.png)
        self.clear_button = ctk.CTkButton(
            control_frame, 
            text="",
            image=self.icons["trash"],
            command=self.clear_sequence,
            width=55,
            height=55,
            fg_color="#d35400",
            hover_color="#e67e22",
            corner_radius=12
        )
        self.clear_button.grid(row=0, column=2, padx=8)

        # ---------------- PANEL BLUETOOTH ----------------
        self.bluetooth_panel = ctk.CTkFrame(
            self, width=350, fg_color="#10131a", corner_radius=0
        )
        self.bluetooth_visible = False

        # Contenedor interior con padding
        inner_bt_frame = ctk.CTkFrame(self.bluetooth_panel, fg_color="#10131a", corner_radius=0)
        inner_bt_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Cabecera con icono + texto
        header_frame = ctk.CTkFrame(inner_bt_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        bt_icon = ctk.CTkLabel(header_frame, text="", font=("Arial", 22))
        bt_icon.pack(side="left", padx=(0, 8))

        bt_title = ctk.CTkLabel(header_frame, text="Conexión Bluetooth", font=("Arial", 18, "bold"))
        bt_title.pack(side="left", padx=(0, 10))

        # Botón de cerrar (esquina superior derecha)
        self.close_bt_panel = ctk.CTkButton(
            header_frame,
            text="✕",
            width=32,
            height=32,
            fg_color="#2b2b2b",
            hover_color="#b22c2b",
            corner_radius=50,
            font=("Arial", 16, "bold"),
            command=self.toggle_bluetooth_panel,
        )
        self.close_bt_panel.pack(side="right")

        # Línea separadora
        sep_line = ctk.CTkLabel(inner_bt_frame, text="", fg_color="#2c3245", height=2)
        sep_line.pack(fill="x", pady=10)

        # Botón de búsqueda
        self.search_button = ctk.CTkButton(
            inner_bt_frame,
            text="Buscar dispositivos",
            command=self.start_ble_scan,
            fg_color="#1e407d",
            hover_color="#2758ad",
            corner_radius=8,
            height=38,
            font=("Arial", 14, "bold")
        )
        self.search_button.pack(pady=(5, 15), fill="x")

        # ---------- MARCO PARA LISTA DE DISPOSITIVOS ----------
        list_frame = ctk.CTkFrame(inner_bt_frame, fg_color="#141820", corner_radius=10)
        list_frame.pack(fill="both", expand=True, pady=10)

        # Scroll interno
        self.device_container = ctk.CTkScrollableFrame(
            list_frame, fg_color="#141820", corner_radius=10
        )
        self.device_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------------- BOTÓN PRINCIPAL BLUETOOTH ----------------
        self.bluetooth_button = ctk.CTkButton(
            self.sequence_frame,
            text="",
            image=self.icons["bluetooth"],
            width=35,
            height=35,
            fg_color="#1e2130",
            hover_color="#2c3245",
            corner_radius=8,
            command=self.toggle_bluetooth_panel,
        )
        self.bluetooth_button.place(relx=0.98, rely=0.97, anchor="se")

        # ---------------- VARIABLES ----------------
        self.blocks = []
        self.drag_data = {"widget": None, "y": 0}
        self.stop_execution = False
        self.connected_device = None

    # =========================
    # DRAG & DROP
    # =========================
    def start_drag(self, event, name, block_type, icon):
        frame = ctk.CTkLabel(self, image=icon, text="", fg_color="#2c2f3b", corner_radius=10)
        frame.place(x=event.x_root - 30, y=event.y_root - 30)
        frame.lift()
        self.drag_data["widget"] = frame
        self.drag_data["name"] = name
        self.drag_data["type"] = block_type
        self.drag_data["icon"] = icon
        self.bind("<Motion>", self.do_drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)

    def do_drag(self, event):
        w = self.drag_data["widget"]
        if w:
            w.place(x=event.x_root - 30, y=event.y_root - 30)

    def stop_drag(self, event):
        w = self.drag_data["widget"]
        if w:
            x, y = self.block_container.winfo_rootx(), self.block_container.winfo_rooty()
            w_x, w_y = event.x_root, event.y_root
            if x < w_x < x + self.block_container.winfo_width() and y < w_y < y + self.block_container.winfo_height():
                w.destroy()
                self.add_block(self.drag_data["name"], self.drag_data["type"], self.drag_data["icon"])
            else:
                w.destroy()
        self.drag_data = {"widget": None, "y": 0}
        self.unbind("<Motion>")
        self.unbind("<ButtonRelease-1>")

    # =========================
    # BLOQUES EN SECUENCIA
    # =========================
    def add_block(self, name, block_type, icon):
        frame = ctk.CTkFrame(self.block_container, corner_radius=12, fg_color="#22252e")
        frame.pack(fill="x", pady=6, padx=15)

        # --- Icono ---
        img_label = ctk.CTkLabel(frame, image=icon, text="")
        img_label.pack(side="left", padx=10, pady=8)

        # --- Entrada para segundos ---
        entry = ctk.CTkEntry(frame, width=60, placeholder_text="seg")
        entry.insert(0, "1")
        entry.pack(side="left", padx=10)

        # --- Botón borrar ---
        del_btn = ctk.CTkButton(frame, text="✖", width=34, height=34, fg_color="#a22424",
                                hover_color="#b93a3a")
        del_btn.pack(side="right", padx=8, pady=6)

        # --- Guardar información ---
        block_info = {
            "frame": frame,
            "type": block_type,
            "name": name,
            "icon": icon,
            "entry": entry,
            "config": {"time": 1.0},
        }

        del_btn.configure(command=lambda b=block_info: self.remove_block(b))
        entry.bind("<KeyRelease>", lambda e, b=block_info: self.update_block_time(b))

        self.blocks.append(block_info)

    def update_block_time(self, block):
        """Actualiza el valor del tiempo configurado."""
        text = block["entry"].get().strip()
        try:
            block["config"]["time"] = float(text) if text else 1.0
        except ValueError:
            block["config"]["time"] = 1.0

    # =========================
    # ELIMINAR Y LIMPIAR BLOQUES
    # =========================
    def remove_block(self, block_or_frame):
        if isinstance(block_or_frame, dict):
            frame = block_or_frame.get("frame")
        else:
            frame = block_or_frame

        if frame:
            try:
                frame.destroy()
            except:
                pass
        self.blocks = [b for b in self.blocks if b["frame"] != frame]

    def clear_sequence(self):
        for block in self.blocks:
            block["frame"].destroy()
        self.blocks.clear()

    # =========================
    # EJECUTAR SECUENCIA REAL
    # =========================
    def start_sequence(self):
        """Ejecuta la secuencia de comandos en el dispositivo BLE conectado"""
        if not self.blocks:
            messagebox.showwarning("Sin bloques", "No hay bloques en la secuencia.")
            return

        if not self.connected_device:
            messagebox.showwarning("Sin conexión", "No hay ningún dispositivo Bluetooth conectado.")
            return

        self.stop_execution = False
        threading.Thread(target=lambda: asyncio.run(self.execute_sequence()), daemon=True).start()

    def stop_sequence(self):
        """Detiene la ejecución de la secuencia"""
        self.stop_execution = True
        # Enviar comando de parada al dispositivo
        threading.Thread(target=lambda: asyncio.run(self.send_stop_command()), daemon=True).start()

    async def execute_sequence(self):
        """Ejecuta la secuencia de comandos en el dispositivo BLE"""
        try:
            for block in self.blocks:
                if self.stop_execution:
                    break

                # Resaltar bloque actual
                self.after(0, lambda b=block: self.highlight_block(b))

                # Obtener comando y duración
                command = block["type"]
                duration = block["config"].get("time", 1.0)

                # Enviar comando al dispositivo BLE
                success = await ble.send_command(command, duration)
                
                if not success:
                    self.after(0, lambda: messagebox.showerror("Error", f"Error al enviar comando: {command}"))
                    break

                # Quitar resaltado
                self.after(0, lambda b=block: self.unhighlight_block(b))

            if not self.stop_execution:
                self.after(0, lambda: messagebox.showinfo("Ejecución", "Secuencia ejecutada correctamente"))
            else:
                self.after(0, lambda: messagebox.showinfo("Ejecución", "Secuencia detenida"))

        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: messagebox.showerror("Error", f"Error en ejecución: {error_msg}"))

    async def send_stop_command(self):
        """Envía comando de parada al dispositivo"""
        try:
            await ble.send_command("stop", 0)
        except Exception as e:
            print(f"Error enviando comando de parada: {e}")

    def highlight_block(self, block):
        """Resalta el bloque que se está ejecutando"""
        block["frame"].configure(fg_color="#355a9a")
        self.update()

    def unhighlight_block(self, block):
        """Quita el resaltado del bloque"""
        block["frame"].configure(fg_color="#22252e")
        self.update()

    def on_close(self):
        """Maneja el cierre de la aplicación"""
        # Desconectar Bluetooth al cerrar
        if self.connected_device:
            threading.Thread(target=lambda: asyncio.run(ble.disconnect_device()), daemon=True).start()
        self.destroy()

    # =========================
    # PANEL BLUETOOTH METHODS
    # =========================
    def toggle_bluetooth_panel(self):
        """Abre o cierra el panel lateral Bluetooth."""
        if not self.bluetooth_visible:
            self.bluetooth_panel.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")
            self.bluetooth_visible = True
        else:
            self.bluetooth_panel.place_forget()
            self.bluetooth_visible = False

    def start_ble_scan(self):
        """Inicia la búsqueda de dispositivos BLE (en hilo separado)."""
        # Limpiar lista actual
        for widget in self.device_container.winfo_children():
            widget.destroy()

        loading_label = ctk.CTkLabel(
            self.device_container,
            text="Buscando dispositivos BLE...",
            font=("Arial", 14, "italic"),
            text_color="#7a7a7a",
        )
        loading_label.pack(pady=15)

        # Escanear en un hilo separado
        threading.Thread(target=lambda: asyncio.run(self.perform_ble_scan()), daemon=True).start()

    async def perform_ble_scan(self):
        """Escanea dispositivos BLE reales y los muestra."""
        try:
            devices = await ble.scan_devices()
            self.after(0, lambda: self.show_ble_devices(devices))

        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.show_ble_error(error_msg))

    def show_ble_devices(self, devices):
        """Muestra la lista de dispositivos BLE en el panel."""
        for w in self.device_container.winfo_children():
            w.destroy()

        if not devices:
            no_devices = ctk.CTkLabel(
                self.device_container,
                text="No se detectaron dispositivos BLE.",
                font=("Arial", 13),
                text_color="#9e9e9e",
            )
            no_devices.pack(pady=10)
            return

        for name, address in devices:
            device_button_frame = ctk.CTkFrame(
                self.device_container, fg_color="#1e2130", corner_radius=8
            )
            device_button_frame.pack(fill="x", pady=6, padx=6)

            lbl = ctk.CTkLabel(device_button_frame, text=f"{name}", anchor="w", font=("Arial", 13))
            lbl.pack(side="left", padx=8, pady=6)

            lbl_addr = ctk.CTkLabel(device_button_frame, text=f"{address}", anchor="w", font=("Arial", 10))
            lbl_addr.pack(side="left", padx=6)

            btn_connect = ctk.CTkButton(
                device_button_frame,
                text="Conectar",
                width=90,
                height=30,
                fg_color="#2758ad",
                hover_color="#3b6dd1",
                command=lambda a=address, n=name: threading.Thread(
                    target=lambda: asyncio.run(self.connect_ble_device(a, n)), daemon=True
                ).start(),
            )
            btn_connect.pack(side="right", padx=8, pady=6)

    def show_ble_error(self, message):
        """Muestra un mensaje de error en el panel BLE."""
        for w in self.device_container.winfo_children():
            w.destroy()
        error_label = ctk.CTkLabel(
            self.device_container,
            text=f"Error escaneando BLE: {message}",
            font=("Arial", 12),
            text_color="#ff5555",
        )
        error_label.pack(pady=15)

    async def connect_ble_device(self, address, name):
        """Conecta al dispositivo BLE seleccionado."""
        try:
            connected = await ble.connect_device(address)
            if connected:
                self.connected_device = (name, address)
                self.after(0, lambda: messagebox.showinfo("Bluetooth", f"Conectado a {name} ({address})"))
            else:
                self.after(0, lambda: messagebox.showerror("Bluetooth", f"No se pudo conectar a {name}"))
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: messagebox.showerror("Bluetooth", f"Error de conexión: {error_msg}"))


if __name__ == "__main__":
    app = BlockApp()
    app.mainloop()