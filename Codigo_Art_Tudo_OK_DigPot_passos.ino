const int CLK =10;

  const int UD = 11;
  const int CS = 12;
  float U = 4980; // VCC mV = total voltage
  float U1=0, U2=0; 
  float Ur=0; // queda de tensão no resistor de baixa resistência
  float Ul=0; // queda de tensão no diodo
  float I =0; // corrente total
float R_drop=200; // resistência do resistor de baixa resistência
int i = 1;

void setup() {
  Serial.begin(9600);
    pinMode(A0, INPUT); //setando entrada de dados
    pinMode(A1, INPUT);
    pinMode(CLK, OUTPUT);
    pinMode(UD, OUTPUT);
    pinMode(CS, OUTPUT);

    digitalWrite(CS, HIGH);

  delay(10);
}

void loop() {

  setToZero();

  while (i <= 128)  {
    digiPOT ();  
 
    U1 = float(analogRead(A0))/1023*U;  // transformando o dado A0 em tensão mV
    U2 = float(analogRead(A1))/1023*U;  

    Ur=U2-U1;     // tomando a ddp no resistor
    I=Ur/R_drop;  // obtendo a corrente pela lei de ohm
    Ul=U-U2; 

    plotagem_dados();
    i = i +1; 
    delay(10);
  }

}

void plotagem_dados () {
  //Serial.print(" U1 ");
  
  Serial.print(U1);
  Serial.print(" , "); //Serial.print(" U2 ");
  Serial.print(U2);
  Serial.print(" , ");  //Serial.print(" Queda de tensao no Resist: ");
  Serial.print(Ur);
  Serial.print(" , ");    //Serial.print(" Queda de tensão no led: ");
  Serial.print(Ul);
  Serial.print(" , ");    //Serial.print(" Corrente total: ");
  Serial.println(I);
 
  delay(10);

}

void setToZero() {
  digitalWrite(CS, LOW); // Habilita o potenciômetro
  digitalWrite(UD, HIGH); // Define a direção para baixo (decremento)

  for (int j = 0; j < 128; j++) { // Envia pulsos suficientes para garantir que chegue a 0
    digitalWrite(CLK, HIGH);
    delay(5); // Pequena espera para garantir a estabilidade do sinal
    digitalWrite(CLK, LOW);
    delay(5); // Pequena espera para garantir a estabilidade do sinal
  }

  digitalWrite(CS, HIGH); // Desabilita o potenciômetro
}

void digiPOT () {
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