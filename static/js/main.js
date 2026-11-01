/*
  main.js - Frontend Logic & Reactivity for Elderly & Career Intelligence Hub
  ByteLife Core Platform
*/

let skillChartInstance = null;
let vitalsChartInstance = null;
let latestHealthDiagnosis = {
  status: "Normal",
  summary: "All vitals are within normal baseline."
};

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initAccessibility();
  initHealthModule();
  initCareerModule();
  initDigitalMeModule();
  
  // Initial data loads
  fetchVitalsHistory();
  fetchAlertHistory();
});

/* ==========================================================
   1. Tab Navigation
   ========================================================== */
function initTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }

      if (targetId === "tab-history") {
        fetchVitalsHistory();
      } else if (targetId === "tab-alerts") {
        fetchAlertHistory();
      }
    });
  });
}

/* ==========================================================
   2. Accessibility Features (Senior Mode, High Contrast, TTS)
   ========================================================== */
function initAccessibility() {
  const btnSenior = document.getElementById("btnSeniorMode");
  const btnContrast = document.getElementById("btnContrast");
  const btnSpeech = document.getElementById("btnSpeech");

  // Restore saved preferences
  if (localStorage.getItem("senior-mode") === "true") {
    document.body.classList.add("senior-mode");
    btnSenior.classList.add("active");
  }
  if (localStorage.getItem("high-contrast") === "true") {
    document.body.classList.add("high-contrast");
    btnContrast.classList.add("active");
  }

  btnSenior.addEventListener("click", () => {
    document.body.classList.toggle("senior-mode");
    const isActive = document.body.classList.contains("senior-mode");
    btnSenior.classList.toggle("active", isActive);
    localStorage.setItem("senior-mode", isActive);
  });

  btnContrast.addEventListener("click", () => {
    document.body.classList.toggle("high-contrast");
    const isActive = document.body.classList.contains("high-contrast");
    btnContrast.classList.toggle("active", isActive);
    localStorage.setItem("high-contrast", isActive);
  });

  btnSpeech.addEventListener("click", () => {
    speakHealthStatus();
  });
}

function speakHealthStatus() {
  if (!("speechSynthesis" in window)) {
    alert("Speech Synthesis (text-to-speech) is not supported in this browser.");
    return;
  }
  window.speechSynthesis.cancel();
  const textToSpeak = `Health Evaluation Alert. Status is ${latestHealthDiagnosis.status}. ${latestHealthDiagnosis.summary}`;
  const utterance = new SpeechSynthesisUtterance(textToSpeak);
  utterance.rate = 0.9; // Slightly slower for elderly comprehension
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

/* ==========================================================
   3. Health Vitals Monitoring Module
   ========================================================== */
const PRESETS = {
  normal: { hr: 74, sys: 116, dia: 76, spo2: 98.2, temp: 98.4 },
  bp_crisis: { hr: 104, sys: 188, dia: 122, spo2: 96.0, temp: 98.6 },
  hypoxia: { hr: 124, sys: 112, dia: 72, spo2: 86.5, temp: 98.8 },
  fever_tachy: { hr: 118, sys: 134, dia: 86, spo2: 93.5, temp: 102.6 },
  hypotension: { hr: 110, sys: 78, dia: 46, spo2: 95.0, temp: 96.2 }
};

function loadPreset(key) {
  const data = PRESETS[key];
  if (!data) return;
  document.getElementById("heartRate").value = data.hr;
  document.getElementById("systolicBp").value = data.sys;
  document.getElementById("diastolicBp").value = data.dia;
  document.getElementById("spo2").value = data.spo2;
  document.getElementById("temperature").value = data.temp;

  // Auto trigger analysis
  document.getElementById("healthForm").dispatchEvent(new Event("submit"));
}

function initHealthModule() {
  const form = document.getElementById("healthForm");
  const btnEvaluate = document.getElementById("btnEvaluate");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    btnEvaluate.disabled = true;
    btnEvaluate.innerHTML = "<span>⏳</span> Analyzing Vitals with AI...";

    const payload = {
      patient_name: document.getElementById("patientName").value,
      recipient_email: document.getElementById("caretakerEmail").value,
      heart_rate: parseFloat(document.getElementById("heartRate").value),
      systolic_bp: parseFloat(document.getElementById("systolicBp").value),
      diastolic_bp: parseFloat(document.getElementById("diastolicBp").value),
      spo2: parseFloat(document.getElementById("spo2").value),
      temperature: parseFloat(document.getElementById("temperature").value),
      auto_alert: document.getElementById("autoAlert").checked
    };

    try {
      const response = await fetch("/api/predict-health", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const res = await response.json();
      if (!response.ok) {
        alert("Error: " + (res.error || "Failed to analyze vitals"));
        return;
      }

      renderHealthResults(res);
    } catch (err) {
      console.error(err);
      alert("Network error communicating with Flask backend.");
    } finally {
      btnEvaluate.disabled = false;
      btnEvaluate.innerHTML = "<span>🩺</span> Analyze Patient Vitals";
    }
  });
}

