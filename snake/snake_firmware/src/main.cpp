 #include <Arduino.h>

// GPIO pins for the four buttons
const int UP_PIN = 1;
const int DOWN_PIN = 2;
const int LEFT_PIN = 3;
const int RIGHT_PIN = 21;

const int BUTTON_COUNT = 4;

const int buttonPins[BUTTON_COUNT] = {
    UP_PIN,
    DOWN_PIN,
    LEFT_PIN,
    RIGHT_PIN
};

const char* buttonCommands[BUTTON_COUNT] = {
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT"
};

// INPUT_PULLUP means:
// HIGH = button released
// LOW  = button pressed
int previousStates[BUTTON_COUNT] = {
    HIGH, HIGH, HIGH, HIGH
};

void setup() {
    Serial.begin(115200);

    for (int i = 0; i < BUTTON_COUNT; i++) {
        pinMode(buttonPins[i], INPUT_PULLUP);
    }

    Serial.println("ESP32 Snake controller ready!");
}

void loop() {
    for (int i = 0; i < BUTTON_COUNT; i++) {
        int currentState = digitalRead(buttonPins[i]);

        // Send a command only when the button is first pressed
        if (currentState == LOW && previousStates[i] == HIGH) {
            Serial.println(buttonCommands[i]);
        }

        previousStates[i] = currentState;
    }

    // Small delay to reduce switch bounce
    delay(20);
}
