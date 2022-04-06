#include <Arduino.h>
#include <unity.h>

extern "C"
{
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

    void youriMain();

    bool odd(int i);

    bool even(int i);

    int sommig(int i);

    int gcd(int a, int b);
}

unsigned int sommigReference(unsigned int n) // copied from the reader to use as reference
{
    unsigned int result = 0;
    while (n >= 1)
    {
        result += n;
        n--;
    }
    return result;
}

// Stolen from here https://en.wikipedia.org/wiki/Euclidean_algorithm
int euclidianGcd(int a, int b)
{
    while (a != b)
    {
        a > b ? a -= b : b -= a;
    }
    return a;
}

void testOdd()
{
    TEST_ASSERT_EQUAL(true, odd(5));
    TEST_ASSERT_EQUAL(true, odd(27));
    TEST_ASSERT_EQUAL(true, odd(1233));
    TEST_ASSERT_EQUAL(false, odd(0));
    TEST_ASSERT_EQUAL(false, odd(24));
    TEST_ASSERT_EQUAL(false, odd(1232));
}

void testEven()
{
    TEST_ASSERT_EQUAL(false, even(5));
    TEST_ASSERT_EQUAL(false, even(27));
    TEST_ASSERT_EQUAL(false, even(1233));
    TEST_ASSERT_EQUAL(true, even(0));
    TEST_ASSERT_EQUAL(true, even(24));
    TEST_ASSERT_EQUAL(true, even(1232));
}

void testSommig()
{
    for (int i = 0; i < 2000; i++)
    {
        TEST_ASSERT_EQUAL(sommigReference(i), sommig(i));
    }
}

void testGcd()
{
    TEST_ASSERT_EQUAL(euclidianGcd(25, 35), gcd(25, 35)); // a < b
    TEST_ASSERT_EQUAL(euclidianGcd(35, 25), gcd(35, 25)); // b > a
    TEST_ASSERT_EQUAL(gcd(25, 35), gcd(35, 25)); // make sure order of params doesn't matter
    TEST_ASSERT_EQUAL(euclidianGcd(7, 5), gcd(7, 5)); // prime numbers
    // negative numbers would go here, but I don't support those
}

void setup()
{
    serialBegin();       // Needed to be able to print to serial monitor
    Sleep(1000);
    UNITY_BEGIN();
    RUN_TEST(testOdd);
    RUN_TEST(testEven);
    RUN_TEST(testSommig);
    RUN_TEST(testGcd);
}

void loop()
{
    // Arduino gets big mad without this function
}