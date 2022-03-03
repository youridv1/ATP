#include <Arduino.h>

extern "C"
{
  void youriMain();

  void serialBegin()
  {
    Serial.begin(9600);
  }

  void printStr(const char *str)
  {
    Serial.print(str);
  }

  void printlnStr(const char *str)
  {
    Serial.println(str);
  }

  void printInteger(int i)
  {
    Serial.print(i);
  }

  void printlnInteger(int i)
  {
    Serial.println(i);
  }

  int timeS()
  {
    return millis() / 1000;
  }

  int timeMs()
  {
    return millis();
  }

  int divide(int a, int b)
  {
    return a / b;
  }
}

void setup()
{
  serialBegin();       // Needed to be able to print to serial monitor
  printlnStr("Start"); // debug
  youriMain();         // start the code compiled by compiler.py
  printlnStr("End");   // debug
}

void loop()
{
  // Arduino gets big mad without this function
}