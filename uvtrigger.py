import RPi.GPIO as GPIO
import time
from array import array

lightPin = 16 # 16 -> GPIO23
txPin = 12 # 12 (GPIO18) is the only PWM pin on the Raspi
rxPin = 22 # 22 -> GPIO25

newLightPin = 32 # 32 0> GPIO12

newPin = 40 # 40 -> GPIO21

# GPIO24 -> 18

#GPIO.cleanup()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(lightPin, GPIO.IN)
GPIO.setup(rxPin, GPIO.IN)

GPIO.setup(txPin, GPIO.OUT)

GPIO.setup(newPin, GPIO.OUT)

def measureLightCharge():
    # don't charge the capacitor
    GPIO.setup(newLightPin, GPIO.OUT)
    GPIO.output(newLightPin, GPIO.LOW)
    time.sleep(0.1) 

    # charge and measure the capacitor

    GPIO.setup(newLightPin, GPIO.IN)

    count = 0
    while GPIO.input(newLightPin) == GPIO.LOW:
        count += 1

    return count

#GPIO.output(newPin, GPIO.LOW)

def transmitter(enabled):
    if enabled:
        GPIO.setup(txPin, GPIO.OUT)
        GPIO.output(newPin, GPIO.LOW)
    else:
        #GPIO.output(newPin, GPIO.HIGH)
        GPIO.setup(txPin, GPIO.IN)


TX_FREQ = 40000
#p = GPIO.PWM(txPin, TX_FREQ)

TIMES_TO_RETRANSMIT = 30

capturing = False
capturingStart = 0

def ircallback(channel):
    if capturing == False:
        capturing = True
        capturingStart = time.perf_counter_ns()

    #print()

#def measureSequence():

#GPIO.add_event_detect(rxPin, GPIO.FALLING, callback=ircallback)

def msToUs(ms):
    return ms * 1000

def usToNs(us):
    return us * 1000

# in microseconds(us)
SONY_UNIT = 600
SONY_HEADER_MARK = SONY_UNIT * 4 # 2400us
SONY_ONE_MARK = SONY_UNIT * 2 # 1200us
SONY_ZERO_MARK = SONY_UNIT
SONY_SPACE = SONY_UNIT
SONY_REPEAT_SPACE = msToUs(10) # 10ms

def nsdelay(ns):
    curtime = time.perf_counter_ns()
    endtime = curtime + ns
    while curtime < endtime:
        curtime = time.perf_counter_ns()

def nsdelaypwm(ns):
    curtime = time.perf_counter_ns()
    endtime = curtime + ns

    dens = int((1000.0 * 1000.0) / TX_FREQ / 2.0) # 50% duty cycle

    while curtime < endtime:      
        GPIO.output(txPin, GPIO.HIGH)
        nsdelay(dens)

        GPIO.output(txPin, GPIO.LOW)
        nsdelay(dens)

        curtime = time.perf_counter_ns()

def nsdelaypwm2(ns):
    dens = TX_FREQ / 1000 / 2 # 50% duty cycle

    its = int(ns / TX_FREQ)

    for i in range(0, its): 
        GPIO.output(txPin, GPIO.HIGH)
        nsdelay(dens)

        GPIO.output(txPin, GPIO.LOW)
        nsdelay(dens)

def usdelay(us):
    nsdelay(usToNs(us))

def mark(m_us):
    #p.start(100.0)
    #GPIO.output(txPin, GPIO.HIGH)
    #usdelay(m_us)
    nsdelaypwm(usToNs(m_us))
    #p.stop()
    GPIO.output(txPin, GPIO.LOW)

def space():
    usdelay(SONY_SPACE)

def one():
    mark(SONY_ONE_MARK)
    space()

def zero():
    mark(SONY_ZERO_MARK)
    space()

def triggerShutter():
    for i in range(0, TIMES_TO_RETRANSMIT):
        mark(SONY_HEADER_MARK)
        space()

        # command (7 bits)
        one()
        zero()
        one()
        one()
        zero()
        one()
        zero()

        #address (5 bits)
        zero()
        one()
        zero()
        one()
        one()

        #extra (8 bits)
        one()
        zero()
        zero()
        zero()
        one()
        one()
        one()
        one()


        #mark(SONY_REPEAT_SPACE)
        #GPIO.output(txPin, GPIO.LOW)
        usdelay(SONY_REPEAT_SPACE)

def testLoop():
    while True:
        triggerShutter()
        time.sleep(1.0)

def runTriggerRemote():
    oldLightVal = 999

    while True:
        # lightVal = GPIO.input(lightPin)
        # if oldLightVal == lightVal:
        #     continue

        # print(lightVal)
        # oldLightVal = lightVal

        # shouldTrigger = lightVal == 0

        lightCharge = measureLightCharge()

        shouldTrigger = lightCharge < 2000

        if shouldTrigger:
            time.sleep(1.0)
            triggerShutter()

        #if lightVal == 0:
           #transmitter(True)
        #else:
           #transmitter(False)
        #GPIO.output(newPin, GPIO.LOW)
        
        # GPIO.output(newPin, GPIO.HIGH)
        # time.sleep(1.0)
        # GPIO.output(newPin, GPIO.LOW)
        # time.sleep(2.0)

        # GPIO.output(newPin, GPIO.HIGH)
        # time.sleep(5.0)

runTriggerRemote()


while True:
#    lightVal = GPIO.input(lightPin)
#    print(lightVal)

    #irVal = GPIO.input(rxPin)
    #print(irVal)

#    if lightVal == 0:
#        GPIO.output(txPin, GPIO.HIGH)
#    else:
#        GPIO.output(txPin, GPIO.LOW)

    #captime = 0

    elaptime = 0
    # in milliseconds, so 500 is 0.5 seconds
    ELAP_TIMEOUT_MS = 500

    MAX_PULSES = 1000
    pulses = array('Q')
    curPulse = 0

   # wait for the first major change
    GPIO.wait_for_edge(rxPin, GPIO.BOTH)

    while True:
        captime = time.perf_counter_ns()
        chan = GPIO.wait_for_edge(rxPin, GPIO.BOTH, timeout=ELAP_TIMEOUT_MS)
        
        # Did the timeout occur? If so, finish collecting data
        if chan is None:
            break
        
        elaptime = time.perf_counter_ns() - captime
        
        pulses.append(elaptime)
        curPulse += 1
        #print(elaptime)

    print(pulses)
    time.sleep(1.0)

    for i in range(0, 5):
        #p.start(100.0)
        #GPIO.output(txPin, GPIO.HIGH)

        highLow = 0
        for ptime in pulses:        
            if highLow:
                p.start(50.0)
                #GPIO.output(txPin, GPIO.HIGH)
            else:
                p.stop()   
                #GPIO.output(txPin, GPIO.LOW)     
            
            highLow = not highLow
            
            curtime = time.perf_counter_ns()
            endtime = curtime + ptime
            #GPIO.output(txPin, GPIO.HIGH)

            while curtime < endtime:
                curtime = time.perf_counter_ns()
            #GPIO.output(txPin, GPIO.LOW)
            #p.stop()
            #GPIO.output(txPin, GPIO.LOW)

        p.stop()
        #GPIO.output(txPin, GPIO.LOW)

        time.sleep(1.0)


#    time.sleep(0.01)
#    time.usleep(10000)



# print("Hello World")
