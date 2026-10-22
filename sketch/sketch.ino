#include <Arduino.h>
#include <Arduino_RouterBridge.h>
#include <Servo.h>

Servo fireServo;
const int SERVO_PIN = 9;
const int MQ2_PIN = A0;
const int DHT22_PIN = 2; // Digital Pin D2 for DHT22

// DHT22 State
float dht_temperature = 25.0f;
float dht_humidity = 50.0f;
bool dht_has_reading = false;

// Read analog value from MQ-2 on A0
int read_mq2() {
    return analogRead(MQ2_PIN);
}

// Low-level safe DHT22 reading function (1-Wire protocol)
bool read_dht22(float &temp, float &hum) {
    uint8_t data[5] = {0, 0, 0, 0, 0};
    
    // 1. Send start signal to DHT22
    pinMode(DHT22_PIN, OUTPUT);
    digitalWrite(DHT22_PIN, LOW);
    delay(2); // Low for 2ms
    digitalWrite(DHT22_PIN, HIGH);
    delayMicroseconds(30);
    pinMode(DHT22_PIN, INPUT_PULLUP);

    // 2. Wait for DHT22 acknowledgment
    unsigned long timeout = micros();
    while (digitalRead(DHT22_PIN) == HIGH) {
        if (micros() - timeout > 200) return false;
    }
    timeout = micros();
    while (digitalRead(DHT22_PIN) == LOW) {
        if (micros() - timeout > 200) return false;
    }
    timeout = micros();
    while (digitalRead(DHT22_PIN) == HIGH) {
        if (micros() - timeout > 200) return false;
    }

    // 3. Read 40 bits of data
    for (int i = 0; i < 40; i++) {
        timeout = micros();
        while (digitalRead(DHT22_PIN) == LOW) {
            if (micros() - timeout > 200) return false;
        }

        unsigned long high_start = micros();
        timeout = micros();
        while (digitalRead(DHT22_PIN) == HIGH) {
            if (micros() - timeout > 200) return false;
        }
        unsigned long high_duration = micros() - high_start;

        int byte_idx = i / 8;
        data[byte_idx] <<= 1;
        // In DHT22, 26-28us is 0, ~70us is 1
        if (high_duration > 45) {
            data[byte_idx] |= 1;
        }
    }

    // 4. Validate checksum
    if (data[4] != ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) {
        return false;
    }

    // 5. Convert bytes to Humidity and Temperature
    float h = ((data[0] << 8) | data[1]) * 0.1f;
    float t;
    if (data[2] & 0x80) {
        t = -(((data[2] & 0x7F) << 8) | data[3]) * 0.1f;
    } else {
        t = ((data[2] << 8) | data[3]) * 0.1f;
    }

    // Range validity check
    if (h >= 0.0f && h <= 100.0f && t >= -40.0f && t <= 80.0f) {
        temp = t;
        hum = h;
        return true;
    }
    return false;
}

float read_dht_temp() {
    return dht_temperature;
}

float read_dht_hum() {
    return dht_humidity;
}

// Set servo angle dynamically (attaches only when needed)
void set_servo(int angle) {
    if (angle < 0) {
        // Disconnect PWM to prevent any jittering
        if (fireServo.attached()) {
            fireServo.detach();
        }
        return;
    }
    if (angle > 180) angle = 180;
    if (!fireServo.attached()) {
        fireServo.attach(SERVO_PIN);
    }
    fireServo.write(angle);
}

// Explicit detach method to kill PWM pulses completely
void detach_servo() {
    if (fireServo.attached()) {
        fireServo.detach();
    }
}

void setup() {
    // Start communication bridge with Qualcomm MPU
    Bridge.begin();
    
    // IMPORTANT: Do NOT attach servo in setup() to avoid idle jittering/humming
    // Servo will only be attached dynamically when fire is detected.
    
    Bridge.provide("read_mq2", read_mq2);
    Bridge.provide("read_dht_temp", read_dht_temp);
    Bridge.provide("read_dht_hum", read_dht_hum);
    Bridge.provide("set_servo", set_servo);
    Bridge.provide("detach_servo", detach_servo);
}

void loop() {
    // Stream MQ-2 reading to Python side every 200ms
    static unsigned long last_mq2_time = 0;
    if (millis() - last_mq2_time >= 200) {
        last_mq2_time = millis();
        int mq2_raw = analogRead(MQ2_PIN);
        Bridge.notify("mq2_data", mq2_raw);
    }

    // Stream DHT-22 reading to Python side every 2500ms (max rate for DHT22)
    static unsigned long last_dht_time = 0;
    if (millis() - last_dht_time >= 2500) {
        last_dht_time = millis();
        float t = 0.0f, h = 0.0f;
        if (read_dht22(t, h)) {
            dht_temperature = t;
            dht_humidity = h;
            dht_has_reading = true;
        }
        Bridge.notify("dht_temp", dht_temperature);
        Bridge.notify("dht_hum", dht_humidity);
    }
}
