const socket = io();

// DOM Elements
const socketStatusDot = document.getElementById('socket-status');
const socketStatusText = document.getElementById('socket-text');
const videoFeed = document.getElementById('video-feed');
const qrContainer = document.getElementById('qr-container');
const qrCodeDiv = document.getElementById('qr-code');
const qrSecretText = document.getElementById('qr-secret-text');

const fireConfEl = document.getElementById('fire-conf');
const smokeConfEl = document.getElementById('smoke-conf');
const fireBar = document.getElementById('fire-bar');
const smokeBar = document.getElementById('smoke-bar');
const fireSlider = document.getElementById('fire-slider');
const fireThValue = document.getElementById('fire-th-value');
const smokeSlider = document.getElementById('smoke-slider');
const smokeThValue = document.getElementById('smoke-th-value');

const telCount = document.getElementById('tel-count');
const telLastStatus = document.getElementById('tel-last-status');
const telHistory = document.getElementById('tel-history');

// Hardware Elements
const mq2RawValEl = document.getElementById('mq2-raw-val');
const dhtTempEl = document.getElementById('dht-temp');
const dhtHumEl = document.getElementById('dht-hum');
const dhtTempBar = document.getElementById('dht-temp-bar');
const dhtHumBar = document.getElementById('dht-hum-bar');
const aiTargetTitle = document.getElementById('ai-target-title');
const fireSliderLabel = document.getElementById('fire-slider-label');

const servoBadgeEl = document.getElementById('servo-badge');
const servoAngleEl = document.getElementById('servo-angle');
const servoCooldownRow = document.getElementById('servo-cooldown-row');
const servoCooldownTimer = document.getElementById('servo-cooldown-timer');

// State
let fireThreshold = 80;
let smokeThreshold = 600;
let appMode = "WEBCAM"; // default
let webcamState = {
    status: "disconnected",
    secret: null,
    protocol: "",
    ip: "",
    port: 0
};

// Video feed configuration (iframe for Mobile mode)
const currentHostname = window.location.hostname;
const targetPort = 4912;
const targetPath = '/embed';
const streamUrl = `http://${currentHostname}:${targetPort}${targetPath}`;
const mobileIframe = document.getElementById('mobile-iframe');

let detectionTimeout = null;

// --- State Update UI Display ---
function updateDisplay() {
    if (appMode !== "MOBILE") {
        videoFeed.style.display = 'block';
        qrContainer.style.display = 'none';
        mobileIframe.style.display = 'none';
        return;
    }

    console.log("Updating display. Status:", webcamState.status);
    if (webcamState.status === "streaming") {
        videoFeed.style.display = 'none';
        qrContainer.style.display = 'none';
        mobileIframe.style.display = 'block';
        if (!mobileIframe.src || mobileIframe.src === "" || !mobileIframe.src.includes(streamUrl)) {
            mobileIframe.src = streamUrl;
        }
    } else if (webcamState.status === "connected") {
        videoFeed.style.display = 'block';
        videoFeed.src = "https://via.placeholder.com/640x480.png?text=Connected.+Starting+stream...";
        qrContainer.style.display = 'none';
        mobileIframe.style.display = 'none';
        mobileIframe.src = "";
        resetDetections();
    } else if (webcamState.status === "paused") {
        videoFeed.style.display = 'block';
        videoFeed.src = "https://via.placeholder.com/640x480.png?text=Webcam+paused";
        qrContainer.style.display = 'none';
        mobileIframe.style.display = 'none';
        mobileIframe.src = "";
        resetDetections();
    } else {
        // disconnected - show QR code
        videoFeed.style.display = 'none';
        mobileIframe.style.display = 'none';
        qrContainer.style.display = 'block';
        mobileIframe.src = "";
        resetDetections();
        if (webcamState.secret) {
            generateQRCode(webcamState.secret, webcamState.protocol, webcamState.ip, webcamState.port);
        }
    }
}

// Reset detection indicators back to 0.0%
function resetDetections() {
    if (detectionTimeout) {
        clearTimeout(detectionTimeout);
        detectionTimeout = null;
    }
    updateDetectionUI(0, 50, 0);
}

// Update the fire/smoke text and progress bar displays
function updateDetectionUI(fireVal, smokePpm, rawVal) {
    fireConfEl.innerText = fireVal.toFixed(1) + '%';
    smokeConfEl.innerText = Math.round(smokePpm) + ' ppm';

    fireBar.style.width = Math.min(100, Math.max(0, fireVal)).toFixed(0) + '%';
    
    // Scale smoke bar based on 0 - 3000 ppm
    let smokePercent = Math.min(100, Math.max(0, (smokePpm / 3000.0) * 100));
    smokeBar.style.width = smokePercent.toFixed(0) + '%';

    if (rawVal !== undefined && mq2RawValEl) {
        mq2RawValEl.innerText = rawVal;
    }

    if (fireVal >= fireThreshold) {
        fireConfEl.className = 'conf-value red';
    } else {
        fireConfEl.className = 'conf-value green';
    }

    if (smokePpm >= smokeThreshold) {
        smokeConfEl.className = 'conf-value red';
    } else {
        smokeConfEl.className = 'conf-value green';
    }
}

