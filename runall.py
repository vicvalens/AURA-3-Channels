import subprocess
import time

# Rutas de los códigos Python que deseas ejecutar
ruta_codigo0 = "4_LSL_3channel_Bandpower.py"
ruta_codigo1 = "main_EEG_Trigger_saver_EEG.py"
ruta_codigo2 = "TESTPragmatico.py"  # Este se mostrará en una terminal visible
ruta_codigo3 = "dummyBwell.py"

# Configurar STARTUPINFO para ocultar la ventana de terminal
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE

# Ejecutar código 0 sin mostrar la terminal
subprocess.Popen(["python", ruta_codigo0], startupinfo=startupinfo)
time.sleep(7)

# Ejecutar código 1 sin mostrar la terminal
subprocess.Popen(["python", ruta_codigo1], startupinfo=startupinfo)
time.sleep(2)

# Ejecutar código 2, manteniendo visible la terminal
subprocess.Popen(["start", "cmd", "/k", f"python {ruta_codigo2}"], shell=True)
time.sleep(2)

# Ejecutar código 3 sin mostrar la terminal
subprocess.Popen(["python", ruta_codigo3], startupinfo=startupinfo)
