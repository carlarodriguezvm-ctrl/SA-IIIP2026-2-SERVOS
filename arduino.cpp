#include <Servo.h>

Servo servo_posicional;
Servo servo_continuo;

void setup()
{
  // El servo de grados puede iniciar en 0°
  servo_posicional.attach(5);
  servo_posicional.write(0);  
  
  // El servo continuo debe iniciar en 90 para estar detenido
  servo_continuo.attach(6);
  servo_continuo.write(90); 

  Serial.begin(9600);
  Serial.println("Sistema de Servos Listo. Envie comandos (ej. P50, C0)");
}

void loop()
{
  if (Serial.available() > 0) {
    // Leer todo el mensaje hasta el salto de linea
    String entrada = Serial.readStringUntil('\n');
    entrada.trim(); // Elimina espacios en blanco y caracteres \r

    if (entrada.length() > 1) {
      char prefijo = entrada.charAt(0);           // Obtener la letra (A, B, G, C)
      int valor = entrada.substring(1).toInt();  // Obtener el numero despues de la letra

      // Validacion de rango
      if (valor >= 0 && valor <= 180) {
        
        // Comandos para Servo de Grados (180°)
        if (prefijo == 'P' || prefijo == 'p') {
          servo_posicional.write(valor);
          Serial.print("Servo Grados (180 deg) movido a: ");
          Serial.println(valor);
        }
        // Comandos para Servo Continuo
        else if (prefijo == 'C' || prefijo == 'c') {
          servo_continuo.write(valor);
          Serial.print("Servo Continuo ajustado a: ");
          Serial.println(valor);
        }
        else {
          Serial.println("Error: Prefijo desconocido. Use 'P' para 180 deg o 'C' para continuo.");
        }

      } else {
        Serial.println("Error: El valor debe estar en el rango de 0 a 180");
      }
    }
  }
}