function renderHealthResults(res) {
  const banner = document.getElementById("statusBanner");
  const title = document.getElementById("statusTitle");
  const desc = document.getElementById("statusDesc");
  const badge = document.getElementById("statusCodeBadge");
  const mlText = document.getElementById("mlPredictionText");
  const ruleText = document.getElementById("ruleOverrideText");
  const overrideAlertBox = document.getElementById("overrideAlertBox");
  const overrideReasonText = document.getElementById("overrideReasonText");
  const confidenceBadge = document.getElementById("confidenceBadge");

  // Update Status Banner
  const status = res.status_label; // Normal, Abnormal, Critical
  banner.className = `status-banner ${status.toLowerCase()}`;
  badge.className = `badge-tag tag-${status.toLowerCase()}`;
  badge.innerText = `STATUS: ${status.toUpperCase()}`;

  const icon = status === "Normal" ? "🟢" : (status === "Abnormal" ? "🟠" : "🔴");
  title.innerHTML = `<span>${icon}</span> ${status.toUpperCase()} Physiological Status`;

  if (status === "Critical") {
    desc.innerText = "CRITICAL ALERT: Vitals indicate acute distress. Immediate caretaker action required!";
  } else if (status === "Abnormal") {
    desc.innerText = "CAUTION: Irregular vital readings detected. Observation and soothing protocols recommended.";
  } else {
    desc.innerText = "All evaluated vitals are within healthy clinical baseline parameters.";
  }

  // Update Safety Analysis Card
  mlText.innerText = `${res.ml_predicted_label} (${res.ml_predicted_class})`;
  confidenceBadge.innerText = `Confidence: ${res.ml_confidence_percentage}%`;

  if (res.rule_override) {
    ruleText.innerText = "FAILSAFE OVERRIDE ACTIVE";
    ruleText.style.color = "#dc2626";
    overrideAlertBox.style.display = "block";
    overrideReasonText.innerText = res.override_reason;
  } else {
    ruleText.innerText = "Safe (No Overrides)";
    ruleText.style.color = "#16a34a";
    overrideAlertBox.style.display = "none";
  }

  // Update Probabilities
  const probs = res.probabilities || { Normal: 0.9, Abnormal: 0.05, Critical: 0.05 };
  const pNorm = Math.round((probs.Normal || 0) * 100);
  const pAbn = Math.round((probs.Abnormal || 0) * 100);
  const pCrit = Math.round((probs.Critical || 0) * 100);

  document.getElementById("probNormal").innerText = `${pNorm}%`;
  document.getElementById("probAbnormal").innerText = `${pAbn}%`;
  document.getElementById("probCritical").innerText = `${pCrit}%`;

  document.getElementById("barNormal").style.width = `${pNorm}%`;
  document.getElementById("barAbnormal").style.width = `${pAbn}%`;
  document.getElementById("barCritical").style.width = `${pCrit}%`;

  // Render Remedies
  const remediesContainer = document.getElementById("remediesContainer");
  remediesContainer.innerHTML = "";
  (res.remedies || []).forEach(r => {
    const item = document.createElement("div");
    item.className = `remedy-item ${r.urgent ? "urgent" : ""}`;
    item.innerHTML = `
      <h4>${r.urgent ? "🚨 " : "✓ "}${r.title} <span style="font-size:0.75rem; font-weight:normal; color:#64748b;">(${r.category})</span></h4>
      <p>${r.description}</p>
    `;
    remediesContainer.appendChild(item);
  });

  // Render Alert Feedback
  const alertBox = document.getElementById("alertFeedbackBox");
  if (res.alert_info) {
    alertBox.style.display = "block";
    alertBox.className = `alert-dispatch-box ${status.toLowerCase()}-box`;
    document.getElementById("alertModeBadge").innerText = res.alert_info.mode.toUpperCase();
    document.getElementById("alertMsgText").innerText = res.alert_info.message;
    document.getElementById("alertRefId").innerText = res.alert_info.message_id || "N/A";
    document.getElementById("alertRecipientText").innerText = res.alert_info.recipient || "caretaker@bytelife.ai";
  } else {
    alertBox.style.display = "none";
  }

  // Update text-to-speech context
  latestHealthDiagnosis = {
    status: status,
    summary: (res.remedies && res.remedies[0]) ? res.remedies[0].description : "Monitoring active."
  };

  // If Critical, auto-speak if user wants quick feedback
  if (status === "Critical") {
    speakHealthStatus();
  }
}

