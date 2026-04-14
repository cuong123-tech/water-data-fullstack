// Data State
let globalData = [];
let globalAnomalies = [];

// DOM Elements
const sensorSelect = document.getElementById('sensor-select');
const startTimeInput = document.getElementById('start-time');
const endTimeInput = document.getElementById('end-time');
const updateBtn = document.getElementById('update-btn');
const totReadings = document.getElementById('tot-readings');
const totAnomalies = document.getElementById('tot-anomalies');
const anomalyList = document.getElementById('anomaly-list');

// Initialize
async function init() {
    await fetchData();
    setupEventListeners();
    updateChart();
    updateSummary();
}

async function fetchData() {
    try {
        const start = startTimeInput.value ? new Date(startTimeInput.value).toISOString() : '';
        const end = endTimeInput.value ? new Date(endTimeInput.value).toISOString() : '';
        
        let url = '/data';
        if (start || end) {
            url += `?start=${start}&end=${end}`;
        }
        
        const resData = await fetch(url);
        const dataJson = await resData.json();
        globalData = dataJson.data;

        // Fetch anomalies
        const resAnom = await fetch('/anomalies');
        const anomJson = await resAnom.json();
        globalAnomalies = anomJson.anomalies;
        
        // Fetch summary
        const resSum = await fetch('/summary');
        const sumJson = await resSum.json();
        
        totReadings.textContent = sumJson.total_rows;
        totAnomalies.textContent = sumJson.total_anomalies;
        
    } catch (e) {
        console.error("Error fetching data:", e);
    }
}

function setupEventListeners() {
    sensorSelect.addEventListener('change', () => {
        updateChart();
        updateSummary();
    });
    
    updateBtn.addEventListener('click', async () => {
        await fetchData();
        updateChart();
        updateSummary();
    });
}

function updateChart() {
    const sensor = sensorSelect.value;
    const sensorName = sensorSelect.options[sensorSelect.selectedIndex].text;
    
    // Filter data for the selected sensor
    const timestamps = globalData.map(d => new Date(d.timestamp));
    const values = globalData.map(d => d[sensor]);
    
    // Find anomalies for this sensor
    const sensorAnomalies = globalAnomalies.filter(a => a.sensor === sensor);
    
    // Extract times and values for anomalies, constrained to current data window
    const anomTimes = [];
    const anomValues = [];
    const anomTexts = [];
    
    const minTime = timestamps.length > 0 ? timestamps[0].getTime() : 0;
    const maxTime = timestamps.length > 0 ? timestamps[timestamps.length-1].getTime() : Infinity;

    sensorAnomalies.forEach(a => {
        const t = new Date(a.timestamp);
        // Sometimes string parsing differs, just display all anomalies for simplicity
        if (t.getTime() >= (minTime - 1000) && t.getTime() <= (maxTime + 1000)) {
            anomTimes.push(t);
            anomValues.push(a.value);
            anomTexts.push(a.issue);
        }
    });

    const mainTrace = {
        x: timestamps,
        y: values,
        mode: 'lines',
        name: sensorName,
        line: { color: '#0ea5e9', width: 2 }
    };

    const anomalyTrace = {
        x: anomTimes,
        y: anomValues,
        mode: 'markers',
        name: 'Anomaly',
        marker: { 
            color: '#ef4444', 
            size: 10,
            line: { color: '#ffffff', width: 1 }
        },
        text: anomTexts,
        hoverinfo: 'text+x+y'
    };

    const layout = {
        title: {
            text: `${sensorName} over Time`,
            font: { color: '#e2e8f0', size: 18 }
        },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#94a3b8' },
        xaxis: {
            showgrid: true,
            gridcolor: 'rgba(56, 189, 248, 0.1)',
            zeroline: false
        },
        yaxis: {
            showgrid: true,
            gridcolor: 'rgba(56, 189, 248, 0.1)',
            zeroline: false
        },
        margin: { t: 50, r: 20, l: 50, b: 50 },
        legend: { orientation: 'h', y: -0.2 }
    };

    Plotly.newPlot('chart-container', [mainTrace, anomalyTrace], layout, {responsive: true});
}

function updateSummary() {
    const sensor = sensorSelect.value;
    const sensorAnomalies = globalAnomalies.filter(a => a.sensor === sensor);
    
    anomalyList.innerHTML = '';
    
    if (sensorAnomalies.length === 0) {
        anomalyList.innerHTML = '<li class="anomaly-item"><div class="anom-issue">No anomalies detected</div></li>';
        return;
    }
    
    sensorAnomalies.slice(0, 50).forEach(a => {
        const li = document.createElement('li');
        li.className = 'anomaly-item';
        
        const timeStr = new Date(a.timestamp).toLocaleString();
        
        li.innerHTML = `
            <div class="anom-time">${timeStr}</div>
            <div class="anom-issue">${a.method}</div>
            <div class="anom-details">${a.issue} <br/>(Value: <b>${a.value}</b>)</div>
        `;
        anomalyList.appendChild(li);
    });
}

// Start
document.addEventListener('DOMContentLoaded', init);
