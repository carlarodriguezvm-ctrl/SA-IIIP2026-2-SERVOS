import sys
import time
from unittest.mock import MagicMock
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from serial import Serial
import serial.tools.list_ports
import sty

# --- VARIABLES GLOBALES DE ESTADO ---
arduino = None
modo_simulacion = True


def obtener_puertos_com():
    """Retorna una lista con los puertos COM disponibles en el sistema."""
    puertos = serial.tools.list_ports.comports()
    lista_puertos = [p.device for p in puertos]
    return lista_puertos if lista_puertos else ["No hay puertos"]


def simular_respuesta_arduino(comando_bytes):
    """Simula las respuestas del Arduino para el modo simulación."""
    try:
        comando = comando_bytes.decode('utf-8').strip()
        if len(comando) > 1:
            prefijo = comando[0]
            valor_str = comando[1:]
            if valor_str.isdigit():
                valor = int(valor_str)
                if 0 <= valor <= 180:
                    if prefijo in ['P', 'p']:
                        respuesta = f"MOCK: Servo Grados movido a: {valor}\n"
                    elif prefijo in ['C', 'c']:
                        respuesta = f"MOCK: Servo Continuo ajustado a: {valor}\n"
                    else:
                        respuesta = "MOCK: Error: Prefijo desconocido\n"
                else:
                    respuesta = "MOCK: Error: Rango fuera de 0-180\n"
            else:
                respuesta = "MOCK: Error: Valor no numérico\n"
        else:
            respuesta = "MOCK: Error: Comando corto\n"
        arduino.readline.return_value = respuesta.encode('utf-8')
    except Exception:
        arduino.readline.return_value = b"MOCK: Error en simulacion\n"


app = ttk.Window(theme=sty.TEMA_VENTANA)
app.title("Proyecto 2 Servos")
app.geometry('1150x940')

style = ttk.Style()
style.configure(
    'Grande.TButton', 
    font=sty.FUENTE_BOTON,
    padding=sty.PADDING_BOTON,
    bootstyle=sty.BOOTSTYLE_BOTON
)

def enviar_comando_arduino(prefijo, valor):
    global arduino, modo_simulacion
    if arduino is None:
        return
    
    comando_str = f"{prefijo}{valor}\n"
    try:
        arduino.write(comando_str.encode('utf-8'))
        if modo_simulacion:
            respuesta = arduino.readline().decode('utf-8').strip()
            print(f"Enviado [{comando_str.strip()}] -> Respuesta: {respuesta}")
        else:
            if arduino.in_waiting > 0:
                respuesta = arduino.readline().decode('utf-8').strip()
                print(f"Enviado [{comando_str.strip()}] -> Respuesta: {respuesta}")
    except Exception as e:
        print(f"Error en comunicación serial: {e}")

# ==========================================
# 1. FRAME FIJO (CONFIGURACIÓN DE CONEXIÓN Y TITULO)
# ==========================================
frame_fijo = ttk.Frame(app)

# Título Principal
titulo = ttk.Label(frame_fijo, text=sty.TEXTO_TITULO, font=sty.FUENTE_TITULO, bootstyle=sty.BOOTSTYLE_TITULO)
titulo.pack(pady=sty.PAD_TITULO_Y, padx=sty.PAD_X)

# --- Sección Modo de Uso / Conexión ---
frame_modo = ttk.Frame(frame_fijo)
frame_modo.pack(pady=5)

lbl_modo = ttk.Label(frame_modo, text="Modo de Uso:", font=sty.FUENTE_ETIQUETA)
lbl_modo.pack(side=LEFT, padx=5)

combo_modo = ttk.Combobox(
    frame_modo,
    values=["Simulación (Sin Arduino)", "Arduino Conectado"],
    state="readonly",
    font=sty.FUENTE_ETIQUETA,
    width=22
)
combo_modo.set("Simulación (Sin Arduino)")
combo_modo.pack(side=LEFT, padx=5)

lbl_puerto = ttk.Label(frame_modo, text="Puerto COM:", font=sty.FUENTE_ETIQUETA)

combo_puertos = ttk.Combobox(
    frame_modo,
    values=obtener_puertos_com(),
    state="readonly",
    font=sty.FUENTE_ETIQUETA,
    width=12
)

btn_refrescar_puertos = ttk.Button(
    frame_modo,
    text="🔄",
    bootstyle="outline-secondary",
    command=lambda: combo_puertos.config(values=obtener_puertos_com())
)

btn_conexion = ttk.Button(
    frame_modo,
    text="Conectar",
    bootstyle="success",
    command=lambda: toggle_conexion()
)
btn_conexion.pack(side=LEFT, padx=10)