/* ==========================================================
   4. Career & Skill Intelligence Module
   ========================================================== */
const PRANITH_SAMPLE_RESUME = `
Pranith Kumar Dupuguntla
Role: Data Analyst & AI Enthusiast | Hyderabad, India
Education: B.Tech in CSE (Data Science), ACE Engineering College (2023–2026)

Technical Skills:
- Power BI: DAX, Power Query, Data Modeling, Dashboard Development, KPI Reporting, Data Visualization
- Microsoft Excel: Pivot Tables, XLOOKUP, INDEX-MATCH, Advanced Formulas, Data Validation
- Python: Pandas, NumPy, Matplotlib, Statistical Analysis, Data Cleaning, Predictive Analytics, Scikit-learn
- Data Analytics: ETL, Business Intelligence, Business Analytics, Trend Analysis, Reporting Automation

Key Projects:
1. Hospital Management Dashboard: Analyzed patient demographics, admissions, billing, BMI, blood pressure, and cholesterol using Power BI and DAX measures.
2. Smoking Health Analysis Dashboard: Designed dashboard analyzing smoking behavior and health indicators using DAX and Power Query for preventive healthcare.
3. Employee Performance Dashboard: Automated performance reporting with Excel Pivot Tables, Charts, and KPI cards.
`;

function loadPranithProfile() {
  document.getElementById("resumeText").value = PRANITH_SAMPLE_RESUME.trim();
  document.getElementById("targetRoleSelect").value = "Data Analyst";
  document.getElementById("careerForm").dispatchEvent(new Event("submit"));
}

function initCareerModule() {
  const form = document.getElementById("careerForm");
  const btnAnalyze = document.getElementById("btnAnalyzeCareer");

  // Load sample on first open
  document.getElementById("resumeText").value = PRANITH_SAMPLE_RESUME.trim();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    btnAnalyze.disabled = true;
    btnAnalyze.innerHTML = "<span>⏳</span> Analyzing Skills & Role Taxonomy...";

    const payload = {
      resume_text: document.getElementById("resumeText").value,
      target_role: document.getElementById("targetRoleSelect").value
    };

    try {
      const response = await fetch("/api/analyze-skills", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      renderCareerResults(data);
    } catch (err) {
      console.error(err);
      alert("Failed to analyze career skills.");
    } finally {
      btnAnalyze.disabled = false;
      btnAnalyze.innerHTML = "<span>🎯</span> Perform Skill Gap Analysis";
    }
  });

  // Run initial career analysis
  form.dispatchEvent(new Event("submit"));
}

