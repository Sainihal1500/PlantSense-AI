/**
 * PlantSense AI - Node.js Express Mock / Simulation Server (Optional)
 * Primary production backend is Python Flask in app.py.
 * This server provides an alternative lightweight simulation for Node environments.
 */
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;


// Serve static files from the 'public' folder (where your HTML will live)
app.use(express.static('public'));

// Mock sensor state to create realistic fluctuations
let currentMoisture = 65;
let currentTemp = 24.0;

app.get('/get-data', (req, res) => {
    // Fluctuate data slightly for realistic chart movement
    currentMoisture += (Math.random() * 4 - 2);
    currentTemp += (Math.random() * 1 - 0.5);

    // Clamp values
    currentMoisture = Math.max(10, Math.min(100, currentMoisture));
    currentTemp = Math.max(15, Math.min(35, currentTemp));

    const signalStrength = Math.floor(Math.random() * 20) + 80; // 80-100%

    // AI Logic Simulation
    let status = "Healthy";
    let issues = [];
    let advice = "Conditions are optimal. Keep it up!";

    if (currentMoisture < 30) {
        status = "Warning";
        issues.push("Low Moisture");
        advice = "Soil is getting dry. Prepare to water soon.";
    } else if (currentMoisture > 85) {
        status = "Warning";
        issues.push("Overwatered");
        advice = "Hold off on watering to prevent root rot.";
    }

    if (currentTemp > 30) {
        status = currentMoisture < 30 ? "Critical" : "Warning";
        issues.push("High Heat");
        advice = status === "Critical" ? "Immediate watering and shade required!" : "Move plant to a cooler spot.";
    }

    const payload = [{
        moisture: currentMoisture.toFixed(1),
        temperature: currentTemp.toFixed(1),
        signal: signalStrength,
        plant: "Monstera Deliciosa",
        status: status,
        issues: issues.length > 0 ? issues : ["None"],
        advice: advice
    }];

    res.json(payload);
});

app.listen(PORT, () => {
    console.log(`🌱 Eco-Server running at http://localhost:${PORT}`);
});
