#include <Arduino.h>

extern "C"
{
    void serialBegin()
    {
        Serial.begin(9600);
    }

    void printlnStr(const char *str)
    {
        Serial.println(str);
    }

    void printlnInteger(int i)
    {
        Serial.println(i);
    }

    int divide(int a, int b)
    {
        return a / b;
    }

    void youriMain();
}

void setup()
{
    serialBegin();       // Needed to be able to print to serial monitor
    Sleep(1000);
    youriMain();
}

void loop()
{
    // Arduino gets big mad without this function
}