function renderCareerResults(data) {
  const target = data.target_evaluation;
  if (!target) return;

  // Match badge
  const matchPct = target.match_percentage;
  const badge = document.getElementById("careerMatchBadge");
  badge.innerText = `${matchPct}% MATCH`;
  badge.className = `badge-tag ${matchPct >= 80 ? "tag-normal" : (matchPct >= 50 ? "tag-abnormal" : "tag-critical")}`;

  document.getElementById("careerVerdictText").innerText =
    `${data.readiness_summary.verdict} for ${target.role}`;

  // Matched Skills
  const matchedContainer = document.getElementById("matchedSkillsList");
  matchedContainer.innerHTML = "";
  if (target.matched_skills && target.matched_skills.length > 0) {
    target.matched_skills.forEach(s => {
      const pill = document.createElement("span");
      pill.className = "skill-pill matched";
      pill.innerText = `✓ ${s}`;
      matchedContainer.appendChild(pill);
    });
  } else {
    matchedContainer.innerHTML = "<span style='color:#64748b;'>No direct taxonomy matches detected.</span>";
  }

  // Missing Skills
  const missingContainer = document.getElementById("missingSkillsList");
  missingContainer.innerHTML = "";
  if (target.missing_skills && target.missing_skills.length > 0) {
    target.missing_skills.forEach(s => {
      const pill = document.createElement("span");
      pill.className = "skill-pill missing";
      pill.innerText = `+ ${s}`;
      missingContainer.appendChild(pill);
    });
  } else {
    missingContainer.innerHTML = "<span style='color:#16a34a; font-weight:bold;'>All benchmark skills covered!</span>";
  }

  // Upskilling Roadmap
  const roadmapContainer = document.getElementById("roadmapList");
  roadmapContainer.innerHTML = "";
  if (data.upskilling_roadmap && data.upskilling_roadmap.length > 0) {
    data.upskilling_roadmap.forEach((step, idx) => {
      const item = document.createElement("div");
      item.className = "roadmap-step";
      item.innerHTML = `
        <div class="roadmap-num">${idx + 1}</div>
        <div class="roadmap-content">
          <h5>${step.skill} <span style="font-size:0.75rem; font-weight:normal; color:#d97706;">(${step.priority})</span></h5>
          <p>${step.action}</p>
        </div>
      `;
      roadmapContainer.appendChild(item);
    });
  } else {
    roadmapContainer.innerHTML = "<p style='color:#64748b;'>Target role profile is fully matched. Explore advanced specialty certifications.</p>";
  }

  // Render Radar/Bar Chart
  renderSkillChart(target.subscores, target.role);
}

function renderSkillChart(subscores, roleName) {
  const ctx = document.getElementById("skillRadarChart");
  if (!ctx) return;

  const labels = ["Core Toolset", "Domain Analytics", "Operational Readiness"];
  const values = [
    subscores.core_competence || 0,
    subscores.domain_analytics || 0,
    subscores.operational_readiness || 0
  ];

  if (skillChartInstance) {
    skillChartInstance.destroy();
  }

  skillChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: `${roleName} Proficiency (%)`,
        data: values,
        backgroundColor: [
          "rgba(37, 99, 235, 0.7)",
          "rgba(16, 185, 129, 0.7)",
          "rgba(245, 158, 11, 0.7)"
        ],
        borderColor: [
          "#2563eb",
          "#10b981",
          "#f59e0b"
        ],
        borderWidth: 1.5,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: value => value + "%"
          }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