// Update DHT22 Temperature and Humidity Displays
function updateEnvironmentUI(temp, hum) {
    if (temp !== undefined && dhtTempEl) {
        const tVal = parseFloat(temp);
        dhtTempEl.innerText = tVal.toFixed(1) + ' °C';
        if (dhtTempBar) {
            // Scale 0°C to 60°C
            const tPct = Math.min(100, Math.max(0, (tVal / 60.0) * 100));
            dhtTempBar.style.width = tPct.toFixed(0) + '%';
        }
    }

    if (hum !== undefined && dhtHumEl) {
        const hVal = parseFloat(hum);
        dhtHumEl.innerText = hVal.toFixed(1) + ' %';
        if (dhtHumBar) {
            // Scale 0% to 100%
            const hPct = Math.min(100, Math.max(0, hVal));
            dhtHumBar.style.width = hPct.toFixed(0) + '%';
        }
    }
}

// --- Dynamic Target Theming (Sync from Python Backend) ---
let currentTargetName = "Fire";
let currentTargetIcon = "🔥";
let currentAppTitle = "Fire & Smoke AI";

function applyTargetTheme(data) {
    if (!data) return;

    if (data.target_name) {
        currentTargetName = data.target_name;
    }
    if (data.target_icon) {
        currentTargetIcon = data.target_icon;
    } else {
        currentTargetIcon = (currentTargetName.toLowerCase() === "fire") ? "🔥" : "🎯";
    }
    if (data.app_title) {
        currentAppTitle = data.app_title;
    } else {
        currentAppTitle = (currentTargetName.toLowerCase() === "fire") 
            ? "Fire & Smoke AI" 
            : `${currentTargetName} Detection AI`;
    }

    // 1. Page Title
    document.title = `${currentAppTitle} Safeguard`;

    // 2. Header Brand (Icon & Title)
    const brandIconEl = document.getElementById('brand-icon') || document.querySelector('.brand-icon');
    if (brandIconEl) brandIconEl.innerText = currentTargetIcon;

    const brandTitleEl = document.getElementById('brand-title') || document.querySelector('.brand-text h1');
    if (brandTitleEl) brandTitleEl.innerText = currentAppTitle;

    // 3. Telemetry Title
    if (aiTargetTitle) {
        aiTargetTitle.innerText = `${currentTargetIcon} ${currentTargetName} Level (AI)`;
    }

    // 4. Slider Label & Help Text
    if (fireSliderLabel) {
        fireSliderLabel.innerText = `${currentTargetIcon} ${currentTargetName} Camera Threshold`;
    }
    const fireHelpEl = document.getElementById('fire-slider-help');
    if (fireHelpEl) {
        fireHelpEl.innerHTML = `Triggers Telegram alert &amp; Servo spray when AI ${currentTargetName.toLowerCase()} confidence &ge; threshold.`;
    }
}

// --- Socket.IO Events ---

socket.on('connect', () => {
    socketStatusDot.className = 'status-dot green';
    socketStatusText.innerText = 'Connected';
});

socket.on('disconnect', () => {
    socketStatusDot.className = 'status-dot red';
    socketStatusText.innerText = 'Disconnected';
    resetDetections();
});

// Used if mobile mode QR code is needed
socket.on('welcome', (msg) => {
    appMode = msg.mode || "WEBCAM";
    console.log("Welcome msg received:", msg);
    if (msg.fire_threshold !== undefined) {
        fireThreshold = parseFloat(msg.fire_threshold);
        if (fireSlider) fireSlider.value = fireThreshold;
        if (fireThValue) fireThValue.innerText = Math.round(fireThreshold) + '%';
    }
    if (msg.smoke_threshold !== undefined) {
        smokeThreshold = parseFloat(msg.smoke_threshold);
        if (smokeSlider) smokeSlider.value = smokeThreshold;
        if (smokeThValue) smokeThValue.innerText = Math.round(smokeThreshold) + ' ppm';
    }
    // Dynamic Theme from Python (One-place configuration)
    applyTargetTheme(msg);

    if (msg.temperature !== undefined || msg.humidity !== undefined) {
        updateEnvironmentUI(msg.temperature, msg.humidity);
    }
    if (appMode === "MOBILE") {
        webcamState.status = msg.status || "disconnected";
        webcamState.secret = msg.secret;
        webcamState.protocol = msg.protocol;
        webcamState.ip = msg.ip;
        webcamState.port = msg.port;
    }
    updateDisplay();
});

socket.on('connected', (message) => {
    console.log("Webcam connected!", message);
    if (appMode === "MOBILE") {
        webcamState.status = "connected";
        updateDisplay();
    }
});

socket.on('disconnected', (message) => {
    console.log("Webcam disconnected!", message);
    if (appMode === "MOBILE") {
        webcamState.status = "disconnected";
        updateDisplay();
    }
});

