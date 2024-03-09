#include <stdio.h>
#include <stdbool.h>
#include <pigpio.h>

int lightPin = 12; // GPIO12 <-> 32

int measureLightCharge() {
    // Don't charge the capacitor (drain it)
    gpioSetMode(lightPin, PI_OUTPUT);
    gpioWrite(lightPin, PI_LOW);
    gpioDelay(200);

    // Charge and measure the capacitor
    gpioSetMode(lightPin, PI_INPUT);

    // Count how long it takes to transition from low to high
    int count = 0;
    while (gpioRead(lightPin) == PI_LOW) {
        count++;
    }

    return count;
}

void triggerShutter();

void main() {
    if (gpioInitialise() < 0) {
        printf("Could not initialize GPIO.");
        return;
    }

    printf("GPIO initialized.");

    bool shouldTrigger = false;
    int oldShouldTrigger = true;

    while (1) {
        int charge = measureLightCharge();

        //gpioSetMode(lightPin, PI_INPUT);
        //printf("Pin Value: %d\n", gpioRead(lightPin));
        // printf("Charge: %d\n", charge);
        // gpioDelay(100000);

        shouldTrigger = charge < 101000;

        // If it had already triggered, don't do it again
        if (shouldTrigger == oldShouldTrigger) {
            continue;
        }
        oldShouldTrigger = shouldTrigger;

        if (shouldTrigger) {
            printf("Triggered Charge: %d\n", charge);
            printf("Triggered Charge: %d\n", charge);
            triggerShutter();
        }
    }
}

int TX_FREQ = 40000;
int TIMES_TO_RETRANSMIT = 30;

#define msToUs(ms) ((ms) * 1000)
#define usToNs(us) ((us) * 1000)


// in microseconds(us)
const int SONY_UNIT = 600;
const int SONY_HEADER_MARK = SONY_UNIT * 4; // 2400us
const int SONY_ONE_MARK = SONY_UNIT * 2; // 1200us
const int SONY_ZERO_MARK = SONY_UNIT;
const int SONY_SPACE = SONY_UNIT;
const int SONY_REPEAT_SPACE = msToUs(10); // 10ms

void nsdelay(int ns) {

}


void nsdelaypwm(int ns) {

}

void space() {

}

void one() {

}

void zero() {

}

void triggerShutter() {
    for (int i = 0; i < TIMES_TO_RETRANSMIT; i++) {
        mark(SONY_HEADER_MARK);
        space();

        // command (7 bits)
        one();
        zero();
        one();
        one();
        zero();
        one();
        zero();

        // address (5 bits)
        zero();
        one();
        zero();
        one();
        one();

        // extra (8 bits)
        one();
        zero();
        zero();
        zero();
        one();
        one();
        one();
        one();


        // mark(SONY_REPEAT_SPACE)
        // GPIO.output(txPin, GPIO.LOW)
        usdelay(SONY_REPEAT_SPACE);
    }
}