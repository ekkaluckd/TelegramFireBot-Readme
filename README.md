# 🔥 TelegramFireBot: AI Fire & Smoke Safeguard System (Arduino UNO Q)

ระบบตรวจจับอัคคีภัยและควันอัจฉริยะแบบบูรณาการ ออกแบบและปรับแต่งสำหรับบอร์ด **Arduino UNO Q (Qualcomm Dragonwing QRB2210 + STM32U585)** ผ่านแพลตฟอร์ม **Arduino App Lab** พร้อมระบบแสดงผลและควบคุมผ่าน Web Dashboard แบบเรียลไทม์ และระบบแจ้งเตือนฉุกเฉินผ่าน Telegram Bot

> [!CAUTION]
> โปรเจกต์นี้เป็น **ระบบต้นแบบเพื่อการศึกษา/ทดลอง** ไม่ใช่อุปกรณ์แจ้งเหตุเพลิงไหม้ที่ผ่านการรับรองมาตรฐาน ห้ามใช้แทนระบบสัญญาณเตือนไฟไหม้จริง ค่า ppm ที่แสดงเป็น **ค่าประมาณจากสูตร** ไม่ได้ผ่านการสอบเทียบ (Calibration)

---

<a id="s1"></a>
## ⚡ Quick Start (เริ่มใช้งานเร็ว)