/* ==========================================================
   5. Vitals History & Trends Chart
   ========================================================== */
async function fetchVitalsHistory() {
  try {
    const res = await fetch("/api/vitals-history");
    const data = await res.json();
    const history = data.history || [];

    renderVitalsTable(history);
    renderVitalsChart(history);
  } catch (err) {
    console.error("Failed to load vitals history:", err);
  }
}

function renderVitalsTable(history) {
  const tbody = document.getElementById("vitalsTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (history.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:#64748b;">No vital records saved yet. Perform an analysis on the Health Monitoring tab.</td></tr>`;
    return;
  }

  history.forEach(item => {
    const v = item.vitals || {};
    const tr = document.createElement("tr");
    const statusClass = item.status_label ? item.status_label.toLowerCase() : "normal";

    tr.innerHTML = `
      <td>${item.timestamp}</td>
      <td><strong>${item.patient_name || "Patient"}</strong></td>
      <td><span class="badge-tag tag-${statusClass}">${item.status_label || "Normal"}</span></td>
      <td>${v.heart_rate || "N/A"} bpm</td>
      <td>${v.systolic_bp || "N/A"} / ${v.diastolic_bp || "N/A"} mmHg</td>
      <td>${v.spo2 || "N/A"}%</td>
      <td>${v.temperature || "N/A"} °F</td>
      <td>${item.rule_override ? "<span style='color:#dc2626; font-weight:bold;'>Override Active</span>" : "<span style='color:#16a34a;'>Safe</span>"}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderVitalsChart(history) {
  const ctx = document.getElementById("vitalsHistoryChart");
  if (!ctx) return;

  const reversed = [...history].reverse(); // chronological order
  const labels = reversed.map(h => (h.timestamp ? h.timestamp.split(" ")[1] : ""));
  const hrData = reversed.map(h => (h.vitals ? h.vitals.heart_rate : null));
  const sysData = reversed.map(h => (h.vitals ? h.vitals.systolic_bp : null));
  const spo2Data = reversed.map(h => (h.vitals ? h.vitals.spo2 : null));

  if (vitalsChartInstance) {
    vitalsChartInstance.destroy();
  }

  vitalsChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Heart Rate (bpm)",
          data: hrData,
          borderColor: "#dc2626",
          backgroundColor: "rgba(220, 38, 38, 0.1)",
          tension: 0.3,
          yAxisID: "y"
        },
        {
          label: "Systolic BP (mmHg)",
          data: sysData,
          borderColor: "#2563eb",
          backgroundColor: "rgba(37, 99, 235, 0.1)",
          tension: 0.3,
          yAxisID: "y"
        },
        {
          label: "SpO2 (%)",
          data: spo2Data,
          borderColor: "#16a34a",
          backgroundColor: "rgba(22, 163, 74, 0.1)",
          tension: 0.3,
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          type: "linear",
          display: true,
          position: "left",
          title: { display: true, text: "Pulse (bpm) / BP (mmHg)" }
        },
        y1: {
          type: "linear",
          display: true,
          position: "right",
          min: 70,
          max: 100,
          grid: { drawOnChartArea: false },
          title: { display: true, text: "SpO2 (%)" }
        }
      }
    }
  });
}

/* ==========================================================
   6. Caretaker Alerts History
   ========================================================== */
