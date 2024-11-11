# Final Code
import serial
import requests
import time
import logging
from decouple import config

# Configuración de logs
logging.basicConfig(
    filename='register_temp_final_local.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Configura el puerto serial (ajusta COM5 a tu puerto correcto)

# Configura el puerto serial
SERIAL_PORT = 'COM7'  # Cambia esto si usas Windows, usualmente COM3, COM4, etc.
BAUD_RATE = 115200  # Asegúrate de que coincida con el Pico
THINGSPEAK_API_KEY =config('THINGSPEAK_API_KEY')

THINGSPEAK_API_KEY_UTFSM = config('THINGSPEAK_API_KEY_UTFSM')

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Espera para estabilizar la conexión

def enviar_a_thingspeak(temperatura):
    url = f"https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}&field1={temperatura}"
    url_wsn = f"https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY_UTFSM}&field6={temperatura}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info("Datos enviados a ThingSpeak con éxito a Private Channel.")
            print("Datos enviados a ThingSpeak con éxito.")
        else:
            logging.error(f"Error al enviar datos a ThingSpeak: {response.status_code}")
            print(f"Error al enviar datos a ThingSpeak: {response.status_code}")

        time.sleep(3)

        response2 = requests.get(url_wsn)
        if response2.status_code == 200:
            logging.info("Datos enviados a ThingSpeak con éxito a UTFSM Labs TEL329.")
            print("Datos enviados a ThingSpeak con éxito a UTFSM Labs TEL329.")
        else:
            logging.error(f"Error al enviar datos a ThingSpeak (UTFSM): {response2.status_code}")
            print(f"Error al enviar datos a ThingSpeak (UTFSM): {response2.status_code}")
    except Exception as e:
        logging.exception("Excepción al enviar datos a ThingSpeak: %s", e)
        print("Error durante la solicitud HTTP:", e)

# Bucle principal para leer y enviar datos
try:
    while True:
        if ser.in_waiting > 0:
            linea = ser.readline().decode('utf-8').strip()
            if linea != None:
                temperatura = linea
                logging.info(f"Temperatura leída: {temperatura} °C")
                print(f"Temperatura leída: {temperatura} °C")
                enviar_a_thingspeak(temperatura)
                time.sleep(75)  # Respeta el límite de actualización de ThingSpeak (45 segundos mínimo) | (5*60)
            else:
                logging.info(f"Read Failed!")
                print(f"Read Failed!")
                continue



except KeyboardInterrupt:
    logging.info("Programa detenido por el usuario.")
    print("\nPrograma detenido por el usuario.")
finally:
    ser.close()
    logging.info("Conexión serial cerrada.")
    print("Conexión serial cerrada.")