1. เตรียมอุปกรณ์ตาม [สิ่งที่ต้องเตรียม](#s2) และต่อสายตาม [ผังการต่อวงจร](#s10)
2. สร้าง Telegram Bot และหา Chat ID ตาม [การตั้งค่า Telegram Bot](#s3)
3. ใส่ `TELEGRAM_TOKEN` และ `TELEGRAM_CHAT_ID` ในบล็อก `USER CONFIGURATION` ของ `python/main.py`
4. Import โปรเจกต์เข้า Arduino App Lab ตาม [ขั้นตอนการ Import](#s17) แล้วกด **Run**
5. เปิด Web Dashboard จากลิงก์ที่ App Lab แสดง (ดู [เรื่องพอร์ต](#s13))
6. รอเซนเซอร์ MQ-2 อุ่นเครื่อง 3–5 นาที แล้วทดสอบ

---

## 📑 สารบัญ (Table of Contents)

0. [สิ่งที่ต้องเตรียม (Prerequisites)](#s2) · [การตั้งค่า Telegram Bot](#s3)
1. [ภาพรวมระบบและจุดเด่น (System Highlights)](#s4)
2. [สถาปัตยกรรมการทำงาน (System Architecture)](#s5)
   - [สถาปัตยกรรม Dual-Brain](#s6)
   - [การสื่อสารผ่าน Router Bridge](#s7)
   - [ระบบ Zero-Jitter Servo Control](#s8)
   - [การคำนวณระดับควัน MQ-2 เป็นหน่วย ppm](#s9)
3. [ผังการต่อวงจรและพินฮาร์ดแวร์ (Hardware Wiring & Pinout Guide)](#s10)
   - [ตารางการต่อสายอุปกรณ์](#s11)
   - [คำแนะนำและข้อควรระวังเรื่องแรงดันไฟฟ้าและเซนเซอร์](#s12)
4. [การแสดงผล Web Dashboard และการปรับเปลี่ยนค่าบนเว็บ (Web Interface & Live Controls)](#s13)
   - [องค์ประกอบหน้าจอแดชบอร์ด](#s14)
   - [การปรับเปลี่ยนค่าเกณฑ์แจ้งเตือนผ่านสไลเดอร์แบบ Real-time](#s15)
   - [กลไกการซิงค์ค่าระหว่าง Web Client และ Python Backend](#s16)
5. [ขั้นตอนการนำเข้าสู่ Arduino App Lab (Importing App Guide)](#s17)
   - [การเตรียมไฟล์และโครงสร้างโฟลเดอร์](#s18)
   - [ขั้นตอนการ Import ทีละขั้นตอน](#s19)
6. [การตั้งค่าให้แอปทำงานอัตโนมัติเมื่อเปิดเครื่อง (Autostart on Boot)](#s20)
   - [ขั้นตอนการเปิดใช้งาน Autostart](#s21)
   - [การนำไปติดตั้งใช้งานจริงแบบ Standalone](#s22)
7. [คู่มือการเปลี่ยนและอัปเดตโมเดล AI และปรับแต่ง Keyword (AI Model & Keyword Customization Guide)](#s23)
   - [ขั้นตอนที่ 1: ดาวน์โหลดโมเดลใหม่ เปลี่ยนชื่อเป็นชื่อเดิม แล้ววางทับ (วิธีแนะนำ: ง่ายที่สุด 100%)](#s24)
   - [ขั้นตอนที่ 2: กำหนด Keyword และธีมที่หัวโค้ด Python (แก้ที่เดียว เว็บเปลี่ยนตามทั้งหมด!)](#s25)
   - [ขั้นตอนที่ 3: (ทางเลือกเสริม) การเปลี่ยนชื่อแอปในการ์ดของ App Lab](#s26)
   - [ขั้นตอนที่ 4: การลบแอปเดิมและ Import ใหม่ใน App Lab เพื่อล้างแคช](#s27)
   - [กรณีพิเศษ: หากต้องการตั้งชื่อไฟล์โมเดลเป็นชื่ออื่นจริงๆ](#s28)
   - 🔧 [คู่มือเพิ่ม / เปลี่ยน / ถอดเซนเซอร์ (Sensor Customization Guide)](#s29)
8. [โครงสร้างไฟล์และโค้ดอย่างละเอียด (Project & Code Structure)](#s34)
9. [การปรับแต่งพารามิเตอร์ระบบในโค้ด (Advanced Configuration)](#s39)
10. [การแก้ปัญหาที่พบบ่อย (Troubleshooting & FAQ)](#s40)

---

<a id="s2"></a>
## 🧰 สิ่งที่ต้องเตรียม (Prerequisites)

| รายการ | รายละเอียด |
| :--- | :--- |
| บอร์ด | Arduino UNO Q |
| ซอฟต์แวร์ | Arduino App Lab (ติดตั้งบนคอมพิวเตอร์) |
| กล้อง | USB Webcam มาตรฐาน UVC |
| เซนเซอร์ควัน | โมดูล MQ-2 (มีขา AO) |
| เซนเซอร์อุณหภูมิ/ความชื้น | DHT-22 (แบบโมดูล 3 ขา หรือตัวเปล่า 4 ขา + ตัวต้านทาน 4.7k–10kΩ) |
| มอเตอร์ | Servo Motor ขนาดเล็ก (เช่น SG90 / MG90S) |
| อื่นๆ | ตัวต้านทาน 1kΩ + 2kΩ (วงจรแบ่งแรงดัน MQ-2), สายจัมเปอร์, Adapter 5V 3A (Type-C) |
| เครือข่าย | Wi-Fi ที่ออกอินเทอร์เน็ตได้ (ตั้งค่าเครือข่ายของบอร์ดผ่าน Arduino App Lab ตอนตั้งค่าบอร์ดครั้งแรก) |
| บัญชี | บัญชี Telegram และบัญชี [Edge Impulse](https://studio.edgeimpulse.com/) (กรณีต้องการเทรนโมเดลเอง) |

---

<a id="s3"></a>
## 🤖 การตั้งค่า Telegram Bot (Telegram Setup)

1. **สร้างบอท**: เปิด Telegram ค้นหา **@BotFather** → ส่งคำสั่ง `/newbot` → ตั้งชื่อและ username (ต้องลงท้ายด้วย `bot`) → จะได้ **Bot Token** รูปแบบ `123456789:AA...`
2. **เริ่มคุยกับบอท**: เปิดแชทกับบอทที่เพิ่งสร้าง แล้วกด **Start** (`/start`) — ถ้าไม่ทำขั้นนี้ บอทจะส่งข้อความหาคุณไม่ได้
   - ถ้าต้องการส่งเข้ากลุ่ม ให้เชิญบอทเข้ากลุ่มและพิมพ์ข้อความในกลุ่มหนึ่งครั้ง
3. **หา Chat ID**: เปิดเบราว์เซอร์ไปที่
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   ```
   มองหา `"chat":{"id": ...}` — ตัวเลขนั้นคือ Chat ID (ของกลุ่มจะขึ้นต้นด้วย `-`)
4. **ใส่ค่าในโค้ด** ที่บล็อก `USER CONFIGURATION` ใน `python/main.py`:
   ```python
   TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
   TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
   ```

> [!WARNING]
> **ห้ามอัปโหลด Bot Token ขึ้น GitHub หรือที่สาธารณะ** ใครที่ได้ Token ไปจะควบคุมบอทของคุณได้ หาก Token หลุด ให้ไปที่ @BotFather → `/revoke` เพื่อออก Token ใหม่ทันที

---

<a id="s4"></a>
## 🌟 ภาพรวมระบบและจุดเด่น (System Highlights)

- **AI Target Detection (Flexible Keyword)**: ตรวจจับวัตถุเป้าหมายด้วยโมเดลคอมพิวเตอร์วิชั่นของ Edge Impulse จากภาพสดผ่าน **USB Webcam** แสดงผลกรอบ Bounding Box พร้อมระบุเปอร์เซ็นต์ความมั่นใจ โดยสามารถกำหนด Keyword ของคลาสที่ต้องการตรวจจับได้ง่ายๆ ที่ส่วนหัวของโค้ด Python
- **MQ-2 Smoke Sensor (A0)**: อ่านค่าระดับควันจากเซนเซอร์ MQ-2 ขา A0 แบบความเร็วสูง แปลงสัญญาณทางกายภาพเป็นหน่วย **ppm (Parts Per Million)** ด้วยสมการ Log-Exponential
- **DHT-22 Climate & Ambient Monitor (Pin D2)**: อ่านค่าอุณหภูมิ (°C) และความชื้นสัมพัทธ์ (%) จากเซนเซอร์ DHT-22 ผ่านขาดิจิทัล Pin D2 แสดงผลแบบเรียลไทม์บนหน้าเว็บแดชบอร์ด และรายงานสภาพแวดล้อมประกอบในข้อความแจ้งเตือน Telegram (เพื่อแสดงค่าสภาพแวดล้อมเท่านั้น ไม่นำไปใช้ทริกเกอร์เตือนภัย)
- **Zero-Jitter Servo Actuator (Pin 9)**: ขับมอเตอร์เซอร์โวหมุน 90 องศาเพื่อจำลองการเปิดวาล์วฉีดสารดับเพลิงเป็นเวลา 10 วินาที หมุนกลับ 0 องศา และ **ตัดสัญญาณ PWM ทันที (`detach`)** ขณะสแตนด์บาย เพื่อแก้ปัญหามอเตอร์เซอร์โวสั่นกระตุกหรือเกิดเสียงฮัม 100%
- **Real-time Web Dashboard & Live Sliders**: หน้าจอเว็บมอนิเตอร์ระดับพรีเมียม สไตล์ Dark Glassmorphism สามารถ **ปรับแต่งเกณฑ์แจ้งเตือน (Thresholds) ผ่านสไลเดอร์บนหน้าเว็บได้ทันทีแบบ Real-time** โดยไม่ต้องหยุดหรือคอมไพล์โค้ดใหม่
- **Telegram Emergency Gateway**: แจ้งเตือนภัยทันทีผ่าน Telegram Bot พร้อมส่งภาพถ่ายเหตุการณ์ความละเอียดสูง (Snapshot with HUD Overlay), ข้อมูลระดับตรวจจับ, ข้อมูลอุณหภูมิ/ความชื้น, เวลาตามโซนประเทศไทย และพิกัด GPS แผนที่ Google Maps
- **Standalone Autostart Ready**: รองรับการตั้งค่าให้เปิดเครื่องแล้วรันระบบเองโดยอัตโนมัติ (Autostart) ทำให้ติดตั้งใช้งานเป็นตู้เตือนภัยอัจฉริยะแบบอิสระได้ทันที

---

<a id="s5"></a>
## 🏛️ สถาปัตยกรรมการทำงาน (System Architecture)

```mermaid
flowchart TD
    subgraph Hardware["🔌 ฮาร์ดแวร์ภายนอก (External Hardware)"]
        CAM["📷 USB Webcam"]
        MQ2["💨 เซนเซอร์ MQ-2 (A0)"]
        DHT22["🌡️ เซนเซอร์ DHT-22 (D2)"]
        SERVO["⚙️ Servo Motor (Pin 9)"]
    end

    subgraph MCU["⚡ STM32U585 Microcontroller (Zephyr RTOS)"]
        INO["sketch.ino"]
        MQ2_READER["analogRead(A0) ความเร็วสูง"]
        DHT_READER["Safe 1-Wire Read DHT-22 (D2)"]
        SERVO_CTRL["Dynamic Servo Attach/Detach"]
    end

    subgraph Bridge["🌉 Arduino Router Bridge (RPC & MsgPack)"]
        NOTIFY_MQ2["Bridge.notify('mq2_data') ทุก 200ms"]
        NOTIFY_DHT["Bridge.notify('dht_temp' & 'dht_hum') ทุก 2.5s"]
        RPC_SERVO["Bridge.provide('set_servo' & 'detach_servo')"]
    end

    subgraph MPU["🐧 Qualcomm Dragonwing QRB2210 (Linux MPU)"]
        MAIN["python/main.py"]
        CONFIG["USER CONFIGURATION (TARGET_LABEL)"]
        MODEL["Edge Impulse (.eim) Model Runner"]
        CONVERT["PPM Curve Converter"]
        SERVO_THREAD["ServoController (Thread แยก ไม่หน่วงกล้อง)"]
        TEL_GATEWAY["Telegram Alert Gateway (แนบ Temp/Hum)"]
    end

    subgraph Web["💻 Web Dashboard (Port 7000 / 8080)"]
        HTML["index.html (Dark Glassmorphism + Climate Panel)"]
        JS["app.js (Socket.IO Real-time Data Binding)"]
    end

    subgraph Cloud["📱 Cloud & Telegram Services"]
        TELEGRAM["🚨 Telegram App (แจ้งเตือนพร้อมภาพถ่าย Snapshot & Temp/Hum)"]
    end

    CAM -->|V4L2 /dev/video2| MAIN
    MAIN --> CONFIG --> MODEL
    MQ2 -->|Analog Signal| MQ2_READER
    DHT22 -->|1-Wire Digital| DHT_READER
    MQ2_READER --> INO
    DHT_READER --> INO
    INO --> NOTIFY_MQ2 --> MAIN
    INO --> NOTIFY_DHT --> MAIN
    MAIN --> CONVERT
    MAIN -->|RPC Call| RPC_SERVO --> SERVO_CTRL --> SERVO
    MAIN -->|Base64 Video & Telemetry & DHT22| JS
    JS <--> HTML
    JS -->|override_fire_th & override_smoke_th| MAIN
    MAIN -->|Send Photo & Caption| TEL_GATEWAY --> TELEGRAM
```

<a id="s6"></a>
### 1. สถาปัตยกรรม Dual-Brain
Arduino UNO Q รวมเอา 2 หน่วยประมวลผลไว้ในบอร์ดเดียวกัน:
1. **STM32U585 Microcontroller (MCU)**: ทำหน้าที่ควบคุมด้านฮาร์ดแวร์แบบ Real-time I/O ทั้งการสุ่มอ่านค่า Analog ADC ขา A0 และการส่งสัญญาณ PWM ความถี่สูงควบคุมมุมเซอร์โวที่ขา Pin 9
2. **Qualcomm Dragonwing QRB2210 Linux MPU**: หน่วยประมวลผลหลักบนระบบปฏิบัติการ Linux ทำหน้าที่รันโมเดล AI Computer Vision ของ Edge Impulse, วิเคราะห์เฟรมวิดีโอจากกล้อง USB ด้วย OpenCV, รัน Web Server (Socket.IO) และสื่อสารกับเครือข่ายอินเทอร์เน็ตเพื่อส่ง Telegram API

<a id="s7"></a>
### 2. การสื่อสารผ่าน Router Bridge
การแลกเปลี่ยนข้อมูลระหว่างโลกของ Linux และ MCU ทำงานผ่านไลบรารี `Arduino_RouterBridge`:
- **MCU $\rightarrow$ Linux (Stream Event)**: โค้ดฝั่ง MCU จะอ่านค่า Analog จากเซนเซอร์ MQ-2 และส่ง `Bridge.notify("mq2_data", raw)` ทุก 200ms และส่ง `dht_temp` / `dht_hum` ทุก 2.5 วินาที ให้โค้ด Python ฝั่ง Linux รับไปประมวลผลต่อ
- **Linux $\rightarrow$ MCU (Fallback Polling)**: เพื่อความทนทาน ฝั่ง Python ยังมีเธรด `sensor_polling_worker()` เรียก `Bridge.call("read_mq2")`, `read_dht_temp` และ `read_dht_hum` ซ้ำทุก 1 วินาที เผื่อกรณีที่ notify หลุด
- **Linux $\rightarrow$ MCU (RPC Call)**: สคริปต์ Python สั่งการเซอร์โวมอเตอร์ผ่าน `Bridge.call("set_servo", angle)` และ `Bridge.call("detach_servo")`

<a id="s8"></a>
### 3. ระบบ Zero-Jitter Servo Control
เซอร์โวมอเตอร์ทั่วไปหากได้รับสัญญาณ PWM 50Hz ค้างไว้แม้จะไม่ได้สั่งเคลื่อนที่ มักจะเกิดปัญหาเรื่อง **เสียงฮัม (Humming noise)** หรือมี **อาการสั่นกระตุก (Idle Jitter)** ตลอดเวลา ในระบบนี้จึงใช้เทคนิค **Dynamic Attach/Detach**:
1. **ขณะ Standby**: โค้ดสั่ง `fireServo.detach()` ดับสัญญาณ PWM ทำให้เซอร์โวนิ่งสนิท ไม่กินกระแส และไม่มีเสียงรบกวน
2. **เมื่อพบไฟ (Fire $\ge$ Threshold)**: สั่ง `fireServo.attach(9)` $\rightarrow$ หมุนไปที่ 90 องศา $\rightarrow$ ค้างไว้ 10 วินาทีเพื่อจำลองการฉีดดับเพลิง
3. **เมื่อครบเวลา**: สั่งหมุนกลับมาที่ 0 องศา $\rightarrow$ หน่วงเวลา 1.5 วินาทีให้มอเตอร์วิ่งเข้าตำแหน่งสมบูรณ์ $\rightarrow$ สั่ง `detach()` ปิดสัญญาณ PWM
4. **Cooldown 60 วินาที**: ป้องกันกลไกทำงานซ้ำซ้อนอย่างต่อเนื่อง หากครบ 60 วินาทีแล้วยังตรวจพบไฟอยู่ ระบบจะสั่งวนลูปทำงานซ้ำอัตโนมัติ

<a id="s9"></a>
### 4. การคำนวณระดับควัน MQ-2 เป็นหน่วย ppm
ฟังก์ชัน `raw_to_smoke_ppm(raw_val)` แปลงค่าดิบจาก Analog ADC (0–1023; ถ้าค่าเกิน 1023 จะถือว่าเป็น 12-bit และย่อสเกลจาก 0–4095 ให้อัตโนมัติ) เป็น **ค่าประมาณ** ความหนาแน่นของควันในหน่วย **ppm (Parts Per Million)**:
$$\text{ppm} = 50.0 \times \left(1.0 + \left(\frac{\text{raw}}{80.0}\right)^{1.8}\right)$$
- ค่า raw ≤ 20 จะถูกปัดเป็น 50 ppm และผลลัพธ์ถูกจำกัดไว้ที่ 50–10,000 ppm
- **อากาศบริสุทธิ์ (Clean Air)**: $\approx 50 - 150 \text{ ppm}$ (raw ~100 → ~110 ppm)
- **ควันจางๆ (Mild Smoke)**: $\approx 300 - 500 \text{ ppm}$ (raw ~300 → ~470 ppm)
- **ควันหนาแน่น (Dense Smoke / Fire Hazard)**: $\ge 600 \text{ ppm}$ (raw ~400 → ~740, raw ~800 → ~2,320 ppm)

> [!NOTE]
> สูตรนี้เป็นเส้นโค้งประมาณการเพื่อให้อ่านค่าง่าย **ไม่ได้สอบเทียบกับก๊าซอ้างอิงจริง** ค่าที่ได้จึงใช้เปรียบเทียบแนวโน้มและตั้งเกณฑ์แจ้งเตือน ไม่ควรใช้เป็นค่าวัดทางวิทยาศาสตร์

---

<a id="s10"></a>
## 🔌 ผังการต่อวงจรและพินฮาร์ดแวร์ (Hardware Wiring & Pinout Guide)

<a id="s11"></a>
### ตารางการต่อสายอุปกรณ์

| อุปกรณ์ | ขาบนตัวอุปกรณ์ | สีสายไฟมาตรฐาน | ขาบนบอร์ด Arduino UNO Q | คำอธิบายหน้าที่ |
| :--- | :--- | :--- | :--- | :--- |
| **เซนเซอร์ MQ-2** | **VCC** | สีแดง | **5V** | ขาจ่ายไฟเลี้ยงโมดูลเซนเซอร์ |
| | **GND** | สีดำ | **GND** | ขากราวด์ร่วมของระบบ |
| | **AO (Analog Out)** | สีเขียว / ขาว | **A0 (Analog In)** | สัญญาณแรงดันอนาล็อกระดับควัน/ก๊าซ |
| **เซนเซอร์ DHT-22** | **VCC (+)** | สีแดง | **3.3V หรือ 5V** | ขาจ่ายไฟเลี้ยงโมดูล (แนะนำ 3.3V ให้ตรงระดับ Logic) |
| | **DATA (Out)** | สีเหลือง / ขาว | **Pin 2 (D2)** | สัญญาณดิจิทัล 1-Wire อ่านค่าอุณหภูมิและความชื้น |
| | **GND (-)** | สีดำ / น้ำเงิน | **GND** | ขากราวด์ร่วมของระบบ |
| **Servo Motor** | **VCC** | สีแดง | **5V** | ขาจ่ายไฟเลี้ยงแกนมอเตอร์ |
| | **GND** | สีน้ำตาล / สีดำ | **GND** | ขากราวด์ร่วมของระบบ |
| | **Signal (PWM)** | สีส้ม / สีเหลือง | **Pin 9 (D9 / PWM)** | สัญญาณพัลส์ควบคุมองศาการหมุน |
| **USB Webcam** | **USB-A Plug** | สาย USB ดั้งเดิม | **USB Host Port** | เสียบเข้าช่องพอร์ต USB-A ของบอร์ด UNO Q |

<a id="s12"></a>
### คำแนะนำและข้อควรระวังเรื่องแรงดันไฟฟ้าและเซนเซอร์

> [!NOTE]
> **ข้อแนะนำสำหรับเซนเซอร์ DHT-22 (Pin D2):**
> 1. **การต่อสายไฟเลี้ยง:** แนะนำให้ต่อไฟเลี้ยงที่ขา **3.3V** ของบอร์ด Arduino UNO Q เพื่อให้สัญญาณดิจิทัลตรงกับระดับแรงดันของไมโครคอนโทรลเลอร์พอดี
> 2. **ตัวต้านทาน Pull-up:** หากใช้เซนเซอร์ DHT-22 แบบโมดูลสำเร็จรูป (มีแผ่นวงจร 3 ขา) ตัวต้านทาน Pull-up จะถูกบัดกรีอยู่บนบอร์ดแล้ว สามารถต่อเข้าขา D2 ได้ทันที แต่หากใช้ตัวถังสีขาว 4 ขาแบบเปล่าๆ ให้ต่อตัวต้านทาน $4.7\text{k}\Omega - 10\text{k}\Omega$ คั่นระหว่างขา DATA กับ VCC
> 3. **จุดประสงค์การทำงาน:** ค่าจาก DHT-22 มีไว้วัดและ**แสดงผลสภาพแวดล้อม (อุณหภูมิและความชื้น) บนหน้าเว็บ และแนบในข้อความ Telegram เพื่อเป็นข้อมูลอ้างอิงเท่านั้น** จะไม่มีผลต่อการกระตุ้นเตือนภัยหรือขับมอเตอร์เซอร์โว

> [!WARNING]
> **ข้อควรระวังเรื่องแรงดันไฟขา Analog (A0):**
> 1. ขา Analog A0–A5 บนบอร์ด Arduino UNO Q รองรับแรงดันอินพุตสูงสุดไม่เกิน **3.3V** 
> 2. บอร์ดโมดูล MQ-2 ทั่วไปที่ใช้ไฟเลี้ยง 5V อาจปล่อยแรงดันขา AO ออกมาได้สูงสุด 4–5V เมื่อเจอกลุ่มควันหนาแน่นมาก
> 3. **คำแนะนำในการติดตั้ง:**
>    - หมุนปรับตัวต้านทานปรับค่าได้ (Potentiometer สีฟ้า) บนตัวโมดูล MQ-2 เพื่อปรับระดับความไวให้อยู่ในย่านปลอดภัย
>    - หรือต่อวงจรแบ่งแรงดัน (Voltage Divider) โดยใช้ตัวต้านทาน $1\text{k}\Omega$ และ $2\text{k}\Omega$ คั่นก่อนเข้าขา A0
>
> **การวอร์มเซนเซอร์ (Burn-in Time):**
> เซนเซอร์ตระกูล MQ ทุกรุ่นมีขดลวดความร้อนภายใน เมื่อเสียบไฟใช้งานครั้งแรกจะต้องรอประมาณ **3–5 นาที** เพื่อให้เซนเซอร์อุ่นและอ่านค่าได้อย่างคงที่และแม่นยำ

---

<a id="s13"></a>
## 💻 การแสดงผล Web Dashboard และการปรับเปลี่ยนค่าบนเว็บ (Web Interface & Live Controls)

ระบบ TelegramFireBot มาพร้อมกับหน้าจอแดชบอร์ด **Web Dashboard** ควบคุมและแสดงผลแบบเรียลไทม์ผ่าน WebSocket (Socket.IO) ผ่าน Brick `arduino:web_ui`:
- เข้าใช้งานจากคอมพิวเตอร์หรือสมาร์ตโฟนผ่าน Wi-Fi วงเดียวกัน: `http://<IP_ของบอร์ด_UNO_Q>:<PORT>`

> [!NOTE]
> **เรื่องพอร์ต:** Brick `web_ui` ของ App Lab ใช้พอร์ต **`7000`** เป็นค่าเริ่มต้น ส่วน `app.yaml` ของโปรเจกต์นี้ประกาศพอร์ต **`8080`** ไว้ใน `ports:` วิธีที่แน่นอนที่สุดคือ **คลิกลิงก์ที่ App Lab แสดงหลังกด Run** หรือดูพอร์ตในหน้าต่าง Logs ถ้าเปิดพอร์ตหนึ่งไม่ได้ให้ลองอีกพอร์ต

| ส่วนหน้าจอ (Dashboard Section) | องค์ประกอบ | ข้อมูลที่แสดงผลและการทำงาน |
| :--- | :--- | :--- |
| **ฝั่งซ้าย: แผงกล้องสด (Live Feed)** | **🔴 Live Video Feed** | สตรีมวิดีโอสด 640x480 (~25 FPS) จากกล้อง USB Webcam ผ่าน Base64 JPEG |
| | **AI Bounding Box** | กรอบสี่เหลี่ยมสีแดงครอบตำแหน่งเปลวไฟ พร้อมเปอร์เซ็นต์ความมั่นใจของโมเดล (วาดเฉพาะเมื่อความมั่นใจ > 20%) |
| | **HUD Overlay (มุมบนซ้าย)** | กล่องมอนิเตอร์สดบนวิดีโอ: `Fire (AI)`, `Smoke (MQ2)`, `DHT22 (D2)`, `Servo` |
| **ฝั่งขวา: แผงควบคุมและสถานะ** | **📊 Telemetry Status** | มาตรวัดระดับไฟ `Fire Level (AI)` (0–100%) และระดับควัน `Smoke Level` (ppm) |
| | **🌡️ Climate & Ambient** | เซนเซอร์ DHT-22 (Pin D2) แสดงอุณหภูมิ (°C) และความชื้นสัมพัทธ์ (%) |
| | **⚙️ Servo Actuator** | สถานะมอเตอร์เซอร์โว `STANDBY` / `ACTIVE (90°)` / `COOLDOWN (60s)` |
| | **🎚️ Alert Thresholds** | สไลเดอร์ปรับเกณฑ์ `Fire Threshold` (1–100%) และ `Smoke Threshold` (ppm) |
| | **🚨 Telegram Gateway** | จำนวนข้อความที่ส่งสำเร็จ (`Total Dispatched`) และประวัติการแจ้งเตือน 5 ครั้งล่าสุด |

<a id="s14"></a>
### องค์ประกอบหน้าจอแดชบอร์ด

1. **🔴 Live Video Feed (การ์ดแสดงผลกล้องสด)**
   - สตรีมภาพวิดีโอความละเอียดสูงจากกล้อง USB Webcam แบบ Base64 JPEG อัตราเร่งประมาณ 25 FPS
   - **AI Bounding Box**: เมื่อโมเดลตรวจพบเป้าหมาย ระบบจะวาดกรอบสี่เหลี่ยมสีแดงครอบตำแหน่งวัตถุบนภาพแบบสด พร้อมระบุเปอร์เซ็นต์ความมั่นใจ
   - **HUD Telemetry Overlay**: มีกล่องมอนิเตอร์สีดำโปร่งแสงซ้อนอยู่มุมบนซ้ายของภาพ แสดงข้อมูลสด:
     - `Target (AI): X% (Th: Y%)`
     - `Smoke (MQ2): X ppm (Th: Y)`
     - `DHT22 (D2): XX.XC | XX.X%`
     - `Servo (Pin 9): STATE (Angle/Countdown)`
2. **📊 Telemetry Status (มาตรวัดระดับเซนเซอร์)**
   - **🔥 Fire Level (AI)**: มาตรวัดความมั่นใจของ AI พร้อมแท่ง Progress Bar แสดง 0–100% (ตัวเลขและแท่งจะเปลี่ยนจากสีเขียวเป็นสีแดงทันทีเมื่อระดับไฟแตะเกณฑ์)
   - **💨 Smoke Level (MQ-2 A0)**: แสดงความเข้มข้นของควันเป็นหน่วย **ppm** พร้อมแท่ง Progress Bar สเกล 0–3,000 ppm และแสดงค่าดิบ `Sensor Raw (A0): XXX` ด้านล่าง
3. **🌡️ Climate & Ambient (สภาพแวดล้อม DHT22 Pin D2)**
   - แสดงค่าอุณหภูมิห้อง/สภาพแวดล้อม (°C) และความชื้นสัมพัทธ์ (%) พร้อมแถบสี Gradient ส้ม/ฟ้า แสดงสภาวะอากาศแบบ Real-time (เป็นข้อมูลสภาพแวดล้อมอ้างอิงเท่านั้น ไม่นำไปใช้ทริกเกอร์เตือนภัย)
4. **⚙️ Servo Actuator Panel (แผงสถานะเซอร์โว Pin 9)**
   - แสดงสถานะการทำงาน 3 สภาวะ:
     - **`STANDBY` (สีเขียว)**: เซอร์โวหยุดนิ่ง ตัดสัญญาณ PWM (`detach`) ไร้การสั่นไหว
     - **`ACTIVE` (สีแดง)**: กำลังหมุนไปที่ 90 องศาเพื่อเปิดระบบดับเพลิง (หน่วงเวลา 10 วินาที)
     - **`COOLDOWN` (สีส้ม)**: หมุนกลับมาที่ 0 องศา ตัดสัญญาณ PWM และแสดงเวลานับถอยหลัง `60s... 59s...`
5. **🚨 Telegram Gateway Panel (ประวัติการส่งแจ้งเตือน)**
   - แสดงตัวเลขจำนวนครั้งที่ส่งแจ้งเตือนสำเร็จ (`Total Dispatched`)
   - แสดงสถานะล่าสุดของการส่ง (`Last Gateway Status: Standby / Success / Failed`)
   - กล่อง `History Logs` แสดงประวัติเวลาของเหตุการณ์ฉุกเฉินล่าสุด

---

<a id="s15"></a>
### การปรับเปลี่ยนค่าเกณฑ์แจ้งเตือนผ่านสไลเดอร์แบบ Real-time

บนหน้าเว็บมีแถบสไลเดอร์ให้ผู้ควบคุมสามารถปรับค่าเกณฑ์ความไว (Thresholds) ได้อย่างอิสระตามสภาพแวดล้อมจริง:

1. **🔥 Fire Camera Threshold (สไลเดอร์เกณฑ์ตรวจจับไฟ)**:
   - ปรับได้ตั้งแต่ **1% ถึง 100%** (ค่าเริ่มต้น: `80%`)
   - **ผลลัพธ์**: หากความมั่นใจของ AI มีค่ามากกว่าหรือเท่ากับค่านี้ ระบบจะ:
     - สั่งให้เซอร์โวมอเตอร์หมุน 90 องศาฉีดสารดับเพลิง
     - สั่งให้ระบบถ่ายภาพ Snapshot ส่งแจ้งเตือนฉุกเฉินเข้า Telegram
2. **💨 Smoke Sensor Threshold (สไลเดอร์เกณฑ์ระดับควัน)**:
   - ปรับได้ตั้งแต่ **100 ถึง 3,000 ppm** โดยขยับครั้งละ 50 ppm (ค่าเริ่มต้น: `600 ppm`)
   - **ผลลัพธ์**: หากระดับควันที่อ่านได้จากขา A0 มีค่ามากกว่าหรือเท่ากับค่านี้ ระบบจะ:
     - สั่งให้ระบบถ่ายภาพ Snapshot ส่งแจ้งเตือนฉุกเฉินเข้า Telegram เพื่อแจ้งเตือนว่ามีกลุ่มควันผิดปกติ

<a id="s16"></a>
### กลไกการซิงค์ค่าระหว่าง Web Client และ Python Backend

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 ผู้ใช้งานบนเบราว์เซอร์
    participant Web as 🌐 Web Dashboard (app.js)
    participant MPU as 🐧 Python Backend (main.py)
    participant Hardware as ⚙️ ระบบแจ้งเตือน / Servo

    User->>Web: เลื่อนสไลเดอร์ Fire / Smoke Threshold
    Note over Web: ขณะเลื่อน ตัวเลขบนจอจะเปลี่ยนตามทันที (Event: input)
    User->>Web: ปล่อยมือจากสไลเดอร์ (Event: change)
    Web->>MPU: socket.emit("override_fire_th", 75)
    Note over MPU: update_fire_threshold(75)<br/>ตัวแปร current_fire_threshold เปลี่ยนเป็น 75% ทันที!
    MPU->>Hardware: ปรับเงื่อนไขการ Trigger ทันทีโดยไม่ต้อง Restart บอร์ด!
    
    opt เมื่อมีผู้ใช้คนใหม่เปิดหน้าเว็บ หรือกด Refresh
        Web->>MPU: Client เชื่อมต่อเข้ามา (connect)
        MPU->>Web: socket.emit("welcome", {fire_threshold: 75, smoke_threshold: 600})
        Note over Web: สไลเดอร์จะถูกตั้งเป็นค่าล่าสุด 75% อัตโนมัติ
    end
```

> [!TIP]
> **ไม่ต้องหยุดโปรแกรม ไม่ต้องรีสตาร์ต:** การปรับสไลเดอร์บนหน้าเว็บจะส่งสัญญาณผ่าน Socket.IO อัปเดตตัวแปรในหน่วยความจำของ Python ทันที ทำให้คุณสามารถจูนเกณฑ์ความไวของเซนเซอร์และกล้องให้เข้ากับแสงและควันในห้องทดสอบได้แบบสดๆ ตลอดเวลา

---

<a id="s17"></a>
## 🚀 ขั้นตอนการนำเข้าสู่ Arduino App Lab (Importing App Guide)

<a id="s18"></a>
### การเตรียมไฟล์และโครงสร้างโฟลเดอร์

ก่อนเริ่มนำเข้าสู่โปรแกรม Arduino App Lab ให้ตรวจสอบว่าไฟล์โปรเจกต์มีโครงสร้างครบถ้วนดังนี้:

```
TelegramFireBot/
├── app.yaml                 # ไฟล์คอนฟิกแอปหลักของ App Lab
├── wildfire-dt-model.eim    # โมเดล Edge Impulse (.eim) ที่ main.py โหลดใช้งานจริง
├── python/
│   ├── main.py              # โค้ดหลักฝั่ง Linux (Webcam, AI, Bridge, Servo, Telegram)
│   └── requirements.txt     # ระบุไลบรารี edge_impulse_linux
├── sketch/
│   ├── sketch.ino           # โค้ด MCU STM32 อ่าน A0 และคุม Servo
│   └── sketch.yaml          # คอนฟิกไลบรารี Arduino_RouterBridge และ Servo
└── assets/
    ├── index.html           # หน้ากาก Web Dashboard
    ├── style.css            # สไตล์ Dark Glassmorphism
    ├── app.js               # สคริปต์ Socket.IO รับส่งข้อมูล
    └── libs/                # ไลบรารีออฟไลน์ socket.io และ qrcode
```

> [!TIP]
> คุณสามารถเลือกนำเข้าได้ 2 รูปแบบ:
> 1. นำเข้าเป็น **โฟลเดอร์โปรเจกต์ `TelegramFireBot`** โดยตรง
> 2. บีบอัดโฟลเดอร์ให้เป็นไฟล์ **`TelegramFireBot.zip`** (โดยข้างใน Zip ต้องประกอบด้วยไฟล์ `app.yaml`, โฟลเดอร์ `python/`, `sketch/`, `assets/` อยู่ที่ Root ของ Zip ทันที)

---

<a id="s19"></a>
### ขั้นตอนการ Import ทีละขั้นตอน

1. **เปิดโปรแกรม Arduino App Lab**:
   - เชื่อมต่อบอร์ด **Arduino UNO Q** เข้ากับคอมพิวเตอร์ผ่านสาย Type-C
   - เปิดโปรแกรม **Arduino App Lab** แล้วรอให้โปรแกรมตรวจสอบสถานะของบอร์ดจนขึ้นว่าเชื่อมต่อเรียบร้อย
2. **เข้าสู่เมนูนำเข้าแอป (Import App)**:
   - ที่หน้าหลักของโปรแกรม มองหาปุ่ม **"Import App"** (หรือคลิกที่เครื่องหมาย **`+`** / Add Application)
3. **เลือกไฟล์โปรเจกต์**:
   - เลือกตัวเลือก **Import from ZIP** (เลือกไฟล์ `TelegramFireBot.zip`) หรือ **Import from Folder** (เลือกโฟลเดอร์โปรเจกต์)
4. **รอ App Lab เตรียมสภาพแวดล้อม**:
   - โปรแกรมจะอ่านไฟล์ `app.yaml` เพื่อดึง Bricks ที่เกี่ยวข้อง (`video_object_detection`, `web_ui`)
   - โปรแกรมจะสร้าง Python Virtual Environment และติดตั้งไลบรารีจาก `python/requirements.txt`
   - โปรแกรมจะคอมไพล์และแฟลชเฟิร์มแวร์ในโฟลเดอร์ `sketch/` ลงสู่ชิป STM32U585 ด้วย Zephyr RTOS ให้โดยอัตโนมัติ
5. **เริ่มการทำงาน (Run)**:
   - กดปุ่ม **"Run"** สีเขียวที่มุมบนขวา
   - ตรวจสอบหน้าต่าง Logs เพื่อดูสถานะการเปิดกล้อง USB Webcam และการโหลดโมเดล AI
   - คลิกลิงก์ Web Dashboard ที่ App Lab แสดง เพื่อเริ่มใช้งาน

---

<a id="s20"></a>
## ⚡ การตั้งค่าให้แอปทำงานอัตโนมัติเมื่อเปิดเครื่อง (Autostart on Boot)

เมื่อคุณต้องการนำบอร์ด Arduino UNO Q ไปประกอบลงกล่อง และติดตั้งในอาคารหรือโรงงานเพื่อใช้งานเป็นอุปกรณ์เตือนภัยอัคคีภัยแบบ **Standalone (ทำงานเดี่ยวๆ โดยไม่ต้องต่อคอมพิวเตอร์)** คุณต้องเปิดใช้งานฟังก์ชัน **Autostart**:

<a id="s21"></a>
### ขั้นตอนการเปิดใช้งาน Autostart

1. เปิดโปรแกรม **Arduino App Lab** ขณะที่เชื่อมต่อกับบอร์ด
2. ไปที่หน้าแท็บ **Apps** หรือหน้ารายการแอปที่ติดตั้งอยู่บนบอร์ด (Installed Applications)
3. ค้นหาการ์ดแอปพลิเคชัน **`TelegramFireBot`**
4. มองหาสวิตช์ Toggle หรือตัวเลือกที่เขียนว่า **"Autostart"** หรือ **"Run on startup"**
   - หรือคลิกที่ปุ่มเมนูจุด 3 จุด (`...`) บนการ์ดแอป แล้วเลือกคำสั่ง **"Set as Autostart"**
5. เลื่อนสวิตช์ให้เป็น **ON (เปิดใช้งาน)**
6. สังเกตจะมีสัญลักษณ์ไอคอนรูปเข็มกลัดหรือข้อความสีเขียวระบุว่า **`Autostart: Enabled`** บนการ์ดแอป

> ⚡ **ข้อมูลบนการ์ดแอปเมื่อเปิด Autostart สำเร็จ:**
> - **ชื่อแอป:** `🔥 TelegramFireBot`
> - **คำอธิบาย:** `Fire and Smoke Detection with Telegram Alert`
> - **สถานะ (Status):** `Installed`
> - **การทำงานอัตโนมัติ (Autostart):** `[ ON ] ⚡ (Runs automatically on device boot)`
> - **พอร์ตการเชื่อมต่อ (Ports):** `8080` (ตาม `app.yaml`; Web UI อาจอยู่ที่ `7000`)

<a id="s22"></a>
### การนำไปติดตั้งใช้งานจริงแบบ Standalone

- **การจ่ายไฟ**: สามารถใช้ Adapter จ่ายไฟ 5V (กระแสอย่างน้อย 2.5A - 3A) เสียบเข้าช่อง Type-C ของบอร์ด Arduino UNO Q ได้โดยตรง
- **ลำดับการบูตเครื่องอัตโนมัติ (Cold Boot Workflow)**:
  1. เมื่อเสียบปลั๊กไฟ บอร์ดจะเริ่มบูตระบบ Linux บนชิป Qualcomm และบูต Zephyr RTOS บนชิป STM32 (~20-30 วินาที)
  2. ระบบ Autostart จะสั่งเปิดคอนเทนเนอร์ของ TelegramFireBot ขึ้นมาทันที
  3. กล้อง USB Webcam จะเปิดทำงาน โมเดล AI จะถูกโหลดเข้าสู่ RAM และเซนเซอร์ MQ-2 จะเริ่มสตรีมข้อมูล
  4. มอเตอร์เซอร์โวจะอยู่ในโหมด Standby ตัดสัญญาณ PWM เพื่อป้องกันการสั่น
  5. บอร์ดจะเชื่อมต่อ Wi-Fi และพร้อมส่งแจ้งเตือน Telegram ทันทีที่มีเหตุเพลิงไหม้เกิดขึ้น แม้ไม่มีคอมพิวเตอร์เชื่อมต่ออยู่ก็ตาม!

---

<a id="s23"></a>
## 🧠 คู่มือการเปลี่ยนและอัปเดตโมเดล AI และปรับแต่ง Keyword (AI Model & Keyword Customization Guide)

หากคุณต้องการเปลี่ยนไปใช้โมเดลใหม่ที่เทรนเองจาก **Edge Impulse** ไม่ว่าจะเป็นโมเดลตรวจจับไฟรุ่นปรับปรุง หรือต้องการนำระบบไปประยุกต์ใช้กับงานตรวจจับประเภทอื่น (เช่น ตรวจจับคน `person`, ตรวจหมวกนิรภัย `helmet`, ยานพาหนะ `car` หรือควัน `smoke`) **วิธีที่ง่ายและสะดวกที่สุดคือ: เปลี่ยนชื่อโมเดลใหม่ให้เป็นชื่อเดิมแล้ววางทับ โดยไม่ต้องแก้โค้ดคอนฟิกเลย!**

---

<a id="s24"></a>
### ขั้นตอนที่ 1: ดาวน์โหลดโมเดลใหม่ เปลี่ยนชื่อเป็นชื่อเดิม แล้ววางทับ (วิธีแนะนำ: ง่ายที่สุด 100%)

> [!TIP]
> **🌟 เคล็ดลับสุดง่าย (The Simplest & Recommended Way):**
> คุณ**ไม่ต้องเข้าไปแก้ไขโค้ดใน `app.yaml` หรือแก้ชื่อไฟล์ใน `python/main.py` เลยแม้แต่บรรทัดเดียว!**
> เพียงแค่ **เปลี่ยนชื่อไฟล์โมเดลใหม่ที่เพิ่งดาวน์โหลดมา ให้กลายเป็นชื่อเดิมคือ `wildfire-dt-model.eim`** แล้วนำไปวางทับไฟล์เดิมได้ทันที!

#### วิธีการทำทีละสเต็ป:
1. **ดาวน์โหลดโมเดลจาก Edge Impulse**:
   - เข้าสู่โปรเจกต์ของคุณบน [Edge Impulse Studio](https://studio.edgeimpulse.com/)
   - ไปที่แถบเมนู **Deployment** ทางซ้ายมือ
   - ในช่องค้นหา Deployment options ให้เลือก **Linux (AARCH64)** (ชิป Qualcomm QRB2210 ของ UNO Q เป็น ARM 64-bit)
   - คลิกปุ่ม **Build** เพื่อสร้างแพ็กเกจไบนารี จะได้ไฟล์นามสกุล `.eim` ออกมา (เช่น `my-new-model.eim`)
2. **เปลี่ยนชื่อไฟล์โมเดลใหม่ ให้เป็นชื่อเดิม**:
   - เปลี่ยนชื่อไฟล์ที่เพิ่งดาวน์โหลดมาให้กลายเป็นชื่อเดิมเป๊ะๆ:
     ```bash
     wildfire-dt-model.eim
     ```
3. **วางทับ (Overwrite/Replace) ไฟล์เดิมในโฟลเดอร์โปรเจกต์**:
   - นำไฟล์ `wildfire-dt-model.eim` ตัวใหม่นี้ ไปคัดลอกวางทับไฟล์เดิมในโฟลเดอร์โปรเจกต์ (หรือลากใส่ไฟล์ Zip ทับไฟล์เดิม) ได้ทันที!
   - **เสร็จสิ้น!** ไม่ต้องไปแตะต้องไฟล์ `app.yaml` หรือชื่อโมเดลใน Python เลย

> [!NOTE]
> **โมเดลถูกอ้างอิง 2 ที่:** `python/main.py` โหลดไฟล์ `wildfire-dt-model.eim` จาก **โฟลเดอร์รากของโปรเจกต์** (ใช้ตรวจจับ วาดกรอบ และสั่งแจ้งเตือนจริง) ส่วน `app.yaml` ส่ง path `/home/arduino/.arduino-bricks/ei-models/wildfire-dt-model.eim` ให้ Brick `video_object_detection` ซึ่งเป็นตำแหน่งของ App Lab เอง การวางทับไฟล์ในโฟลเดอร์โปรเจกต์จึงเพียงพอสำหรับการทำงานของระบบนี้ และการคงชื่อไฟล์เดิมไว้ทำให้ทั้งสองที่ยังตรงกัน

---

<a id="s25"></a>
### ขั้นตอนที่ 2: กำหนด Keyword และธีมที่หัวโค้ด Python (แก้ที่เดียว เว็บเปลี่ยนตามทั้งหมด!)

ระบบ TelegramFireBot ได้รับการออกแบบสถาปัตยกรรมให้มี **Single Source of Truth**:
> [!TIP]
> **🌟 แก้จุดเดียว เปลี่ยนครบทั้งระบบ (1-Click Centralized Configuration):**
> คุณสามารถเปิดไฟล์ **`python/main.py`** แล้วแก้ไขเฉพาะ 4 ตัวแปรในบล็อก `⚙️ USER CONFIGURATION` ที่ส่วนหัวไฟล์ **ไม่ต้องเข้าไปแก้ไขไฟล์ `index.html` หรือ `app.js` เลย**
> เมื่อเปิดหน้าเว็บแดชบอร์ด ระบบจะซิงค์ข้อมูลผ่าน Socket.IO ปรับเปลี่ยนชื่อระบบ, ไอคอน, แผงตรวจวัด, ป้ายสไลเดอร์, กล่อง HUD วิดีโอสด และข้อความ Telegram Alert ให้ตรงกันทั้งหมดโดยอัตโนมัติ!

#### การตั้งค่าใน `python/main.py`:

```python
# ==========================================
# ⚙️ USER CONFIGURATION (ส่วนตั้งค่าสำหรับผู้ใช้งาน)
# 🌟 แก้จุดนี้จุดเดียว! หน้าเว็บแดชบอร์ด, สไลเดอร์, กล่อง HUD วิดีโอสด และ Telegram จะเปลี่ยนตามทั้งหมดอัตโนมัติ
# ==========================================
# ค่าตั้งต้นเดิมของระบบ: ตรวจจับไฟ (Fire)
TARGET_LABEL = "fire"              # Keyword จากโมเดล Edge Impulse เช่น "fire", "person", "smoke", "helmet", "car"
TARGET_DISPLAY_NAME = "Fire"       # ชื่อแสดงผล เช่น "Fire", "Person", "Safety Helmet"
TARGET_ICON = "🔥"                 # ไอคอนแสดงผล เช่น "🔥", "👤", "⛑️", "🚗", "🎯"
APP_TITLE = "Fire & Smoke AI"      # ชื่อหัวเว็บ/ระบบ เช่น "Fire & Smoke AI", "Person AI Guard"
```

**ตัวอย่างเมื่อต้องการเปลี่ยนไปตรวจจับ "คน" (`Person`):**
เพียงแค่เปลี่ยนค่าในบล็อกนี้ใน `python/main.py`:

```python
TARGET_LABEL = "person"            # Label ให้ตรงกับที่เทรนใน Edge Impulse
TARGET_DISPLAY_NAME = "Person"     # ชื่อแสดงผล
TARGET_ICON = "👤"                 # ไอคอนบนหน้าเว็บและ Telegram
APP_TITLE = "Person AI Guard"      # ชื่อหัวเว็บแดชบอร์ด
```

#### สิ่งที่ระบบจะอัปเดตให้อัตโนมัติทันที:
1. **🌐 Web Dashboard (หน้าเว็บแดชบอร์ด)**:
   - ไอคอนหัวเว็บเปลี่ยนเป็น `👤`
   - ชื่อหัวเว็บเปลี่ยนเป็น `Person AI Guard`
   - แผง Telemetry เปลี่ยนเป็น `👤 Person Level (AI)`
   - ป้ายกำกับสไลเดอร์เปลี่ยนเป็น `👤 Person Camera Threshold`
   - ข้อความคำอธิบายสไลเดอร์และบันทึกแจ้งเตือนเปลี่ยนเป็น `Person Alert` อัตโนมัติ
2. **📹 กล้องสด (Live Video & HUD Overlay)**:
   - กรอบ Bounding Box สีแดงจะครอบจับเฉพาะคลาส `person` และมีป้ายชื่อ `Person: XX%`
   - กล่องข้อมูล HUD มุมบนซ้ายจะแสดง `Person (AI): XX.X% (Th: 80%)`
3. **🚨 Telegram Alert**:
   - ข้อความแจ้งเตือนจะส่งว่า: `🚨 ALARM: Person Detected! 🚨` (หรือ `Person & Smoke` / `Smoke (MQ-2)` ตามเงื่อนไขที่ทริกเกอร์)
   - บรรทัดรายงานระดับความมั่นใจจะแสดง: `👤 Person Level: XX.X%`

---

<a id="s26"></a>
### ขั้นตอนที่ 3: (ทางเลือกเสริม) การเปลี่ยนชื่อแอปในการ์ดของ App Lab

หากต้องการให้ชื่อการ์ดแอปพลิเคชันในโปรแกรม **Arduino App Lab** เปลี่ยนชื่อด้วย สามารถเข้าไปแก้ที่ไฟล์ `app.yaml` ได้โดยตรง:

```yaml
name: TelegramPersonBot
description: Person Detection with Telegram Alert
...
icon: 👤
```
*(หากไม่แก้ App Lab จะยังคงแสดงการ์ดชื่อเดิม แต่การทำงานและหน้าเว็บจะทำงานด้วยโมเดลใหม่ 100%)*

---

<a id="s27"></a>
### ขั้นตอนที่ 4: การลบแอปเดิมและ Import ใหม่ใน App Lab เพื่อล้างแคช

เมื่อมีการสลับโมเดล AI ไบนารี `.eim` ตัวใหม่ คอนเทนเนอร์ของ Arduino App Lab อาจมีการแคชไฟล์โมเดลเก่าไว้ **วิธีที่สะอาด ถูกต้อง และไม่เกิดปัญหาแคชค้าง 100% คือ**:

```
[ 1. กด Stop แอปเดิม ]
          ↓
[ 2. คลิกปุ่ม '...' บนการ์ดแอป แล้วเลือก 'Delete' เพื่อลบแอปเดิมออกจากบอร์ด ]
          ↓
[ 3. คลิก 'Import App' แล้วเลือกไฟล์ Zip หรือโฟลเดอร์โปรเจกต์ที่วางโมเดลใหม่แล้ว ]
          ↓
[ 4. กด 'Run' เพื่อให้ App Lab สร้างคอนเทนเนอร์และโหลดโมเดลใหม่อย่างบริสุทธิ์ ]
```

1. ในหน้าต่าง **Arduino App Lab** ให้กดปุ่ม **Stop** บนการ์ดแอป
2. คลิกปุ่มจุดสามจุด **`...`** บนการ์ดแอป แล้วเลือก **Delete** เพื่อลบแอปเดิมออก
3. คลิกปุ่ม **Import App** ที่แถบเครื่องมือ
4. เลือกโฟลเดอร์โปรเจกต์ (หรือไฟล์ `.zip` ที่เตรียมไว้)
5. รอ App Lab แตกไฟล์และจัดเตรียม จากนั้นกดปุ่ม **Run**
6. ตรวจสอบในแท็บ Logs จะต้องพบข้อความ:
   ```
   Ensured executable permissions for /.../wildfire-dt-model.eim
   Edge Impulse model initialized successfully from: /.../wildfire-dt-model.eim
   Model info: ...
   ```
   ระบบจะเริ่มทำงานด้วยโมเดลใหม่ Keyword ใหม่ และหน้าเว็บใหม่ทันที!

---

<a id="s28"></a>
### กรณีพิเศษ: หากต้องการตั้งชื่อไฟล์โมเดลเป็นชื่ออื่นจริงๆ (ไม่แนะนำเพราะต้องแก้หลายจุด)

หากจำเป็นต้องตั้งชื่อไฟล์โมเดลเป็นชื่ออื่น เช่น `custom-model.eim` คุณจะต้องไปตามแก้จุดอ้างอิงเอง 2 ไฟล์:
1. **`app.yaml`**: แก้ไขตัวแปร `EI_OBJ_DETECTION_MODEL` และ `EI_V_OBJ_DETECTION_MODEL` ใต้ Brick `video_object_detection` เป็นชื่อใหม่
2. **`python/main.py`**: แก้ไขตัวแปร `MODEL_PATH = "custom-model.eim"` ในบล็อก `USER CONFIGURATION`
*(แนะนำให้ใช้วิธีเปลี่ยนชื่อเป็น `wildfire-dt-model.eim` แล้ววางทับตาม **ขั้นตอนที่ 1** จะง่าย รวดเร็ว และปลอดภัยที่สุด)*

---

<a id="s29"></a>
## 🔧 คู่มือเพิ่ม / เปลี่ยน / ถอดเซนเซอร์ (Sensor Customization Guide)

ข้อมูลเซนเซอร์ทุกตัวไหลผ่าน **5 จุด** ตามลำดับนี้ ไม่ว่าจะเพิ่ม เปลี่ยน หรือถอดเซนเซอร์ ให้ไล่แก้ตามจุดเหล่านี้:

```
[1] sketch.ino อ่านค่า → [2] Bridge.notify / provide → [3] main.py รับค่า + เก็บสถานะ
      → [4] เงื่อนไขแจ้งเตือน / HUD / Telegram → [5] หน้าเว็บ (index.html + app.js)
```

| จุด | ไฟล์ | สิ่งที่ต้องแก้ |
| :--- | :--- | :--- |
| 1 | `sketch/sketch.ino` | ประกาศขา (`const int ..._PIN`), ฟังก์ชันอ่านค่า, ส่งค่าใน `loop()` |
| 2 | `sketch/sketch.ino` | `Bridge.notify("ชื่อ_event", ค่า)` ใน `loop()` และ `Bridge.provide("read_...", ฟังก์ชัน)` ใน `setup()` |
| 3 | `python/main.py` | ตัวแปรสถานะ + `threading.Lock()`, ฟังก์ชัน handler, `Bridge.provide(...)`, `sensor_polling_worker()` |
| 4 | `python/main.py` | `latest_detections`, `process_frame()` (HUD + เงื่อนไข `is_...`), `send_telegram_alert()` (caption) |
| 5 | `assets/index.html`, `assets/app.js` | เพิ่มช่องแสดงผล และอ่านค่าใน `socket.on('detection', ...)` |

> [!IMPORTANT]
> ชื่อ event ต้อง **ตรงกันทุกตัวอักษร** ระหว่าง `Bridge.notify("x")` ฝั่ง sketch กับ `Bridge.provide("x", ...)` ฝั่ง Python และชื่อฟังก์ชัน `Bridge.provide("read_x")` ฝั่ง sketch กับ `Bridge.call("read_x")` ฝั่ง Python
> หลังแก้ `sketch.ino` App Lab จะคอมไพล์และแฟลช MCU ใหม่ให้เองตอนกด **Run** ถ้าเพิ่มไลบรารี Arduino ให้เพิ่มใน `sketch/sketch.yaml` ด้วย

<a id="s30"></a>
### กรณีที่ 1: เพิ่มเซนเซอร์ใหม่ (ตัวอย่าง: MQ-135 ที่ขา A1)

**① `sketch/sketch.ino`**
```cpp
const int MQ135_PIN = A1;

int read_mq135() {
    return analogRead(MQ135_PIN);
}

// ใน setup()
Bridge.provide("read_mq135", read_mq135);

// ใน loop() — ส่งค่าทุก 200ms เหมือน MQ-2
static unsigned long last_mq135_time = 0;
if (millis() - last_mq135_time >= 200) {
    last_mq135_time = millis();
    Bridge.notify("mq135_data", analogRead(MQ135_PIN));
}
```

**② `python/main.py` — รับค่าและเก็บสถานะ**
```python
# ใกล้กับ MQ-2 State
current_mq135_raw = 0
mq135_lock = threading.Lock()

def on_mq135_data(raw_val):
    global current_mq135_raw
    try:
        with mq135_lock:
            current_mq135_raw = int(raw_val)
    except Exception as e:
        print(f"Error handling mq135_data: {e}")

# ในบล็อก if Bridge:
Bridge.provide("mq135_data", on_mq135_data)

# ใน sensor_polling_worker() (fallback)
v = Bridge.call("read_mq135")
if v is not None:
    on_mq135_data(v)
```

**③ `python/main.py` — ใช้งานค่าใน `process_frame()`**
```python
with mq135_lock:
    mq135_val = current_mq135_raw
latest_detections["mq135_raw"] = mq135_val   # ส่งไปหน้าเว็บอัตโนมัติผ่าน event "detection"

# (ถ้าต้องการให้ทริกเกอร์แจ้งเตือน) เพิ่มเงื่อนไขข้าง is_fire / is_smoke
MQ135_THRESHOLD = 400
is_air = (mq135_val >= MQ135_THRESHOLD)
if is_fire or is_smoke or is_air:
    ...
```
- ถ้าต้องการให้แสดงบนวิดีโอสด ให้เพิ่ม `cv2.putText(...)` อีกบรรทัดใน HUD แล้วขยายกรอบ `cv2.rectangle(ui_frame, (10, 10), (350, 115), ...)` ให้สูงขึ้น (ทีละ ~22px ต่อบรรทัด)
- ถ้าต้องการให้แสดงใน Telegram ให้เพิ่มบรรทัดใน `caption` ของ `send_telegram_alert()`

**④ หน้าเว็บ**
- `assets/index.html`: เพิ่ม element เช่น `<span id="mq135-val">--</span>` ในแผงที่ต้องการ
- `assets/app.js`: ใน `socket.on('detection', (data) => { ... })` เพิ่ม
  ```js
  const mq135El = document.getElementById('mq135-val');
  if (data.mq135_raw !== undefined) mq135El.textContent = data.mq135_raw;
  ```

<a id="s31"></a>
### กรณีที่ 2: เปลี่ยนเซนเซอร์แทน MQ-2 (เช่น MQ-135, MQ-7 หรือเซนเซอร์ควันรุ่นอื่น)

- **ถ้าเป็นเซนเซอร์อนาล็อกและต่อขา A0 เหมือนเดิม** → ไม่ต้องแก้ sketch เลย ระบบจะอ่านค่าและส่งผ่าน `mq2_data` ตามเดิม
  - แก้สูตรใน `raw_to_smoke_ppm()` ให้เข้ากับ datasheet ของเซนเซอร์ใหม่ (ค่า `50.0`, `80.0`, `1.8` คือพารามิเตอร์ของเส้นโค้ง)
  - ปรับ `DEFAULT_SMOKE_THRESHOLD` และช่วงสไลเดอร์ (`min` / `max` / `step` ของ `smoke-slider` ใน `index.html`)
  - แก้ข้อความ `Smoke (MQ2)` ใน HUD, caption Telegram และป้ายบนหน้าเว็บ
- **ถ้าย้ายขา** → แก้ `MQ2_PIN` ใน `sketch.ino`
- **ถ้าเป็นเซนเซอร์ดิจิทัล (เช่น Flame Sensor ขา DO)** → เปลี่ยน `analogRead` เป็น `digitalRead` และให้ Python ตีความเป็น 0/1 แทน ppm
- ⚠️ ตรวจแรงดันขาเอาต์พุตของเซนเซอร์ใหม่ทุกครั้ง ขาอนาล็อกของ UNO Q รับได้ไม่เกิน **3.3V**

<a id="s32"></a>
### กรณีที่ 3: ถอดเซนเซอร์ออก (เช่น ไม่ใช้ DHT-22)

- **วิธีง่าย (ไม่แก้โค้ด):** ถอดสายออกได้เลย
  - DHT-22: `read_dht22()` จะคืน `false` และส่งค่าเดิมล่าสุดต่อ (ค่าเริ่มต้น 25.0°C / 50.0%) ระบบยังทำงานต่อปกติ แต่ค่าบนจอจะไม่ใช่ค่าจริง
  - MQ-2: ขา A0 ที่ลอยอยู่จะอ่านค่ามั่ว **อาจทำให้แจ้งเตือนควันผิดพลาด** ให้ต่อขา A0 ลง GND หรือแก้โค้ดตามวิธีด้านล่าง
- **วิธีสะอาด:** ลบตามจุด 1–5 ในตารางด้านบน
  - `sketch.ino`: ลบโค้ดอ่านค่า, `Bridge.notify` และ `Bridge.provide` ของเซนเซอร์นั้น
  - `main.py`: ลบ handler, `Bridge.provide`, การเรียกใน `sensor_polling_worker()`, ค่าใน `latest_detections`, บรรทัด HUD และบรรทัด caption Telegram
  - **ถ้าถอด MQ-2:** ต้องลบ `is_smoke` ออกจากเงื่อนไขแจ้งเตือนใน `process_frame()` ด้วย ไม่อย่างนั้นระบบจะยังเทียบค่ากับเกณฑ์ควันอยู่
  - หน้าเว็บ: ซ่อนหรือลบแผงที่ไม่ใช้ใน `index.html` (โค้ดใน `app.js` จะข้ามค่าที่ไม่มีมาให้เองเพราะเช็ก `!== undefined` อยู่แล้ว)

<a id="s33"></a>
### ตรวจสอบหลังแก้ไข

1. กด **Run** ใน App Lab แล้วรอคอมไพล์ sketch จนเสร็จ
2. ใน Logs ต้องเห็นข้อความลงทะเบียน handler (เช่น `Bridge RPC 'mq2_data' handler registered.`) และไม่มี `Error handling ...` ต่อเนื่อง
3. เปิดหน้าเว็บแล้วดูว่าค่าเซนเซอร์ใหม่เปลี่ยนตามจริง
4. ทดสอบให้ค่าเกินเกณฑ์ แล้วตรวจว่าได้รับข้อความ Telegram

---

<a id="s34"></a>
## 📂 โครงสร้างไฟล์และโค้ดอย่างละเอียด (Project & Code Structure)

<a id="s35"></a>
### 1. `app.yaml`
ไฟล์ประกาศคุณลักษณะแอปพลิเคชันสำหรับ **Arduino App Lab**:
- กำหนดชื่อแอป `TelegramFireBot` และไอคอน 🔥
- เปิดพอร์ตสื่อสาร `8080` สำหรับระบบ WebUI
- ผูกโมเดล Edge Impulse ผ่าน Brick `arduino:video_object_detection`
- เรียกใช้คอมโพเนนต์เว็บเซิร์ฟเวอร์ผ่าน Brick `arduino:web_ui`

<a id="s36"></a>
### 2. `python/main.py`
แกนกลางของระบบที่ประมวลผลบน Linux MPU (Qualcomm Dragonwing):
- **ระบบกำหนดเป้าหมายยืดหยุ่น (`TARGET_LABEL` & `TARGET_DISPLAY_NAME`)**: กำหนดคีย์เวิร์ดคลาสที่ต้องการตรวจจับได้จากส่วนหัวของโค้ด พร้อมส่งชื่อและสถานะไปซิงค์กับหน้าเว็บและ Telegram Alert
- **ระบบ Auto-chmod โมเดล**: มีคำสั่ง `os.chmod()` อัตโนมัติ ป้องกัน Error สิทธิ์การ Execute (`+x`) ของไฟล์ `.eim`
- **คลาส `ServoController`**: ควบคุมเซอร์โวมอเตอร์แบบ State Machine ผ่านเธรดแยก (`threading.Thread`) ทำให้การหน่วงเวลา 10 วินาที และการนับถอยหลัง Cooldown 60 วินาที ไม่ไปหน่วงการประมวลผลของกล้องวิดีโอและหน้าเว็บ
- **ฟังก์ชัน `raw_to_smoke_ppm()`**: แปลงค่า ADC จากขา A0 เป็นหน่วย ppm อ้างอิงสมการ Exponential Curve
- **ระบบจัดการเซนเซอร์ DHT-22 (Pin D2)**: รับสตรีมอุณหภูมิและความชื้นผ่าน Bridge RPC เพื่อแสดงผลสภาพแวดล้อมบน Web Dashboard และแนบใน Telegram Alert
- **ฟังก์ชัน `sensor_polling_worker()`**: เธรดสำรองที่เรียกอ่านค่า MQ-2 และ DHT-22 ผ่าน `Bridge.call()` ทุก 1 วินาที
- **ฟังก์ชัน `trigger_telegram_alert()` / `send_telegram_alert()`**: เข้ารหัสภาพถ่าย (640x480, JPEG quality 85) แนบพิกัด Google Maps ค่าอุณหภูมิ/ความชื้น วันที่และเวลาโซนไทย (UTC+7) ส่งผ่าน Telegram Bot API (`sendPhoto`) ในเธรดแยก พร้อมระบบป้องกันสแปม `TELEGRAM_COOLDOWN` 20 วินาที
- **ฟังก์ชัน `open_usb_camera()` / `camera_loop()`**: เปิดกล้องตามลำดับ index `[2, 0, 1]` อ่านเฟรม ~25 FPS และเชื่อมต่อกล้องใหม่อัตโนมัติเมื่อหลุด
- **ระบบ Socket.IO Handlers**:
  - รับสัญญาณ `override_fire_th` และ `override_smoke_th` จากสไลเดอร์หน้าเว็บมาปรับเกณฑ์ทันที
  - ส่งข้อมูล `detection`, `servo_status`, `telegram_status` และสตรีมภาพ `video_frame` ไปยังหน้าเว็บแบบเรียลไทม์

<a id="s37"></a>
### 3. `sketch/sketch.ino` & `sketch.yaml`
เฟิร์มแวร์ฝั่งชิปไมโครคอนโทรลเลอร์ STM32U585:
- `sketch.yaml`: กำหนดโปรไฟล์บอร์ด `arduino:zephyr:unoq` และนำเข้าไลบรารี `Arduino_RouterBridge` และ `Servo`
- `sketch.ino`:
  - ฟังก์ชัน `read_mq2()`, `read_dht_temp()`, `read_dht_hum()`: เปิดให้ฝั่ง Python เรียกผ่าน `Bridge.provide()` (ใช้กับ fallback polling)
  - ฟังก์ชัน `read_dht22()`: อ่านค่าอุณหภูมิและความชื้นสัมพัทธ์จากขา **Digital Pin 2 (D2)** ด้วยโปรโตคอล 1-Wire แบบปลอดภัย
  - ฟังก์ชัน `set_servo(angle)`: สั่ง `fireServo.attach(9)` เมื่อต้องการหมุน และสั่ง `fireServo.write(angle)` (จำกัดไม่เกิน 180°; ถ้าส่งค่าติดลบจะ detach แทน)
  - ฟังก์ชัน `detach_servo()`: สั่ง `fireServo.detach()` เพื่อตัดสัญญาณ PWM อย่างเด็ดขาด ป้องกันเซอร์โวสั่น
  - ในฟังก์ชัน `loop()`:
    - สตรีม `Bridge.notify("mq2_data", mq2_raw)` ทุก 200ms
    - สตรีม `Bridge.notify("dht_temp", temp)` และ `Bridge.notify("dht_hum", hum)` ทุก 2.5 วินาที

<a id="s38"></a>
### 4. `assets/` (Web Dashboard)
- `index.html`: โครงสร้างหน้าเว็บ แบ่งเป็นแผงวิดีโอสด (Live Feed) พร้อม HUD Overlay, แผง Telemetry, แผงตรวจวัดสภาพแวดล้อม (DHT22 Climate Panel), แผงเซอร์โว, สไลเดอร์ปรับเกณฑ์คู่ และประวัติแจ้งเตือน Telegram
- `style.css`: ตกแต่งด้วยธีม Dark Glassmorphism ผสมผสาน Neon Glow, Smooth Gradient และรองรับ Responsive บนแท็บเล็ต/มือถือ
- `app.js`: เชื่อมต่อ Socket.IO, ซิงค์ข้อมูลสไลเดอร์แบบ 2-way data binding, อัปเดตข้อมูล DHT22 และชื่อ Target Label แบบ Real-time

---

<a id="s39"></a>
## ⚙️ การปรับแต่งพารามิเตอร์ระบบในโค้ด (Advanced Configuration)

หากต้องการแก้ไขการตั้งค่าเริ่มต้นของระบบ ให้เปิดไฟล์ `python/main.py` และปรับแต่งพารามิเตอร์ในบล็อก `⚙️ USER CONFIGURATION` ที่ส่วนหัวไฟล์:

| ตัวแปรในโค้ด | ค่าเริ่มต้น | รายละเอียดและการตั้งค่า |
| :--- | :--- | :--- |
| `INPUT_MODE` | `"WEBCAM"` | โหมดรับภาพ: ใช้ `"WEBCAM"` สำหรับกล้อง USB (โหมด `"MOBILE"` มีระบุในคอมเมนต์ แต่ **ยังไม่รองรับ** — ถ้าตั้งค่านี้ระบบจะไม่ประมวลผลภาพเลย) |
| `TARGET_LABEL` | `"fire"` | Keyword คลาสที่ต้องการตรวจจับจากโมเดล Edge Impulse (เช่น `"fire"`, `"person"`, `"helmet"`) |
| `TARGET_DISPLAY_NAME` | `"Fire"` | ชื่อที่ต้องการแสดงบนหน้าจอแดชบอร์ด, HUD และในข้อความ Telegram |
| `TARGET_ICON` | `"🔥"` | ไอคอนประจำคลาสที่จะแสดงบนหน้าเว็บและ Telegram (เช่น `"🔥"`, `"👤"`, `"⛑️"`, `"🚗"`, `"🎯"`) |
| `APP_TITLE` | `"Fire & Smoke AI"` | ชื่อระบบบนหัวเว็บแดชบอร์ด (เช่น `"Fire & Smoke AI"`, `"Person AI Guard"`) |
| `TELEGRAM_TOKEN` | `"YOUR_TELEGRAM_BOT_TOKEN"` | Bot Token ที่ได้รับจาก `@BotFather` (ดู [การตั้งค่า Telegram Bot](#s3)) |
| `TELEGRAM_CHAT_ID` | `"YOUR_CHAT_ID"` | Chat ID ของผู้ใช้ หรือ Group ID ของกลุ่ม Telegram ที่ต้องการรับแจ้งเตือน |
| `DEFAULT_FIRE_THRESHOLD` | `80.0` | เกณฑ์ความมั่นใจตรวจจับไฟเริ่มต้น (1% – 100%) หากแตะเกณฑ์จะหมุน Servo และส่ง Telegram |
| `DEFAULT_SMOKE_THRESHOLD` | `600.0` | เกณฑ์ระดับควันเริ่มต้น (100 – 3,000 ppm) หากแตะเกณฑ์จะส่ง Telegram |
| `TELEGRAM_COOLDOWN` | `20` | ระยะเวลาหน่วงระหว่างการส่ง Telegram แต่ละข้อความ (วินาที) ป้องกันข้อความสแปม |
| `LATITUDE` / `LONGITUDE` | `"-"` | พิกัดจุดติดตั้งของกล่อง ใช้สร้างลิงก์เปิดแผนที่ Google Maps ในข้อความเตือน |
| `MODEL_PATH` | `"wildfire-dt-model.eim"` | ชื่อไฟล์โมเดล Edge Impulse ที่ต้องการโหลด (อ้างอิงจากโฟลเดอร์รากของโปรเจกต์) |

**ค่าที่กำหนดตายตัวในโค้ด (ไม่อยู่ในบล็อก USER CONFIGURATION แต่แก้ได้หากจำเป็น):**

| ค่า | ค่าปัจจุบัน | ตำแหน่งในโค้ด |
| :--- | :--- | :--- |
| เวลาที่เซอร์โวค้างที่ 90° | 10 วินาที | `ServoController._run_servo_cycle()` ใน `main.py` |
| เวลารอเซอร์โวกลับ 0° ก่อน detach | 1.5 วินาที | `ServoController._run_servo_cycle()` |
| Cooldown ของเซอร์โว | 60 วินาที | `ServoController._run_servo_cycle()` |
| ความมั่นใจขั้นต่ำที่จะวาด Bounding Box | 20% | `process_frame()` |
| เขตเวลาในข้อความ Telegram | UTC+7 (Bangkok) | `send_telegram_alert()` |
| ลำดับ index กล้องที่ลองเปิด | `[2, 0, 1]` | `open_usb_camera()` |
| ความถี่ส่งค่า MQ-2 / DHT-22 | 200ms / 2.5s | `loop()` ใน `sketch/sketch.ino` |

---

<a id="s40"></a>
## 🛠️ การแก้ปัญหาที่พบบ่อย (Troubleshooting & FAQ)

#### Q1: ภาพจากกล้อง USB ไม่แสดง หรือขึ้นข้อความแจ้งว่ากล้องเปิดไม่ได้?
- **สาเหตุ**: บนบอร์ด Arduino UNO Q กล้อง USB มาตรฐาน UVC อาจถูกแมปเป็นอุปกรณ์ตำแหน่งอื่น เช่น `/dev/video2` หรือ `/dev/video0`
- **วิธีแก้ปัญหา**: สคริปต์ `open_usb_camera()` ในโค้ดปัจจุบันถูกออกแบบให้ทดสอบเปิดกล้องตามลำดับ `[2, 0, 1]` โดยอัตโนมัติแล้ว หากยังไม่ติด ให้ตรวจสอบว่าเสียบสาย USB แน่นหรือไม่ หรือลองถอดสายกล้องออกแล้วเสียบใหม่ จากนั้นตรวจสอบว่าไฟ LED บนตัวกล้องติดสว่างหรือไม่

#### Q2: มอเตอร์เซอร์โวสั่นกระตุก หรือมีเสียงฮัมตลอดเวลาแม้ไม่มีไฟ?
- **สาเหตุ**: เกิดจากสัญญาณคลื่น PWM 50Hz ถูกส่งไปยังเซอร์โวค้างไว้ตลอดเวลา
- **วิธีแก้ปัญหา**: โค้ดในโปรเจกต์นี้ได้รับการแก้ไขด้วยระบบ **Zero-Jitter Control** โดยสั่ง `detach_servo()` ตัดสัญญาณ PWM ทันทีที่เข้าสู่สถานะ Standby หากเซอร์โวยังคงสั่น ให้ตรวจสอบสายกราว (GND) ระหว่างบอร์ดกับเซอร์โวว่าต่อร่วมกันแน่นหนาดีหรือไม่

#### Q3: นำเข้าแอปแล้วเจอ Error: Model file is not executable?
- **สาเหตุ**: ไฟล์โมเดล `.eim` ถูกบีบอัดในระบบปฏิบัติการ Windows ทำให้ค่า Permission การรันไฟล์ (Execute bit) สูญหายไป
- **วิธีแก้ปัญหา**: ในสคริปต์ `python/main.py` ได้เพิ่มคำสั่ง `os.chmod()` ให้โดยอัตโนมัติก่อนเริ่มโหลดโมเดล หากยังพบปัญหา ให้ตรวจ Logs ว่ามีข้อความ `Warning setting chmod on model` หรือไม่ และตรวจว่า build โมเดลเป็น **Linux (AARCH64)**

#### Q6: ไม่ได้รับข้อความ Telegram เลย?
- ดูสถานะ `Last Gateway Status` บนแดชบอร์ด:
  - `Failed (Invalid Token)`: ยังไม่ได้ใส่ `TELEGRAM_TOKEN`
  - `Failed (401)`: Token ผิดหรือถูก revoke แล้ว
  - `Failed (400)`: Chat ID ผิด หรือยังไม่ได้กด `/start` กับบอท
  - `Error: ...`: บอร์ดออกอินเทอร์เน็ตไม่ได้ ให้ตรวจ Wi-Fi
- ระบบส่งได้ไม่เกิน 1 ข้อความทุก 20 วินาที (`TELEGRAM_COOLDOWN`) ข้อความที่อยู่ในช่วงนี้จะถูกข้าม

#### Q4: ค่าควันจากเซนเซอร์ MQ-2 อ่านได้ 50 ppm นิ่งๆ หรือแกว่งสูงมาก?
- **สาเหตุ**: เซนเซอร์ตระกูล MQ ทุกรุ่นจำเป็นต้องใช้เวลาอุ่นเครื่อง (Burn-in) หลังจากเสียบไฟประมาณ 3–5 นาที
- **วิธีแก้ปัญหา**: ให้รอสักครู่เพื่อให้ขดลวดความร้อนภายในเซนเซอร์ทำงานคงที่ จากนั้นทดสอบนำควันธูปหรือก๊าซไฟแช็กมาจ่อใกล้ๆ จะพบว่าค่าดิบ ADC และค่า ppm ดีดตัวสูงขึ้นอย่างชัดเจน

#### Q5: เปลี่ยนโมเดล AI ใหม่แล้ว แต่ทำไมระบบยังทำงานเหมือนโมเดลเก่า?
- **สาเหตุ**: Arduino App Lab อาจมีการบันทึกแคชของคอนเทนเนอร์เดิมไว้
- **วิธีแก้ปัญหา**: ให้ปฏิบัติตามคู่มือใน [ขั้นตอนที่ 4: การลบแอปเดิมและ Import ใหม่](#s27) โดยการ **กด Stop $\rightarrow$ ลบแอปเดิมทิ้ง (Delete) $\rightarrow$ Import ไฟล์ Zip ตัวใหม่เข้ามาใหม่** จะทำให้ระบบสร้างสภาพแวดล้อมใหม่และโหลดโมเดลใหม่อย่างแน่นอน