async function fetchAlertHistory() {
  try {
    const res = await fetch("/api/alerts-history");
    const data = await res.json();
    const alerts = data.alerts || [];

    const tbody = document.getElementById("alertsTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (alerts.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#64748b;">No alerts recorded yet. Trigger an abnormal/critical test on the Health Monitoring tab.</td></tr>`;
      return;
    }

    alerts.forEach(a => {
      const tr = document.createElement("tr");
      const level = (a.alert_level || "Critical").toLowerCase();
      tr.innerHTML = `
        <td><code>${a.message_id || "N/A"}</code></td>
        <td><strong>${a.patient_name || "Patient"}</strong></td>
        <td><span class="badge-tag tag-${level}">${(a.alert_level || "Critical").toUpperCase()}</span></td>
        <td>${a.recipient || "N/A"}</td>
        <td>${a.timestamp || "N/A"}</td>
        <td><span class="badge-tag tag-normal">${(a.mode || "Simulated").toUpperCase()}</span></td>
        <td style="font-size:0.8rem; color:#475569;">${a.override_reason ? a.override_reason.slice(0, 50) + "..." : "Standard triage dispatch"}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load alerts history:", err);
  }
}

/* ==========================================================
   7. Digital Me (AI Digital Twin) Interactive Controller
   ========================================================== */
let isDigitalMeAudioActive = true;

function initDigitalMeModule() {
  const form = document.getElementById("digitalMeForm");
  const input = document.getElementById("digitalMeInput");

  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleDigitalMeSubmit(e);
      }
    });
  }
}

function toggleDigitalMeAudio() {
  isDigitalMeAudioActive = !isDigitalMeAudioActive;
  const statusEl = document.getElementById("audioStatusText");
  const iconEl = document.getElementById("audioIcon");
  if (statusEl) statusEl.textContent = isDigitalMeAudioActive ? "ON" : "OFF";
  if (iconEl) iconEl.textContent = isDigitalMeAudioActive ? "🔊" : "🔇";
}

function askDigitalMePrompt(text) {
  const input = document.getElementById("digitalMeInput");
  if (!input) return;
  input.value = text;
  handleDigitalMeSubmit(new Event("submit"));
}

function clearDigitalMeChat() {
  const container = document.getElementById("digitalMeChatMessages");
  if (!container) return;
  container.innerHTML = `
    <div class="chat-bubble-row bot-row">
      <div class="chat-avatar bot-avatar">👨‍💻</div>
      <div class="chat-bubble bot-bubble">
        <div class="bubble-header">
          <strong>Pranith Kumar Dupuguntla (Digital Twin)</strong>
          <span class="bubble-time">Just now</span>
        </div>
        <div class="bubble-body">
          Conversation cleared. Feel free to ask another question about my <strong>ByteLife</strong> system, 
          <strong>IJIRSET research paper</strong>, <strong>Power BI dashboards</strong>, or educational background!
        </div>
      </div>
    </div>
  `;
}

