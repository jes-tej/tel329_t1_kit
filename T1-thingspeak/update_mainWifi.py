
import machine  # For interfacing with hardware components like ADC
import utime    # For time-related functions, such as sleep
import network
import time
import os
import urequests
 
# Initialize the ADC (Analog to Digital Converter) on pin 26 for reading LM35 temperature sensor
LM35 = machine.ADC(26)
 
# Define a calibration offset value. This is determined through practical testing to correct systematic error.
Cal_Offset = -2400
 
# Function to compute temperature from the averaged analog readings
def Compute_Temp(Avg_A):
    # Add calibration adjustment to the average ADC value
    LM35_A = Avg_A + Cal_Offset
    # Convert the adjusted analog reading to voltage (assuming each ADC unit represents .00005 Volts)
    LM35_V = LM35_A * .00005
    # Convert the voltage to temperature in Celsius (since LM35 has a scale factor of 10mV/°C)
    Tmp_C = round((LM35_V * 100), 1)-36
    # Convert temperature from Celsius to Fahrenheit
    Tmp_F = round((Tmp_C * 1.8 + 32), 1)
    # Return both Celsius and Fahrenheit temperatures
    return Tmp_C, Tmp_F
 
# Initialize variables for accumulating samples and counting the number of samples
Samples = 0
Num_Samples = 1

ssid = 'fl4g{H0l4}' 
password = os.getenv('Password_wifi')

def ConnectWiFi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    print(wlan.ifconfig())

ConnectWiFi()

#ThingSpeak Initialization
server = "http://api.thingspeak.com/" 
apikey = os.getenv('THINGSPEAK_API_KEY_UTFSM')
api_key_personal = os.getenv('THINGSPEAK_API_KEY')
field = 6 #cambiar segun corresponda
field_personal=1
 
# Main loop to continuously read temperature
while True:
    # Check if fewer than 10 samples have been collected
    if Num_Samples <= 100:
        # Read the current temperature sensor value from the ADC
        LM35_A = LM35.read_u16()
        # Add the current reading to the total samples accumulator
        Samples += LM35_A
        # Increment the counter for the number of samples collected
        Num_Samples += 1
    else:
        # Calculate the average of the collected samples
        Avg_A = Samples / 100
        # Reset the samples accumulator and samples counter for the next batch of readings
        Samples = 0
        Num_Samples = 1
        # Compute the temperature in Celsius and Fahrenheit from the average ADC value
        T_c, T_f = Compute_Temp(Avg_A)
        # Print the calculated temperatures
        print(round(T_c))
        url = f"{server}/update?api_key={apikey}&field{field}={T_c}"
        url2 = f"{server}/update?api_key={api_key_personal}&field{field_personal}={T_c}"
        request = urequests.post(url)
        print("Se logra enviar data a ThingSpeak UTFSM:", request.status_code == 200)
        time.sleep(15)
        request2 = urequests.post(url2)
        print("Se logra enviar data a ThingSpeak Personal:", request2.status_code == 200)
        time.sleep(9)
        
        request.close()
        request2.close()
    
    
    # Wait for 0.1 seconds before the next loop iteration to limit the rate of temperature reading
    utime.sleep(.01)
