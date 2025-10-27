import asyncio
from bleak import BleakScanner, BleakClient

class BLEManager:
    def __init__(self):
        self.devices = []
        self.client = None
        # UUIDs comunes para dispositivos BLE (ajusta según tu dispositivo)
        self.service_uuid = "0000ffe0-0000-1000-8000-00805f9b34fb"
        self.char_uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"

    async def scan_devices(self):
        print("Escaneando dispositivos BLE...")
        self.devices = await BleakScanner.discover()
        return [(d.name or "Sin nombre", d.address) for d in self.devices]

    async def connect_device(self, address):
        print(f"Intentando conectar a {address}...")
        try:
            self.client = BleakClient(address)
            await self.client.connect()
            connected = await self.client.is_connected()
            if connected:
                print(f"Conectado a {address}")
            else:
                print(f"Falló la conexión con {address}")
            return connected
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False

    async def disconnect_device(self):
        """Desconecta del dispositivo BLE"""
        try:
            if self.client and await self.client.is_connected():
                await self.client.disconnect()
                print("Desconectado del dispositivo BLE.")
                return True
        except Exception as e:
            print(f"Error al desconectar: {e}")
        return False

    async def send_command(self, command, duration=0):
        """Envía comandos al dispositivo BLE"""
        if not self.client or not await self.client.is_connected():
            print("No hay dispositivo conectado")
            return False

        try:
            # Mapeo de comandos a caracteres
            command_map = {
                "move_forward": b"F",    # Adelante
                "move_backward": b"B",   # Atrás
                "move_left": b"L",       # Izquierda
                "move_right": b"R",      # Derecha
                #"rotate": b"T",          # Girar
                "stop": b"S",            # Detener
                "time": b"W",            # Esperar
                "speed": b"V"            # Velocidad
            }

            # Obtener el comando correspondiente
            cmd_byte = command_map.get(command, b"S")  # Por defecto Stop
            
            print(f"Enviando comando: {command} -> {cmd_byte}")
            
            # Enviar comando al dispositivo
            await self.client.write_gatt_char(self.char_uuid, cmd_byte)
            
            # Si es un comando de movimiento, esperar la duración
            if command in ["move_forward", "move_backward", "move_left", "move_right", "rotate"]:
                if duration > 0:
                    print(f"Ejecutando por {duration} segundos")
                    await asyncio.sleep(duration)
                    # Enviar comando de parada después del tiempo
                    await self.client.write_gatt_char(self.char_uuid, b"S")
                    print("Comando de parada enviado")
            
            return True
            
        except Exception as e:
            print(f"Error enviando comando {command}: {e}")
            return False