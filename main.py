import sys
import ttkbootstrap as ttk
from serial import Serial
from unittest.mock import MagicMock
import time
from ttkbootstrap.constants import *
import sty

MODO_SIMULACION = True  # CAMBIAR A False CUANDO TENGAS EL ARDUINO FÍSICO

puertoCom = "COM5" 

if not MODO_SIMULACION:
    # Conexión real con el Arduino físico
    arduino = Serial(port=puertoCom, baudrate=9600, timeout=1)
    time.sleep(2)
else:
    print("PROBANDO EN MODO SIMULACIÓN (Sin Arduino físico)")
    arduino = MagicMock()
    
    def simular_respuesta_arduino(comando_bytes):
        try:

            comando = comando_bytes.decode('utf-8').strip()
            
            if len(comando) > 1:
                prefijo = comando[0]
                valor_str = comando[1:]
                
                if valor_str.isdigit():
                    valor = int(valor_str)
                    
                    if 0 <= valor <= 180:
                        if prefijo in ['P', 'p']:
                            respuesta = f"MOCK: Servo Grados (180 deg) movido a: {valor}\n"
                        elif prefijo in ['C', 'c']:
                            respuesta = f"MOCK: Servo Continuo ajustado a: {valor}\n"
                        else:
                            respuesta = "MOCK: Error: Prefijo desconocido. Use 'P' para 180 deg o 'C' para continuo.\n"
                    else:
                        respuesta = "MOCK: Error: El valor debe estar en el rango de 0 a 180\n"
                else:
                    respuesta = "MOCK: Error: Formato de valor inválido\n"
            else:
                respuesta = "MOCK: Error: Comando muy corto\n"
                

            arduino.readline.return_value = respuesta.encode('utf-8')
            
        except Exception as e:
            arduino.readline.return_value = b"MOCK: Error en simulacion de comando\n"

    # Asociar la función al método write del mock
    arduino.write.side_effect = simular_respuesta_arduino
    
    # Simular un readline inicial por defecto
    arduino.readline.return_value = b"MOCK: Sistema de Servos Listo. Envie comandos (ej. P50, C0)\n"
    
app = ttk.Window(theme=sty.TEMA_VENTANA)
app.title("Proyecto 2 Servos")
app.geometry('1150x760')

style = ttk.Style()
style.configure(
    'Grande.TButton', 
    font=sty.FUENTE_BOTON,
    padding=sty.PADDING_BOTON,
    bootstyle=sty.BOOTSTYLE_BOTON
)

def enviar_comando_arduino(prefijo, valor):
    comando_str = f"{prefijo}{valor}\n"
    try:
        # Enviar los bytes al Arduino o al mock
        arduino.write(comando_str.encode('utf-8'))
        
        if MODO_SIMULACION:
            respuesta = arduino.readline().decode('utf-8').strip()
            print(f"Enviado [{comando_str.strip()}] -> Respuesta Arduino: {respuesta}")
        else:
            if arduino.in_waiting > 0:
                respuesta = arduino.readline().decode('utf-8').strip()
                print(f"Enviado [{comando_str.strip()}] -> Respuesta Arduino: {respuesta}")
                
    except Exception as e:
        print(f"Error al enviar comando serial: {e}")

# LABEL Y ENTRADA FIJAS (NO VAN A CAMBIAR)
frame_fijo = ttk.Frame(app) 
titulo = ttk.Label(frame_fijo, text=sty.TEXTO_TITULO, font=sty.FUENTE_TITULO, bootstyle=sty.BOOTSTYLE_TITULO)
titulo.pack(pady=sty.PAD_TITULO_Y, padx=sty.PAD_X)
titulo.pack_configure(anchor="center")

seleccion_servo = ttk.Combobox(
    frame_fijo,
    values=["Continuo", "Posicional"],
    state="readonly", # hace que no podamos modificar el combobox
    font=sty.FUENTE_ETIQUETA,
)

# FRAME CONTINUO
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

btn_C0 = ttk.Button(frame_botones_continuo, style='Grande.TButton', text="0", bootstyle=sty.BOOTSTYLE_BOTON,
                    command=lambda: valor_continuo(0))
btn_C0.pack(side=LEFT, padx=sty.PAD_X, pady=sty.PAD_Y)

btn_C90 = ttk.Button(frame_botones_continuo, style='Grande.TButton', text="90", bootstyle=sty.BOOTSTYLE_BOTON,
                    command=lambda: valor_continuo(90))
btn_C90.pack(side=LEFT, padx=sty.PAD_X, pady=sty.PAD_Y)

btn_C180 = ttk.Button(frame_botones_continuo, style='Grande.TButton', text="180", bootstyle=sty.BOOTSTYLE_BOTON,
                    command=lambda: valor_continuo(180))
btn_C180.pack(side=LEFT, padx=sty.PAD_X, pady=sty.PAD_Y)

def valor_continuo(val):
    entero = int(float(val))
    lbl_valor_actual_c.config(text=f"Valor actual: {entero}")
    enviar_comando_arduino('C', entero)

# FRAME POSICIONAL
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

# Función ejecutada al pulsar botones de posición rápida (0, 90, 180)
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

# Indicadores (0 y 180)
frame_marcas = ttk.Frame(frame_control_barra)
frame_marcas.pack(fill=X, padx=10)
lbl_min = ttk.Label(frame_marcas, text="0°", font=("Arial", 10, "bold"))
lbl_min.pack(side=LEFT)
lbl_max = ttk.Label(frame_marcas, text="180°", font=("Arial", 10, "bold"))
lbl_max.pack(side=RIGHT)

# Botones iguales que en el continuo
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

def cambiar_servo(event=None):
    servo_seleccionado = seleccion_servo.get()
    if servo_seleccionado == "Continuo":
        frame_posicional.pack_forget()
        frame_continuo.pack(fill=BOTH, expand=True, pady=sty.PAD_Y, padx=sty.PAD_X)
    elif servo_seleccionado == "Posicional":
        frame_continuo.pack_forget()
        frame_posicional.pack(fill=BOTH, expand=True, pady=sty.PAD_Y, padx=sty.PAD_X)

seleccion_servo.bind("<<ComboboxSelected>>", cambiar_servo)
seleccion_servo.pack(pady=sty.PAD_Y, padx=sty.PAD_X)
frame_fijo.pack(pady=sty.PAD_Y, padx=sty.PAD_X)

app.protocol("WM_DELETE_WINDOW", lambda: (arduino.close() 
                                        if arduino and arduino.is_open 
                                        else None, app.destroy(), sys.exit(0))) 

app.mainloop()