# --- Selección de Tipo de Servo ---
frame_servo_select = ttk.Frame(frame_fijo)

lbl_tipo_servo = ttk.Label(frame_servo_select, text="Escoger Tipo de Servo:", font=sty.FUENTE_ETIQUETA)
lbl_tipo_servo.pack(side=LEFT, padx=5)

seleccion_servo = ttk.Combobox(
    frame_servo_select,
    values=["Continuo", "Posicional"],
    state="disabled",
    font=sty.FUENTE_ETIQUETA,
    width=15
)
seleccion_servo.pack(side=LEFT, padx=5)

# --- Botón de Terminar / Reiniciar Conexión ---
btn_desconectar = ttk.Button(
    frame_fijo,
    text="Terminar Conexión / Reiniciar",
    bootstyle="danger-outline",
    command=lambda: terminar_conexion()
)

frame_fijo.pack(pady=sty.PAD_Y, padx=sty.PAD_X)

# ==========================================
# 2. FRAME SERVO CONTINUO
# ==========================================
frame_continuo = ttk.Frame(app)
continuo_subtitulo = ttk.Label(
    frame_continuo, font=sty.FUENTE_SUBTITULO, text="Servo Continuo", bootstyle=sty.BOOTSTYLE_TITULO
)
continuo_subtitulo.pack(pady=sty.PAD_Y, padx=sty.PAD_X)

lbl_valor_actual_c = ttk.Label(
    frame_continuo, 
    text="Valor actual: 90", 
    font=("Arial", 12, "bold"),
    bootstyle="danger" 
)
lbl_valor_actual_c.pack(pady=(0, 3))

frame_botones_continuo = ttk.Frame(frame_continuo)
frame_botones_continuo.pack(anchor="center")

def valor_continuo(val):
    entero = int(float(val))
    lbl_valor_actual_c.config(text=f"Valor actual: {entero}")
    enviar_comando_arduino('C', entero)

btn_C0 = ttk.Button(frame_botones_continuo, style='Grande.TButton', text="0", bootstyle=sty.BOOTSTYLE_BOTON,
                    command=lambda: valor_continuo(0))
btn_C0.pack(side=LEFT, padx=sty.PAD_X, pady=sty.PAD_Y)

btn_C90 = ttk.Button(frame_botones_continuo, style='Grande.TButton', text="90", bootstyle=sty.BOOTSTYLE_BOTON,
                    command=lambda: valor_continuo(90))
btn_C90.pack(side=LEFT, padx=sty.PAD_X, pady=sty.PAD_Y)

btn_C180 = ttk.Button(frame_botones_continuo, style='Grande.TButton', text="180", bootstyle=sty.BOOTSTYLE_BOTON,
                    command=lambda: valor_continuo(180))
btn_C180.pack(side=LEFT, padx=sty.PAD_X, pady=sty.PAD_Y)

# ==========================================
# 3. FRAME SERVO POSICIONAL
# ==========================================
frame_posicional = ttk.Frame(app)

posicional_subtitulo = ttk.Label(
    frame_posicional, text="Servo Posicional (180°)", font=sty.FUENTE_SUBTITULO, bootstyle=sty.BOOTSTYLE_TITULO
)
posicional_subtitulo.pack(pady=(10, 5))

frame_control_barra = ttk.Frame(frame_posicional)
frame_control_barra.pack(fill=X, padx=40, pady=20)

lbl_valor_actual = ttk.Label(
    frame_control_barra, 
    text="Posición actual: 0°", 
    font=("Arial", 12, "bold"),
    bootstyle="danger"
)
lbl_valor_actual.pack(pady=(0, 10))

valor_slider = ttk.IntVar(value=0)

def al_mover_slider(val):
    entero = int(float(val))
    valor_slider.set(entero)
    lbl_valor_actual.config(text=f"Posición actual: {entero}°")
    enviar_comando_arduino('P', entero)

def posicionar_slider(val):
    valor_slider.set(val)
    al_mover_slider(val)

slide_P = ttk.Scale(
    frame_control_barra, 
    from_=0, 
    to=180, 
    orient=HORIZONTAL,
    variable=valor_slider,
    command=al_mover_slider,
    bootstyle="danger"
)
slide_P.pack(fill=X, padx=10, pady=5)

frame_marcas = ttk.Frame(frame_control_barra)
frame_marcas.pack(fill=X, padx=10)
lbl_min = ttk.Label(frame_marcas, text="0°", font=("Arial", 10, "bold"))
lbl_min.pack(side=LEFT)
lbl_max = ttk.Label(frame_marcas, text="180°", font=("Arial", 10, "bold"))
lbl_max.pack(side=RIGHT)

