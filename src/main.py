import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image

# Configuración visual general
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BlockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Control Bluetooth - Bloques Configurables")
        self.geometry("1000x600")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # ---------------- ICONOS ----------------
        self.icons = {
            "up": ctk.CTkImage(light_image=Image.open("icons/up.png"), size=(30, 30)),
            "down": ctk.CTkImage(light_image=Image.open("icons/down.png"), size=(30, 30)),
            "left": ctk.CTkImage(light_image=Image.open("icons/left.png"), size=(30, 30)),
            "right": ctk.CTkImage(light_image=Image.open("icons/right.png"), size=(30, 30)),
            "rotate": ctk.CTkImage(light_image=Image.open("icons/rotate.png"), size=(40, 40)),
            "stop": ctk.CTkImage(light_image=Image.open("icons/stop.png"), size=(40, 40)),
            "wait": ctk.CTkImage(light_image=Image.open("icons/wait.png"), size=(40, 40)),
            "speed": ctk.CTkImage(light_image=Image.open("icons/speed.png"), size=(40, 40)),
            "bluetooth": ctk.CTkImage(light_image=Image.open("icons/bluetooth.png"), size=(25, 25)),
        }

        # ---------------- PANEL IZQUIERDO ----------------
        self.block_frame = ctk.CTkFrame(self, width=250)
        self.block_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.block_frame, text="Bloques disponibles", font=("Arial", 16, "bold")).pack(pady=5)

        # Lista de bloques disponibles
        self.available_blocks = [
            ("Adelante", "move_forward", self.icons["up"]),
            ("Atrás", "move_backward", self.icons["down"]),
            ("Izquierda", "move_left", self.icons["left"]),
            ("Derecha", "move_right", self.icons["right"]),
            ("Girar", "rotate", self.icons["rotate"]),
            ("Detener", "stop", self.icons["stop"]),
            ("Esperar", "wait", self.icons["wait"]),
            ("Velocidad", "speed", self.icons["speed"]),
        ]

        # Crear botones de bloques
        for name, block_type, icon in self.available_blocks:
            btn = ctk.CTkButton(
                self.block_frame,
                text="",
                image=icon,
                fg_color="#1a1d29",
                hover_color="#2b2f3d",
                command=lambda n=name, t=block_type: self.add_block(n, t),
                height=50,
            )
            btn.pack(pady=4, fill="x")

        # ---------------- PANEL CENTRAL ----------------
        self.sequence_frame = ctk.CTkFrame(self)
        self.sequence_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Botón Bluetooth (esquina superior derecha)
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

        self.sequence_label = ctk.CTkLabel(
            self.sequence_frame, text="Secuencia de comandos", font=("Arial", 16, "bold")
        )
        self.sequence_label.pack(pady=5)

        self.block_container = ctk.CTkFrame(self.sequence_frame)
        self.block_container.pack(fill="both", expand=True, pady=10)

        # ---------------- BOTONES DE CONTROL ----------------
        self.run_button = ctk.CTkButton(
            self.sequence_frame, text="▶ Ejecutar Secuencia", command=self.execute_sequence
        )
        self.run_button.pack(pady=5)

        self.clear_button = ctk.CTkButton(
            self.sequence_frame, text="🗑 Limpiar Secuencia", command=self.clear_sequence
        )
        self.clear_button.pack(pady=5)

        # ---------------- PANEL BLUETOOTH OCULTO ----------------
        self.bluetooth_panel = None
        self.panel_visible = False

        # ---------------- LISTA DE BLOQUES ----------------
        self.blocks = []

    # =====================================================
    #        PANEL DESLIZABLE BLUETOOTH
    # =====================================================
    def toggle_bluetooth_panel(self):
        if self.panel_visible:
            if self.bluetooth_panel:
                self.bluetooth_panel.destroy()
                self.panel_visible = False
            return

        self.panel_visible = True
        self.bluetooth_panel = ctk.CTkFrame(self, width=250, corner_radius=10)
        self.bluetooth_panel.pack(side="right", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.bluetooth_panel, text="Dispositivos Bluetooth", font=("Arial", 16, "bold")).pack(pady=10)

        self.device_list = tk.Listbox(self.bluetooth_panel, bg="#1c1f2b", fg="white", relief="flat", height=10)
        self.device_list.pack(padx=10, pady=5, fill="both", expand=True)

        search_button = ctk.CTkButton(self.bluetooth_panel, text="🔍 Buscar dispositivos", command=self.search_devices)
        search_button.pack(pady=5)

        close_button = ctk.CTkButton(
            self.bluetooth_panel, text="❌ Cerrar", fg_color="red", hover_color="#b22c2c", command=self.close_bluetooth_panel
        )
        close_button.pack(pady=5)

    def close_bluetooth_panel(self):
        if self.bluetooth_panel:
            self.bluetooth_panel.destroy()
            self.panel_visible = False

    def search_devices(self):
        # Simulación de búsqueda de dispositivos
        self.device_list.delete(0, tk.END)
        fake_devices = ["HC-05 (Carro)", "ESP32-Bot", "BT-Control", "Arduino_BT"]
        for device in fake_devices:
            self.device_list.insert(tk.END, device)
        messagebox.showinfo("Bluetooth", "Búsqueda finalizada. Dispositivos encontrados ✅")

    # =====================================================
    #                AGREGAR BLOQUES
    # =====================================================
    def add_block(self, name, block_type):
        frame = ctk.CTkFrame(self.block_container, corner_radius=10)
        frame.pack(fill="x", pady=5, padx=10)

        label = ctk.CTkLabel(frame, text=name, font=("Arial", 14))
        label.pack(side="left", padx=10, pady=5)

        block_info = {"frame": frame, "type": block_type, "name": name, "label": label, "config": {}}

        if block_type in ["rotate", "stop", "wait", "speed"]:
            ctk.CTkButton(frame, text="⚙ Configurar", width=80, command=lambda b=block_info: self.configure_block(b)).pack(
                side="right", padx=5
            )

        ctk.CTkButton(frame, text="✖", width=30, fg_color="red", command=lambda f=frame: self.remove_block(f)).pack(
            side="right", padx=5
        )

        self.blocks.append(block_info)

    # =====================================================
    #                CONFIGURAR BLOQUES
    # =====================================================
    def configure_block(self, block):
        win = ctk.CTkToplevel(self)
        win.title(f"Configurar {block['name']}")
        win.geometry("300x200")

        t = block["type"]

        if t == "rotate":
            self.make_config(win, block, "Selecciona grados de giro:", "angle", ["45", "90", "180", "360"])
        elif t == "stop":
            self.make_entry(win, block, "Segundos para detenerse:", "duration", 1.0)
        elif t == "wait":
            self.make_entry(win, block, "Segundos para esperar:", "time", 1.0)
        elif t == "speed":
            self.make_entry(win, block, "Velocidad (1-100):", "speed", 50)

    def make_config(self, win, block, text, key, values):
        ctk.CTkLabel(win, text=text).pack(pady=10)
        value = tk.StringVar(value=block["config"].get(key, values[0]))
        combo = ctk.CTkComboBox(win, values=values, variable=value)
        combo.pack(pady=5)
        ctk.CTkButton(win, text="Guardar", command=lambda: self.save_config(block, {key: value.get()}, win)).pack(pady=10)

    def make_entry(self, win, block, text, key, default):
        ctk.CTkLabel(win, text=text).pack(pady=10)
        val = tk.DoubleVar(value=block["config"].get(key, default))
        entry = ctk.CTkEntry(win, textvariable=val)
        entry.pack(pady=5)
        ctk.CTkButton(win, text="Guardar", command=lambda: self.save_config(block, {key: val.get()}, win)).pack(pady=10)

    # =====================================================
    #                GUARDAR CONFIGURACIÓN
    # =====================================================
    def save_config(self, block, config, win):
        block["config"].update(config)
        win.destroy()

        text = block["name"]
        if block["type"] == "rotate":
            text += f" ({block['config']['angle']}°)"
        elif block["type"] == "stop":
            text += f" ({block['config']['duration']}s)"
        elif block["type"] == "wait":
            text += f" ({block['config']['time']}s)"
        elif block["type"] == "speed":
            text += f" ({block['config']['speed']}%)"

        block["label"].configure(text=text)
        messagebox.showinfo("Configurado", "Parámetros guardados correctamente ✅")

    # =====================================================
    #                ELIMINAR Y LIMPIAR
    # =====================================================
    def remove_block(self, frame):
        frame.destroy()
        self.blocks = [b for b in self.blocks if b["frame"] != frame]

    def clear_sequence(self):
        for block in self.blocks:
            block["frame"].destroy()
        self.blocks.clear()

    # =====================================================
    #                EJECUTAR SECUENCIA
    # =====================================================
    def execute_sequence(self):
        if not self.blocks:
            messagebox.showwarning("Sin bloques", "No hay bloques en la secuencia.")
            return

        result = "\n".join(f"{b['name']} → {b['config']}" for b in self.blocks)
        print(result)
        messagebox.showinfo("Ejecución", f"Secuencia ejecutada (modo simulado):\n\n{result}")

    def on_close(self):
        self.destroy()


if __name__ == "__main__":
    app = BlockApp()
    app.mainloop()