function formatMarkdownToHtml(text) {
  if (!text) return "";
  let html = text
    // Escape HTML tags to prevent XSS
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    // Headers: ### Header
    .replace(/^### (.*$)/gim, "<h4>$1</h4>")
    .replace(/^## (.*$)/gim, "<h3>$1</h3>")
    // Bold: **text**
    .replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>")
    // Italic: *text*
    .replace(/\*(.*?)\*/gim, "<em>$1</em>")
    // Links: [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:#0284c7; text-decoration:underline;">$1</a>')
    // Bullet lists: - item
    .replace(/^\s*-\s+(.*$)/gim, "<li>$1</li>")
    // Wrap consecutive <li> into <ul>
    .replace(/(<li>.*?<\/li>(\s*<li>.*?<\/li>)*)/gis, "<ul>$1</ul>")
    // Newlines to breaks (double newline to paragraph)
    .replace(/\n\n+/g, "<br><br>")
    .replace(/\n/g, "<br>");

  return html;
}

async function handleDigitalMeSubmit(e) {
  if (e && e.preventDefault) e.preventDefault();

  const input = document.getElementById("digitalMeInput");
  const sendBtn = document.getElementById("digitalMeSendBtn");
  const messagesBox = document.getElementById("digitalMeChatMessages");
  if (!input || !messagesBox) return;

  const query = input.value.trim();
  if (!query) return;

  // 1. Append User Bubble
  const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const userHtml = `
    <div class="chat-bubble-row user-row">
      <div class="chat-avatar user-avatar">👤</div>
      <div class="chat-bubble user-bubble">
        <div class="bubble-header">
          <strong>You</strong>
          <span class="bubble-time" style="color:rgba(255,255,255,0.8);">${now}</span>
        </div>
        <div class="bubble-body">${query}</div>
      </div>
    </div>
  `;
  messagesBox.insertAdjacentHTML("beforeend", userHtml);
  input.value = "";
  messagesBox.scrollTop = messagesBox.scrollHeight;

  // 2. Append Typing Indicator
  const typingId = "typingIndicator_" + Date.now();
  const typingHtml = `
    <div class="chat-bubble-row bot-row" id="${typingId}">
      <div class="chat-avatar bot-avatar">👨‍💻</div>
      <div class="chat-bubble bot-bubble">
        <div class="typing-dots">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
        <span style="font-size:0.8rem; color:#64748b; margin-left:6px;">Retrieving from ChromaDB & synthesizing...</span>
      </div>
    </div>
  `;
  messagesBox.insertAdjacentHTML("beforeend", typingHtml);
  messagesBox.scrollTop = messagesBox.scrollHeight;

  if (sendBtn) sendBtn.disabled = true;

  try {
    const res = await fetch("/api/digital_me/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query })
    });

    const data = await res.json();
    const typingEl = document.getElementById(typingId);
    if (typingEl) typingEl.remove();

    const responseText = data.response || "No response received.";
    const formattedBody = formatMarkdownToHtml(responseText);

    // Build Sources List if available
    let sourcesHtml = "";
    if (data.sources && data.sources.length > 0) {
      const items = data.sources
        .map(s => `<span class="source-item" title="${s.snippet || ''}">📚 ${s.title || s.source}</span>`)
        .join("");
      sourcesHtml = `
        <div class="sources-container">
          <span class="sources-label">Verified Knowledge References:</span>
          ${items}
        </div>
      `;
    }

    const botHtml = `
      <div class="chat-bubble-row bot-row">
        <div class="chat-avatar bot-avatar">👨‍💻</div>
        <div class="chat-bubble bot-bubble">
          <div class="bubble-header">
            <strong>Pranith Kumar Dupuguntla (Digital Twin)</strong>
            <span class="bubble-time">${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
          </div>
          <div class="bubble-body">${formattedBody}</div>
          ${sourcesHtml}
        </div>
      </div>
    `;
    messagesBox.insertAdjacentHTML("beforeend", botHtml);
    messagesBox.scrollTop = messagesBox.scrollHeight;

    // Audio Speech Synthesis if active
    if (isDigitalMeAudioActive && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      // Clean markdown tags for spoken audio
      const cleanSpeech = responseText
        .replace(/[*#>`_-]/g, "")
        .replace(/https?:\/\/\S+/g, "")
        .slice(0, 240); // First couple sentences

      const utterance = new SpeechSynthesisUtterance(cleanSpeech);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }

  } catch (err) {
    console.error("Digital Me API error:", err);
    const typingEl = document.getElementById(typingId);
    if (typingEl) typingEl.remove();

    const errorHtml = `
      <div class="chat-bubble-row bot-row">
        <div class="chat-avatar bot-avatar">👨‍💻</div>
        <div class="chat-bubble bot-bubble" style="border-left: 4px solid #ef4444;">
          <div class="bubble-header">
            <strong>Pranith Kumar Dupuguntla (Digital Twin)</strong>
          </div>
          <div class="bubble-body" style="color:#b91c1c;">
            Sorry, I encountered an issue retrieving that information. Please try again or reach me directly at Praneeth.dupukuntla@gmail.com!
          </div>
        </div>
      </div>
    `;
    messagesBox.insertAdjacentHTML("beforeend", errorHtml);
  } finally {
    if (sendBtn) sendBtn.disabled = false;
    input.focus();
  }
}