frame_botones_posicional = ttk.Frame(frame_posicional)
frame_botones_posicional.pack(anchor="center", pady=sty.PAD_Y)

btn_P0 = ttk.Button(frame_botones_posicional, style='Grande.TButton', text="0", bootstyle=sty.BOOTSTYLE_BOTON,
                    command=lambda: posicionar_slider(0))
btn_P0.pack(side=LEFT, padx=sty.PAD_X, pady=sty.PAD_Y)

btn_P90 = ttk.Button(frame_botones_posicional, style='Grande.TButton', text="90", bootstyle=sty.BOOTSTYLE_BOTON,
                     command=lambda: posicionar_slider(90))
btn_P90.pack(side=LEFT, padx=sty.PAD_X, pady=sty.PAD_Y)

btn_P180 = ttk.Button(frame_botones_posicional, style='Grande.TButton', text="180", bootstyle=sty.BOOTSTYLE_BOTON,
                      command=lambda: posicionar_slider(180))
btn_P180.pack(side=LEFT, padx=sty.PAD_X, pady=sty.PAD_Y)

# ==========================================
# LÓGICA DE CONTROL DE CONEXIÓN Y SERVO
# ==========================================
def al_cambiar_modo(event=None):
    if combo_modo.get() == "Arduino Conectado":
        lbl_puerto.pack(side=LEFT, padx=(15, 5))
        combo_puertos.config(values=obtener_puertos_com())
        combo_puertos.pack(side=LEFT, padx=5)
        btn_refrescar_puertos.pack(side=LEFT, padx=2)
    else:
        lbl_puerto.pack_forget()
        combo_puertos.pack_forget()
        btn_refrescar_puertos.pack_forget()

combo_modo.bind("<<ComboboxSelected>>", al_cambiar_modo)

def toggle_conexion():
    global arduino, modo_simulacion
    
    modo_sel = combo_modo.get()
    
    if modo_sel == "Simulación (Sin Arduino)":
        modo_simulacion = True
        arduino = MagicMock()
        arduino.write.side_effect = simular_respuesta_arduino
        arduino.readline.return_value = b"MOCK: Sistema Listo\n"
    else:
        puerto = combo_puertos.get()
        if not puerto or puerto == "No hay puertos":
            print("Seleccione un puerto COM válido.")
            return
        modo_simulacion = False
        try:
            arduino = Serial(port=puerto, baudrate=9600, timeout=1)
            time.sleep(2)
        except Exception as e:
            print(f"Error al abrir puerto {puerto}: {e}")
            return

    # Bloquear selectores de conexión
    combo_modo.config(state="disabled")
    combo_puertos.config(state="disabled")
    btn_refrescar_puertos.config(state="disabled")
    btn_conexion.config(state="disabled")
    
    # Mostrar opciones de servo
    frame_servo_select.pack(pady=10)
    seleccion_servo.config(state="readonly")
    btn_desconectar.pack(pady=10)

def terminar_conexion():
    global arduino
    if arduino is not None:
        try:
            if hasattr(arduino, 'close'):
                arduino.close()
        except Exception:
            pass
        arduino = None

    # Ocultar frames de servos
    frame_continuo.pack_forget()
    frame_posicional.pack_forget()
    frame_servo_select.pack_forget()
    btn_desconectar.pack_forget()
    
    # Restablecer valores
    seleccion_servo.set('')
    valor_slider.set(0)
    lbl_valor_actual.config(text="Posición actual: 0°")
    lbl_valor_actual_c.config(text="Valor actual: 90")
    
    # Rehabilitar controles de conexión
    combo_modo.config(state="readonly")
    combo_puertos.config(state="readonly")
    btn_refrescar_puertos.config(state="normal")
    btn_conexion.config(state="normal")

def cambiar_servo(event=None):
    servo_seleccionado = seleccion_servo.get()
    if servo_seleccionado == "Continuo":
        frame_posicional.pack_forget()
        frame_continuo.pack(fill=BOTH, expand=True, pady=sty.PAD_Y, padx=sty.PAD_X)
    elif servo_seleccionado == "Posicional":
        frame_continuo.pack_forget()
        frame_posicional.pack(fill=BOTH, expand=True, pady=sty.PAD_Y, padx=sty.PAD_X)

seleccion_servo.bind("<<ComboboxSelected>>", cambiar_servo)

app.protocol("WM_DELETE_WINDOW", lambda: (
    arduino.close() if arduino and hasattr(arduino, 'is_open') and arduino.is_open else None,
    app.destroy(),
    sys.exit(0)
))

app.mainloop()