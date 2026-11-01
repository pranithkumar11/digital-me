/**
 * app.js - Interactive Client Logic for Digital Me Dashboard v2.5
 * Features:
 * - 360-degree radial audio spectrum analyzer around avatar
 * - Dynamic SVG lip-sync mouth modulation & eye pupil tracking
 * - Avatar mode switcher (Cyber Twin, Quantum Core, Custom Photo)
 * - Ambient background cyber particle matrix canvas
 * - Web Audio API synthesized futuristic sound FX
 * - Streaming conversational typewriter dialogue
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const chatForm = document.getElementById("chat-form");
  const queryInput = document.getElementById("query-input");
  const clearInputBtn = document.getElementById("clear-input-btn");
  const sendBtn = document.getElementById("send-btn");
  const chatStream = document.getElementById("chat-stream");
  const typingIndicator = document.getElementById("typing-indicator");
  const chipsContainer = document.getElementById("chips-container");
  const resetChatBtn = document.getElementById("reset-chat-btn");

  // Avatar & Audio Elements
  const avatarContainer = document.getElementById("avatar-container");
  const avatarBadge = document.getElementById("avatar-state-badge");
  const stateText = document.getElementById("state-text");
  const toggleAudio = document.getElementById("toggle-audio");
  const voiceSelect = document.getElementById("voice-select");
  const globalAudio = document.getElementById("global-audio-stream");
  const playerPlayBtn = document.getElementById("player-play-btn");
  const playerIcon = document.getElementById("player-icon");
  const playerProgress = document.getElementById("player-progress");
  const playerTime = document.getElementById("player-time");
  const playerTimeline = document.getElementById("player-timeline");

  // Face Elements for Dynamic Animation
  const avatarMouth = document.getElementById("avatar-mouth");
  const avatarMouthGlow = document.getElementById("avatar-mouth-glow");
  const pupilLeft = document.querySelector(".pupil-left");
  const pupilRight = document.querySelector(".pupil-right");
  const cheekBars = document.querySelectorAll(".cheek-bar");

  // Avatar Mode Tabs & Views
  const avatarTabBtns = document.querySelectorAll(".avatar-tab-btn");
  const avatarViews = document.querySelectorAll(".avatar-view");
  const photoDropzone = document.getElementById("photo-dropzone");
  const photoUploadInput = document.getElementById("photo-upload-input");
  const customAvatarImg = document.getElementById("custom-avatar-img");
  const photoPlaceholder = document.getElementById("photo-placeholder");

  // Status & SFX Elements
  const pillRag = document.getElementById("pill-rag");
  const dotLlm = document.getElementById("dot-llm");
  const valLlm = document.getElementById("val-llm");
  const dotTts = document.getElementById("dot-tts");
  const sfxToggleBtn = document.getElementById("sfx-toggle");

  // Canvas Visualizers
  const radialCanvas = document.getElementById("avatar-radial-canvas");
  const radialCtx = radialCanvas ? radialCanvas.getContext("2d") : null;
  const ambientCanvas = document.getElementById("ambient-canvas");
  const ambientCtx = ambientCanvas ? ambientCanvas.getContext("2d") : null;

  // State
  let isTransmitting = false;
  let sfxEnabled = true;
  let audioCtx = null;
  let analyser = null;
  let audioSource = null;
  let dataArray = null;
  let isAudioPlaying = false;
  let animationFrameId = null;

  // ==========================================
  // Web Audio Synthesized SFX (Zero File Assets)
  // ==========================================

  function getAudioContext() {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) {
        audioCtx = new AudioContextClass();
      }
    }
    if (audioCtx && audioCtx.state === "suspended") {
      audioCtx.resume();
    }
    return audioCtx;
  }

  function playCyberSfx(type) {
    if (!sfxEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);

      const now = ctx.currentTime;

      if (type === "transmit") {
        // High-tech laser chirping blip
        osc.type = "sine";
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(1760, now + 0.12);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.linearRampToValueAtTime(0, now + 0.12);
        osc.start(now);
        osc.stop(now + 0.12);
      } else if (type === "speech_start") {
        // Welcoming neural boot chime
        osc.type = "triangle";
        osc.frequency.setValueAtTime(523.25, now); // C5
        osc.frequency.exponentialRampToValueAtTime(659.25, now + 0.08); // E5
        osc.frequency.exponentialRampToValueAtTime(783.99, now + 0.18); // G5
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.linearRampToValueAtTime(0, now + 0.22);
        osc.start(now);
        osc.stop(now + 0.22);
      } else if (type === "click") {
        // Subtle micro UI tick
        osc.type = "sine";
        osc.frequency.setValueAtTime(1200, now);
        gain.gain.setValueAtTime(0.04, now);
        gain.gain.linearRampToValueAtTime(0, now + 0.04);
        osc.start(now);
        osc.stop(now + 0.04);
      }
    } catch (e) {
      // AudioContext unavailable
    }
  }

  sfxToggleBtn.addEventListener("click", () => {
    sfxEnabled = !sfxEnabled;
    sfxToggleBtn.classList.toggle("muted", !sfxEnabled);
    sfxToggleBtn.innerHTML = sfxEnabled
      ? `<span id="sfx-icon">&#128266;</span> SFX: ON`
      : `<span id="sfx-icon">&#128263;</span> SFX: OFF`;
    playCyberSfx("click");
  });

  // ==========================================
  // Web Audio API Live Spectrum Setup
  // ==========================================

  function setupAudioAnalyser() {
    if (analyser || !globalAudio) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;

      analyser = ctx.createAnalyser();
      analyser.fftSize = 128;
      analyser.smoothingTimeConstant = 0.8;

      audioSource = ctx.createMediaElementSource(globalAudio);
      audioSource.connect(analyser);
      analyser.connect(ctx.destination);

      dataArray = new Uint8Array(analyser.frequencyBinCount);
    } catch (e) {
      console.log("[*] Audio analyser setup notice (using procedural fallback):", e);
    }
  }

  // ==========================================
  // 360-Degree Radial Audio Spectrum Canvas
  // ==========================================

  let angleOffset = 0;

  function renderRadialSpectrum() {
    if (!radialCanvas || !radialCtx) return;

    const width = radialCanvas.width;
    const height = radialCanvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const baseRadius = 78;
    const barCount = 42;

    radialCtx.clearRect(0, 0, width, height);

    // Get live frequency data or simulate rhythm
    let averageFrequency = 0;
    if (isAudioPlaying && analyser && dataArray) {
      analyser.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      averageFrequency = sum / dataArray.length / 255;
    } else if (isAudioPlaying) {
      averageFrequency = 0.4 + Math.sin(Date.now() / 150) * 0.3;
    }

    angleOffset += 0.008;

    // Draw radial frequency spokes
    for (let i = 0; i < barCount; i++) {
      const angle = (i / barCount) * Math.PI * 2 + angleOffset;
      let barLength = 4;

      if (isAudioPlaying) {
        if (dataArray && dataArray.length > i) {
          const val = dataArray[i % dataArray.length] / 255;
          barLength = 5 + val * 38;
        } else {
          barLength = 6 + Math.abs(Math.sin((i * 0.4) + (Date.now() / 200))) * 28;
        }
      } else {
        // Idle gentle breathing ripple
        barLength = 3 + Math.sin((i * 0.3) + (Date.now() / 1000)) * 3;
      }

      const xStart = centerX + Math.cos(angle) * baseRadius;
      const yStart = centerY + Math.sin(angle) * baseRadius;
      const xEnd = centerX + Math.cos(angle) * (baseRadius + barLength);
      const yEnd = centerY + Math.sin(angle) * (baseRadius + barLength);

      const spokeGrad = radialCtx.createLinearGradient(xStart, yStart, xEnd, yEnd);
      if (isAudioPlaying) {
        spokeGrad.addColorStop(0, "rgba(0, 240, 255, 0.9)");
        spokeGrad.addColorStop(0.5, "rgba(0, 112, 243, 0.7)");
        spokeGrad.addColorStop(1, "rgba(121, 40, 202, 0.9)");
      } else {
        spokeGrad.addColorStop(0, "rgba(0, 240, 255, 0.25)");
        spokeGrad.addColorStop(1, "rgba(0, 112, 243, 0.05)");
      }

      radialCtx.beginPath();
      radialCtx.moveTo(xStart, yStart);
      radialCtx.lineTo(xEnd, yEnd);
      radialCtx.strokeStyle = spokeGrad;
      radialCtx.lineWidth = isAudioPlaying ? 2.5 : 1.2;
      radialCtx.lineCap = "round";
      radialCtx.stroke();
    }

    // Dynamic Facial & Mouth Lip-Sync Modulation
    if (avatarMouth) {
      if (isAudioPlaying) {
        const mouthOpen = Math.min(22, Math.max(3, averageFrequency * 26 + (Math.sin(Date.now() / 90) * 4)));
        avatarMouth.setAttribute("d", `M 48 78 Q 60 ${78 + mouthOpen} 72 78`);
        avatarMouth.setAttribute("stroke", "#00f0ff");
        if (avatarMouthGlow) {
          avatarMouthGlow.setAttribute("rx", (mouthOpen * 0.6).toFixed(1));
          avatarMouthGlow.setAttribute("ry", (mouthOpen * 0.4).toFixed(1));
          avatarMouthGlow.style.opacity = (averageFrequency * 0.8).toFixed(2);
        }
        // Cheek frequency micro bars
        cheekBars.forEach((b, idx) => {
          const h = 4 + Math.sin(Date.now() / 120 + idx) * 6;
          b.setAttribute("height", Math.max(2, h));
        });
      } else {
        avatarMouth.setAttribute("d", "M 48 78 Q 60 78 72 78");
        if (avatarMouthGlow) {
          avatarMouthGlow.style.opacity = "0";
        }
      }
    }

    requestAnimationFrame(renderRadialSpectrum);
  }

  renderRadialSpectrum();

  // ==========================================
  // Ambient Starfield & Particle Grid Canvas
  // ==========================================

  function initAmbientCanvas() {
    if (!ambientCanvas || !ambientCtx) return;

    let width = (ambientCanvas.width = window.innerWidth);
    let height = (ambientCanvas.height = window.innerHeight);

    window.addEventListener("resize", () => {
      width = ambientCanvas.width = window.innerWidth;
      height = ambientCanvas.height = window.innerHeight;
    });

    const particles = [];
    const count = 45;

    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        radius: Math.random() * 1.6 + 0.5,
        alpha: Math.random() * 0.5 + 0.2
      });
    }

    function drawAmbient() {
      ambientCtx.clearRect(0, 0, width, height);

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ambientCtx.beginPath();
        ambientCtx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ambientCtx.fillStyle = `rgba(0, 240, 255, ${p.alpha})`;
        ambientCtx.shadowBlur = 6;
        ambientCtx.shadowColor = "#00f0ff";
        ambientCtx.fill();
        ambientCtx.shadowBlur = 0;
      });

      requestAnimationFrame(drawAmbient);
    }

    drawAmbient();
  }

  initAmbientCanvas();

  // ==========================================
  // Eye Pupil Tracking (Mouse Parallax)
  // ==========================================

  document.addEventListener("mousemove", (e) => {
    if (!pupilLeft || !pupilRight) return;
    const rect = avatarContainer.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const deltaX = (e.clientX - centerX) / window.innerWidth;
    const deltaY = (e.clientY - centerY) / window.innerHeight;

    const moveX = Math.max(-2.5, Math.min(2.5, deltaX * 10));
    const moveY = Math.max(-2, Math.min(2, deltaY * 8));

    pupilLeft.style.transform = `translate(${moveX}px, ${moveY}px)`;
    pupilRight.style.transform = `translate(${moveX}px, ${moveY}px)`;
  });

  // ==========================================
  // Avatar Mode Switcher (Cyber / Core / Photo)
  // ==========================================

  avatarTabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      avatarTabBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      playCyberSfx("click");

      const mode = btn.getAttribute("data-mode");
      avatarViews.forEach((v) => v.classList.remove("active"));

      if (mode === "cyber-twin") {
        document.getElementById("view-cyber-twin").classList.add("active");
      } else if (mode === "quantum-core") {
        document.getElementById("view-quantum-core").classList.add("active");
      } else if (mode === "holo-portrait") {
        document.getElementById("view-holo-portrait").classList.add("active");
      }
    });
  });

  // Photo Upload Handler
  if (photoDropzone && photoUploadInput) {
    photoDropzone.addEventListener("click", () => {
      photoUploadInput.click();
    });

    photoUploadInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file && file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (event) => {
          customAvatarImg.src = event.target.result;
          customAvatarImg.style.display = "block";
          photoPlaceholder.style.display = "none";
          playCyberSfx("speech_start");
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // ==========================================
  // Audio Synchronization & Avatar Pulse
  // ==========================================

  function setAvatarState(state, message) {
    avatarBadge.classList.remove("speaking", "thinking");
    avatarContainer.classList.remove("is-speaking", "is-thinking");

    if (state === "speaking") {
      avatarBadge.classList.add("speaking");
      avatarContainer.classList.add("is-speaking");
      stateText.textContent = message || "NEURAL VOICE TRANSMITTING";
      isAudioPlaying = true;
    } else if (state === "thinking") {
      avatarBadge.classList.add("thinking");
      avatarContainer.classList.add("is-thinking");
      stateText.textContent = message || "NEURAL RETRIEVAL & SYNTHESIS...";
      isAudioPlaying = false;
    } else {
      stateText.textContent = message || "SYSTEM IDLE";
      isAudioPlaying = false;
    }
  }

  // Audio Player Listeners
  globalAudio.addEventListener("play", () => {
    setupAudioAnalyser();
    setAvatarState("speaking");
    playerPlayBtn.disabled = false;
    playerIcon.innerHTML = "&#10074;&#10074;"; // Pause
    playCyberSfx("speech_start");
  });

  globalAudio.addEventListener("pause", () => {
    if (!globalAudio.ended) {
      setAvatarState("idle", "AUDIO PAUSED");
      playerIcon.innerHTML = "&#9658;"; // Play
    }
  });

  globalAudio.addEventListener("ended", () => {
    setAvatarState("idle", "SYSTEM IDLE");
    playerIcon.innerHTML = "&#9658;";
    playerProgress.style.width = "0%";
    playerTime.textContent = "0:00";
  });

  globalAudio.addEventListener("timeupdate", () => {
    if (globalAudio.duration) {
      const pct = (globalAudio.currentTime / globalAudio.duration) * 100;
      playerProgress.style.width = `${pct}%`;
      const curM = Math.floor(globalAudio.currentTime / 60);
      const curS = Math.floor(globalAudio.currentTime % 60).toString().padStart(2, "0");
      playerTime.textContent = `${curM}:${curS}`;
    }
  });

  globalAudio.addEventListener("error", (e) => {
    console.warn("[!] Audio streaming fallback notice:", e);
    setAvatarState("idle", "SYSTEM IDLE");
    playerPlayBtn.disabled = true;
    playerIcon.innerHTML = "&#9658;";
  });

  playerPlayBtn.addEventListener("click", () => {
    playCyberSfx("click");
    if (globalAudio.src) {
      if (globalAudio.paused) {
        globalAudio.play();
      } else {
        globalAudio.pause();
      }
    }
  });

  if (playerTimeline) {
    playerTimeline.addEventListener("click", (e) => {
      if (globalAudio.duration) {
        const rect = playerTimeline.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        globalAudio.currentTime = pos * globalAudio.duration;
      }
    });
  }

  function playAudioUrl(url) {
    if (!url) return;
    try {
      globalAudio.src = url;
      globalAudio.play().catch((err) => {
        console.log("[*] Browser autoplay policy restricted audio. Press Play to listen:", err);
        setAvatarState("idle", "CLICK PLAY TO LISTEN");
        playerPlayBtn.disabled = false;
      });
    } catch (e) {
      console.error("[!] Audio playback error:", e);
    }
  }

  // Web Speech Fallback for Offline Environments
  function speakWithWebSpeechFallback(text) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      setAvatarState("speaking", "LOCAL SPEECH SYNTHESIS");
    };
    utterance.onend = () => {
      setAvatarState("idle", "SYSTEM IDLE");
    };
    utterance.onerror = () => {
      setAvatarState("idle", "SYSTEM IDLE");
    };

    window.speechSynthesis.speak(utterance);
  }

  // ==========================================
  // Markdown & Text Rendering Helpers
  // ==========================================

  function parseMarkdown(text) {
    if (!text) return "";
    let html = text;

    html = html.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
    html = html.replace(/^## (.*$)/gim, "<h3>$1</h3>");
    html = html.replace(/^# (.*$)/gim, "<h3>$1</h3>");
    html = html.replace(/^\> (.*$)/gim, "<blockquote>$1</blockquote>");
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    html = html.replace(/_([^_]+)_/g, "<em>$1</em>");
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
    html = html.replace(/^\s*[-*]\s+(.*$)/gim, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>)/gms, "<ul>$1</ul>");

    const paragraphs = html.split(/\n{2,}/);
    html = paragraphs
      .map((p) => {
        p = p.trim();
        if (!p) return "";
        if (p.startsWith("<h3>") || p.startsWith("<ul>") || p.startsWith("<blockquote>")) {
          return p;
        }
        return `<p>${p.replace(/\n/g, "<br>")}</p>`;
      })
      .join("");

    return html;
  }

  function getTimeString() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function scrollToBottom() {
    setTimeout(() => {
      chatStream.scrollTop = chatStream.scrollHeight;
    }, 50);
  }

  // ==========================================
  // Chat Stream Message Appenders
  // ==========================================

  function appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "message-row message-user";
    row.innerHTML = `
      <div class="msg-avatar-badge">YOU</div>
      <div class="msg-bubble-wrap">
        <div class="msg-header">
          <span class="sender-name">GUEST OPERATOR</span>
          <span class="msg-timestamp">${getTimeString()}</span>
        </div>
        <div class="msg-content">
          <p>${text.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</p>
        </div>
      </div>
    `;
    chatStream.appendChild(row);
    scrollToBottom();
  }

  function appendTwinMessage(data) {
    const row = document.createElement("div");
    row.className = "message-row message-twin";

    const responseHtml = parseMarkdown(data.response);
    const audioUrl = data.audio_url || (data.audio && data.audio.audio_url);
    const sources = data.sources || [];

    let sourcesHtml = "";
    if (sources.length > 0) {
      const sourceItems = sources
        .map(
          (s) => `
        <div class="source-item">
          <div class="source-title">&#128196; ${s.title || s.source}</div>
          <div class="source-snippet">${s.snippet || ""}</div>
        </div>
      `
        )
        .join("");

      sourcesHtml = `
        <button class="sources-toggle-btn" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
          &#128065; Grounded Sources (${sources.length})
        </button>
        <div class="sources-dropdown" style="display: none;">
          ${sourceItems}
        </div>
      `;
    }

    let audioButtonHtml = "";
    if (audioUrl) {
      audioButtonHtml = `
        <button class="msg-action-btn speak-again-btn" data-audiourl="${audioUrl}">
          &#9658; Play Voice
        </button>
      `;
    } else {
      audioButtonHtml = `
        <button class="msg-action-btn speak-again-btn" data-rawtext="${data.response.replace(/"/g, "&quot;")}">
          &#128266; Read Aloud
        </button>
      `;
    }

    row.innerHTML = `
      <div class="msg-avatar-badge">PK</div>
      <div class="msg-bubble-wrap">
        <div class="msg-header">
          <span class="sender-name">PRANITH KUMAR DUPUGUNTLA</span>
          <span class="msg-timestamp">${getTimeString()} &bull; ${data.model || "Llama 3"}</span>
        </div>
        <div class="msg-content">
          ${responseHtml}
        </div>
        <div class="msg-footer">
          ${audioButtonHtml}
          ${sourcesHtml}
        </div>
      </div>
    `;

    chatStream.appendChild(row);
    scrollToBottom();

    // Attach speak button listener
    const playBtn = row.querySelector(".speak-again-btn");
    if (playBtn) {
      playBtn.addEventListener("click", () => {
        playCyberSfx("click");
        const url = playBtn.getAttribute("data-audiourl");
        if (url) {
          playAudioUrl(url);
        } else {
          const raw = playBtn.getAttribute("data-rawtext");
          if (raw) speakWithWebSpeechFallback(raw);
        }
      });
    }

    // Auto-play audio if toggle is on
    if (toggleAudio.checked) {
      if (audioUrl) {
        playAudioUrl(audioUrl);
      } else {
        speakWithWebSpeechFallback(data.response);
      }
    }

    // Update suggestions chips
    if (data.suggested_questions && data.suggested_questions.length > 0) {
      updateSuggestionChips(data.suggested_questions);
    }
  }

  function updateSuggestionChips(questions) {
    chipsContainer.innerHTML = "";
    questions.forEach((q) => {
      const chip = document.createElement("button");
      chip.className = "query-chip";
      chip.textContent = q;
      chip.setAttribute("data-query", q);
      chip.addEventListener("click", () => {
        playCyberSfx("click");
        submitQuery(q);
      });
      chipsContainer.appendChild(chip);
    });
  }

  // ==========================================
  // Form Submission & Query Pipeline
  // ==========================================

  async function submitQuery(queryText) {
    const text = (queryText || queryInput.value || "").trim();
    if (!text || isTransmitting) return;

    isTransmitting = true;
    sendBtn.disabled = true;
    queryInput.value = "";
    clearInputBtn.style.display = "none";

    appendUserMessage(text);
    playCyberSfx("transmit");

    // Set avatar state to thinking with laser scan
    setAvatarState("thinking");
    typingIndicator.style.display = "block";
    scrollToBottom();

    const payload = {
      query: text,
      synthesize_audio: toggleAudio.checked,
      voice: voiceSelect.value,
      top_k: 4
    };

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`API error ${res.status}`);
      }

      const data = await res.json();
      typingIndicator.style.display = "none";
      appendTwinMessage(data);

    } catch (err) {
      console.error("[!] Transmission error:", err);
      typingIndicator.style.display = "none";
      appendTwinMessage({
        response: "I encountered a brief connection anomaly while querying my neural network. Please verify that the local server is running.",
        model: "offline_failsafe",
        sources: []
      });
      setAvatarState("idle", "CONNECTION RETRY READY");
    } finally {
      isTransmitting = false;
      sendBtn.disabled = false;
      queryInput.focus();
    }
  }

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    submitQuery();
  });

  queryInput.addEventListener("input", () => {
    clearInputBtn.style.display = queryInput.value.length > 0 ? "block" : "none";
  });

  clearInputBtn.addEventListener("click", () => {
    queryInput.value = "";
    clearInputBtn.style.display = "none";
    queryInput.focus();
    playCyberSfx("click");
  });

  chipsContainer.addEventListener("click", (e) => {
    const chip = e.target.closest(".query-chip");
    if (chip) {
      const query = chip.getAttribute("data-query");
      if (query) submitQuery(query);
    }
  });

  // Re-index button (Dev Tool)
  const reindexBtn = document.getElementById("reindex-btn");
  if (reindexBtn) {
    reindexBtn.addEventListener("click", async () => {
      playCyberSfx("click");
      reindexBtn.disabled = true;
      reindexBtn.textContent = "⏳ Re-indexing...";
      try {
        const res = await fetch("/api/reindex", { method: "POST" });
        const data = await res.json();
        if (data.success) {
          reindexBtn.textContent = "✅ Indexed!";
          playCyberSfx("speech_start");
          checkSystemHealth();
          setTimeout(() => {
            reindexBtn.textContent = "🔄 Re-Index KB";
            reindexBtn.disabled = false;
          }, 3000);
        } else {
          alert(`Re-index error: ${data.error}`);
          reindexBtn.textContent = "🔄 Re-Index KB";
          reindexBtn.disabled = false;
        }
      } catch (err) {
        alert("Failed to connect to /api/reindex endpoint.");
        reindexBtn.textContent = "🔄 Re-Index KB";
        reindexBtn.disabled = false;
      }
    });
  }

  resetChatBtn.addEventListener("click", () => {
    playCyberSfx("click");
    if (confirm("Reset conversation history?")) {
      chatStream.innerHTML = "";
      window.location.reload();
    }
  });

  // ==========================================
  // System Diagnostics Check on Boot
  // ==========================================

  async function checkSystemHealth() {
    try {
      const res = await fetch("/health");
      if (res.ok) {
        const data = await res.json();
        const ollama = data.diagnostics?.ollama;
        const kb = data.diagnostics?.knowledge_base;

        if (ollama && ollama.online) {
          dotLlm.className = "status-indicator-dot dot-active";
          valLlm.textContent = `${ollama.target_model.toUpperCase()} (LIVE)`;
        } else {
          dotLlm.className = "status-indicator-dot dot-warning";
          valLlm.textContent = "PERSONA RAG";
          valLlm.title = "Ollama offline. Running ultra-fast First-Person Persona RAG engine.";
        }

        if (kb && kb.total_indexed_chunks > 0) {
          pillRag.querySelector(".pill-val").textContent = `CHROMADB (${kb.total_indexed_chunks})`;
        }
      }
    } catch (e) {
      console.log("[*] Health check notice:", e);
    }
  }

  async function loadVoices() {
    try {
      const res = await fetch("/api/voices");
      if (res.ok) {
        const data = await res.json();
        if (data.voices) {
          voiceSelect.innerHTML = "";
          for (const [key, label] of Object.entries(data.voices)) {
            const opt = document.createElement("option");
            opt.value = key;
            opt.textContent = label;
            if (key === data.default) opt.selected = true;
            voiceSelect.appendChild(opt);
          }
        }
      }
    } catch (e) {
      // Offline fallback
    }
  }

  // Initial Boot
  checkSystemHealth();
  loadVoices();
  queryInput.focus();
});