socket.on('streaming', (message) => {
    console.log("Webcam streaming started!", message);
    if (appMode === "MOBILE") {
        webcamState.status = "streaming";
        updateDisplay();
    }
});

socket.on('paused', (message) => {
    console.log("Webcam streaming paused!", message);
    if (appMode === "MOBILE") {
        webcamState.status = "paused";
        updateDisplay();
    }
});

// Receive base64 video frame for WEBCAM mode
socket.on('video_frame', (frameData) => {
    if (appMode === "WEBCAM") {
        qrContainer.style.display = 'none';
        mobileIframe.style.display = 'none';
        videoFeed.style.display = 'block';
        videoFeed.src = frameData;
    }
});

// Receive detection statistics (Fire from AI, Smoke from MQ-2 on A0)
socket.on('detection', (data) => {
    if (detectionTimeout) {
        clearTimeout(detectionTimeout);
    }

    const fireVal = data.fire || 0;
    const smokeVal = data.smoke_ppm !== undefined ? data.smoke_ppm : (data.smoke || 50);
    const rawVal = data.mq2_raw !== undefined ? data.mq2_raw : 0;

    updateDetectionUI(fireVal, smokeVal, rawVal);

    if (data.temperature !== undefined || data.humidity !== undefined) {
        updateEnvironmentUI(data.temperature, data.humidity);
    }

    applyTargetTheme(data);

    // Timeout to reset fire level if AI frame detection stops
    detectionTimeout = setTimeout(() => {
        updateDetectionUI(0, smokeVal, rawVal);
    }, 1500);
});

// Receive Servo status updates
socket.on('servo_status', (data) => {
    if (!data) return;
    const state = data.state || "STANDBY";
    const angle = data.angle !== undefined ? data.angle : 0;
    const rem = data.remaining_cooldown !== undefined ? data.remaining_cooldown : 0;

    if (servoAngleEl) {
        servoAngleEl.innerText = `${angle}°`;
    }

    if (servoBadgeEl) {
        servoBadgeEl.className = `servo-badge ${state.toLowerCase()}`;
        if (state === "COOLDOWN") {
            servoBadgeEl.innerText = "COOLDOWN";
        } else if (state === "ACTIVE") {
            servoBadgeEl.innerText = `ACTIVE (${angle}°)`;
        } else {
            servoBadgeEl.innerText = "STANDBY";
        }
    }

    if (servoCooldownRow && servoCooldownTimer) {
        if (state === "COOLDOWN" && rem > 0) {
            servoCooldownRow.style.display = 'flex';
            servoCooldownTimer.innerText = `${rem}s`;
        } else {
            servoCooldownRow.style.display = 'none';
        }
    }
});

// Receive telegram status updates
socket.on('telegram_status', (data) => {
    telCount.innerText = data.count;
    telLastStatus.innerText = data.last_status;

    if (data.last_status.toLowerCase().includes("success")) {
        telLastStatus.className = "stat-status success";
    } else if (data.last_status.toLowerCase().includes("failed") || data.last_status.toLowerCase().includes("error")) {
        telLastStatus.className = "stat-status failed";
    } else {
        telLastStatus.className = "stat-status waiting";
    }

    if (data.history && data.history.length > 0) {
        telHistory.innerHTML = '';
        data.history.forEach(ts => {
            const li = document.createElement('li');
            const d = new Date(ts);
            const timeStr = d.toLocaleTimeString();
            li.innerHTML = `<span>🚨 ${currentTargetName} Alert Notification Sent</span> <strong>${timeStr}</strong>`;
            telHistory.appendChild(li);
        });
    } else {
        telHistory.innerHTML = '<li class="no-history-placeholder">No alerts triggered in this session</li>';
    }
});

// --- UI Controls ---

if (fireSlider) {
    fireSlider.addEventListener('input', (e) => {
        fireThreshold = parseFloat(e.target.value);
        if (fireThValue) fireThValue.innerText = Math.round(fireThreshold) + '%';
    });

    fireSlider.addEventListener('change', (e) => {
        socket.emit('override_fire_th', parseFloat(e.target.value));
    });
}

if (smokeSlider) {
    smokeSlider.addEventListener('input', (e) => {
        smokeThreshold = parseFloat(e.target.value);
        if (smokeThValue) smokeThValue.innerText = Math.round(smokeThreshold) + ' ppm';
    });

    smokeSlider.addEventListener('change', (e) => {
        socket.emit('override_smoke_th', parseFloat(e.target.value));
    });
}

// --- QR Code Generator ---
function generateQRCode(secret, protocol, ip, port) {
    qrCodeDiv.innerHTML = '';
    qrSecretText.textContent = '';

    const text = `https://cloud.arduino.cc/installmobileapp?otp=${secret}&protocol=${protocol}&ip=${ip}&port=${port}`;
    console.log("Generating QR Code with text:", text);

    new QRCode(qrCodeDiv, {
        text: text,
        width: 200,
        height: 200,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.L,
    });

    qrSecretText.textContent = secret;
}
