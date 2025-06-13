const int CLK = 10;

const int UD = 11;
const int CS = 12;
float R_drop = 200;  // resistance value of the shunt resistor.
float U = 4980;      // VCC mV = total voltage
float U1 = 0, U2 = 0, Ur = 0, Ud = 0, I = 0;
//U1 = Input voltage of the resistor;
//U2 = Output voltage of the resistor and Input voltage of the diode;
//Ur = voltage drop across the shunt resistor;
//Ud = voltage drop across diode;
//I = total current.

int i = 1;

void setup() {
  Serial.begin(9600);
  pinMode(A1, INPUT);    //Input of the resistor's output voltage value
  pinMode(A2, INPUT);    //Input of the resistor's input voltage value
  pinMode(CLK, OUTPUT);  //Output of the signal control for Clock.
  pinMode(UD, OUTPUT);   // Signal output to increase or decrease the variable resistance of the digital potenciometer.
  pinMode(CS, OUTPUT);   // Output of the signal control for CS.

  digitalWrite(CS, HIGH);  //Define CS to HIGH for avoiding changing resistance value for now.

  delay(10);
}

void loop() {

  setToZero();

  while (i <= 128) {  
  // Creating a loop of 128 steps to go from the lowest resistance value of the digital potentiometer to the highest,
  // collect data at each step, and plot it.

    digiPOT();  

    U1 = float(analogRead(A1)) / 1023 * U;  // Converting the signal in A1 for milliVolt.
    U2 = float(analogRead(A2)) / 1023 * U;  // Converting the signal in A2 for mV.

    Ur = U2 - U1;     // Calculaiting the voltage drop across shunt resistor.
    I = Ur / R_drop;  // Obtaining current using Ohm's Law.
    Ud = U - U2;      // Calculaiting the voltage drop across the diode.

    plotagem_dados();
    i = i + 1;
    delay(10);
  }
}

void plotagem_dados() {

  Serial.print(" U1 "); // Input voltage to the resistor.
  Serial.print(U1);

  Serial.print(" U2 ");  // Input voltage to the diode.
  Serial.print(U2);
  Serial.print(" R_DDP ");  // DDP across the resistor.
  Serial.print(Ur);
  Serial.print(" D_DDP ");  // DDP across the diode.
  Serial.print(Ud);
  Serial.print(" I ");  // I total.
  Serial.println(I);

  delay(10);
}

void setToZero() {
  digitalWrite(CS, LOW);   // Enable to variate Potenciometer.
  digitalWrite(UD, HIGH);  // Define to decrease resistence in Potenciometer.

  for (int j = 0; j < 128; j++) {  //Creates a 128-step loop to ensure that the digital potentiometer reaches its maximum resistance.
    digitalWrite(CLK, HIGH);
    delay(5);  
    digitalWrite(CLK, LOW);
    delay(5);  
  }

  digitalWrite(CS, HIGH);  // Disables the resistance change of the potentiometer.
}

void digiPOT() {    // Performs one step decreasing the resistance.
  digitalWrite(CS, LOW); 
  delay(5);
  digitalWrite(UD, LOW);
  delay(5);
  digitalWrite(CLK, HIGH);
  delay(5);
  digitalWrite(CLK, LOW);
  delay(5);
  digitalWrite(CLK, HIGH);
  delay(5);
}