/**
 * Global Voice & Text Linux Advisor Assistant
 * Works across all pages in Firefox, Chrome, and Edge using MediaRecorder & SpeechSynthesis.
 * Speech-to-text powered by Gemini API with 30s limit, in-memory processing, and multi-language support.
 */

document.addEventListener("DOMContentLoaded", () => {
  const launcherBtn = document.getElementById("chatLauncherBtn");
  const windowPanel = document.getElementById("chatWindowPanel");
  const closeBtn = document.getElementById("chatCloseBtn");
  const textInput = document.getElementById("chatTextInput");
  const sendBtn = document.getElementById("chatSendInputBtn");
  const micBtn = document.getElementById("chatMicInputBtn");
  const messagesContainer = document.getElementById("chatMessagesContainer");
  const typingIndicator = document.getElementById("chatTypingIndicator");
  const recordingBanner = document.getElementById("chatRecordingBanner");
  const stopRecBtn = document.getElementById("chatStopRecordingBtn");
  const micFallback = document.getElementById("chatMicFallback");
  const voiceModeBtn = document.getElementById("chatVoiceModeBtn");
  const notificationBadge = document.getElementById("chatNotificationBadge");
  const languageSelect = document.getElementById("chatLanguageSelect");
  const recordingTimerEl = document.getElementById("chatRecordingTimer");
  const voicePreviewBar = document.getElementById("chatVoicePreviewBar");
  const autoSendCountdownEl = document.getElementById("chatAutoSendCountdown");
  const cancelAutoSendBtn = document.getElementById("chatCancelAutoSendBtn");

  if (!launcherBtn || !windowPanel) return;

  // State
  let isOpen = false;
  let chatContext = {};
  let chatHistory = [];
  let isVoiceMode = localStorage.getItem("distro_chat_voice_mode") === "true";
  let mediaRecorder = null;
  let audioStream = null;
  let audioChunks = [];
  let autoStopTimer = null;
  let recTimerInterval = null;
  let recordingSeconds = 0;
  let isRecording = false;
  let autoSendInterval = null;
  let autoSendSecondsLeft = 0;
  let pendingVoiceMessage = false;

  // Sync language selection
  if (languageSelect) {
    const savedLang = localStorage.getItem("distro_advisor_lang") || "auto";
    languageSelect.value = savedLang;
    languageSelect.addEventListener("change", () => {
      localStorage.setItem("distro_advisor_lang", languageSelect.value);
      const quizLang = document.getElementById("quizLanguageSelect");
      if (quizLang) quizLang.value = languageSelect.value;
    });
  }

  // Initialize Voice Mode UI
  updateVoiceModeUI();

  if (voiceModeBtn) {
    voiceModeBtn.addEventListener("click", () => {
      isVoiceMode = !isVoiceMode;
      localStorage.setItem("distro_chat_voice_mode", isVoiceMode);
      updateVoiceModeUI();
      if (!isVoiceMode) {
        stopSpeech();
      }
    });
  }

  function updateVoiceModeUI() {
    if (!voiceModeBtn) return;
    if (isVoiceMode) {
      voiceModeBtn.classList.add("active");
      voiceModeBtn.innerHTML = `<span class="vm-icon">🔊</span><span class="vm-text">Voice Mode: ON</span>`;
    } else {
      voiceModeBtn.classList.remove("active");
      voiceModeBtn.innerHTML = `<span class="vm-icon">🔇</span><span class="vm-text">Voice Mode: OFF</span>`;
    }
  }

  // Toggle Chat Panel
  launcherBtn.addEventListener("click", () => {
    isOpen = !isOpen;
    if (isOpen) {
      windowPanel.style.display = "flex";
      launcherBtn.classList.add("open");
      if (notificationBadge) notificationBadge.style.display = "none";
      if (textInput) textInput.focus();
      scrollToBottom();
    } else {
      windowPanel.style.display = "none";
      launcherBtn.classList.remove("open");
      stopSpeech();
      stopRecording();
      cancelAutoSend();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      isOpen = false;
      windowPanel.style.display = "none";
      launcherBtn.classList.remove("open");
      stopSpeech();
      stopRecording();
      cancelAutoSend();
    });
  }

  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  // Send message when button clicked or Enter pressed
  if (sendBtn) {
    sendBtn.addEventListener("click", () => {
      const fromVoice = pendingVoiceMessage;
      cancelAutoSend();
      handleSendMessage(null, fromVoice);
    });
  }

  if (textInput) {
    textInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const fromVoice = pendingVoiceMessage;
        cancelAutoSend();
        handleSendMessage(null, fromVoice);
      }
    });

    // If user types/modifies the recognized text, cancel auto-send so they can fix it freely
    textInput.addEventListener("input", () => {
      if (autoSendInterval) {
        cancelAutoSend();
      }
    });
  }

  // Cancel auto-send button
  if (cancelAutoSendBtn) {
    cancelAutoSendBtn.addEventListener("click", () => {
      cancelAutoSend();
      if (textInput) textInput.focus();
    });
  }

  function cancelAutoSend() {
    if (autoSendInterval) {
      clearInterval(autoSendInterval);
      autoSendInterval = null;
    }
    if (voicePreviewBar) {
      voicePreviewBar.style.display = "none";
    }
    pendingVoiceMessage = false;
  }

  // Handle Quick Chips
  document.addEventListener("click", (e) => {
    const chip = e.target.closest(".quick-chip");
    if (chip) {
      cancelAutoSend();
      const query = chip.dataset.query;
      if (textInput) textInput.value = query;
      handleSendMessage(null, false);
    }
  });

  async function handleSendMessage(customMessage = null, fromVoice = false) {
    if (!textInput && customMessage === null) return;
    const message = (customMessage !== null ? customMessage : (textInput ? textInput.value : "")).trim();
    if (!message) return;

    // Clear input
    if (textInput) textInput.value = "";
    stopSpeech();

    // Append user message
    appendMessage("user", message);
    chatHistory.push({ role: "user", text: message });
    scrollToBottom();

    // Show typing indicator
    if (typingIndicator) typingIndicator.style.display = "flex";
    scrollToBottom();

    let quizResult = null;
    try {
      const saved = localStorage.getItem("distro_advisor_last_result");
      if (saved) {
        quizResult = JSON.parse(saved);
      }
    } catch (e) {
      console.warn("Could not read local quiz result:", e);
    }

    try {
      const response = await fetch("/api/chat_advisor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message,
          context: chatContext,
          history: chatHistory,
          quiz_result: quizResult
        })
      });

      const resData = await response.json();
      if (typingIndicator) typingIndicator.style.display = "none";

      if (resData.success && resData.data) {
        const data = resData.data;
        if (data.context) {
          chatContext = data.context;
        }

        // Add assistant response to history
        chatHistory.push({ role: "assistant", text: data.reply });
        if (chatHistory.length > 25) {
          chatHistory = chatHistory.slice(-25);
        }

        // Append assistant message
        appendMessage("assistant", data.reply, data.recommendation, data.suggestions);
        scrollToBottom();

        // Speak aloud if voice mode is on or user initiated message via voice
        if (fromVoice || isVoiceMode) {
          const speechText = data.tts_text || data.reply.replace(/[*•#]/g, "");
          speakAssistantReply(speechText);
        }
      } else {
        appendMessage("assistant", "⚠️ I encountered a temporary problem contacting the advisor service. Please try asking again.");
        scrollToBottom();
      }
    } catch (err) {
      console.error("Chat network error:", err);
      if (typingIndicator) typingIndicator.style.display = "none";
      appendMessage("assistant", "⚠️ Network connection error. Please check your internet connection.");
      scrollToBottom();
    }
  }

  function appendMessage(sender, text, recommendation = null, suggestions = []) {
    if (!messagesContainer) return;

    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-msg ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";

    let formattedText = escapeHtml(text)
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/^• (.*?)$/gm, "<li>$1</li>")
      .replace(/\n\n/g, "</p><p>")
      .replace(/\n/g, "<br>");

    if (formattedText.includes("<li>")) {
      formattedText = formattedText.replace(/(<li>.*?<\/li>)/gs, "<ul class='chat-reasons-list'>$1</ul>");
    }

    bubble.innerHTML = `<p>${formattedText}</p>`;

    // If a distro recommendation card is provided
    if (recommendation) {
      const recCard = document.createElement("div");
      recCard.className = "chat-rec-card";
      recCard.innerHTML = `
        <div class="chat-rec-top">
          <img src="/static/images/distros/${recommendation.id}.svg" alt="${recommendation.name}" class="chat-rec-logo">
          <div class="chat-rec-meta">
            <strong>${recommendation.name}</strong>
            <span class="chat-rec-tagline">${recommendation.tagline}</span>
          </div>
          <span class="chat-match-badge">${recommendation.match_percentage}%</span>
        </div>
        <div class="chat-rec-chips">
          <span>🖥️ ${recommendation.desktop_environment}</span>
          <span>📦 ${recommendation.package_manager}</span>
        </div>
        <div class="chat-rec-links">
          <a href="/distro/${recommendation.id}" class="chat-card-btn primary">View Specs</a>
          <a href="/compare?d1=${recommendation.id}" class="chat-card-btn secondary">Compare</a>
        </div>
      `;
      bubble.appendChild(recCard);
    }

    // If suggestions are provided
    if (suggestions && suggestions.length > 0) {
      const chipsWrap = document.createElement("div");
      chipsWrap.className = "chat-quick-chips";
      suggestions.forEach(s => {
        const chipBtn = document.createElement("button");
        chipBtn.type = "button";
        chipBtn.className = "quick-chip";
        chipBtn.dataset.query = s;
        chipBtn.textContent = s;
        chipsWrap.appendChild(chipBtn);
      });
      bubble.appendChild(chipsWrap);
    }

    // Audio replay button for assistant messages
    if (sender === "assistant") {
      const replayBtn = document.createElement("button");
      replayBtn.type = "button";
      replayBtn.className = "msg-speak-btn";
      replayBtn.title = "Listen to this reply aloud";
      replayBtn.innerHTML = `🔊`;
      replayBtn.addEventListener("click", () => {
        const clean = text.replace(/[*•#]/g, "");
        speakAssistantReply(clean);
      });
      bubble.appendChild(replayBtn);
    }

    msgDiv.appendChild(bubble);

    const timeSpan = document.createElement("span");
    timeSpan.className = "msg-time";
    const now = new Date();
    timeSpan.textContent = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    msgDiv.appendChild(timeSpan);

    messagesContainer.appendChild(msgDiv);
  }

  function escapeHtml(str) {
    return (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  // =========================================================================
  // Voice Synthesis (SpeechSynthesis with multilingual voice detection)
  // =========================================================================
  function detectScriptLanguage(text) {
    if (!text) return "en";
    if (/[\u0B80-\u0BFF]/.test(text)) return "ta"; // Tamil
    if (/[\u0900-\u097F]/.test(text)) return "hi"; // Hindi / Devanagari
    if (/[\u0D00-\u0D7F]/.test(text)) return "ml"; // Malayalam
    if (/[\u0C00-\u0C7F]/.test(text)) return "te"; // Telugu
    return "en";
  }

  function speakAssistantReply(text) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    const detectedLang = detectScriptLanguage(text);
    const langCodeMap = {
      "ta": "ta-IN",
      "hi": "hi-IN",
      "ml": "ml-IN",
      "te": "te-IN",
      "en": "en-US"
    };

    const targetLang = langCodeMap[detectedLang] || "en-US";
    utterance.lang = targetLang;

    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length > 0) {
      // Find voice matching target language prefix
      const targetPrefix = detectedLang.toLowerCase();
      const matchingVoice = voices.find(v => {
        const vLang = (v.lang || "").toLowerCase().replace("_", "-");
        return vLang.startsWith(targetPrefix);
      });
      if (matchingVoice) {
        utterance.voice = matchingVoice;
      } else if (detectedLang === "en") {
        const preferredEn = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("Zira")));
        if (preferredEn) utterance.voice = preferredEn;
      }
    }

    window.speechSynthesis.speak(utterance);
  }

  function stopSpeech() {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  }

  // Ensure speech synthesis voices are loaded
  if ("speechSynthesis" in window) {
    window.speechSynthesis.onvoiceschanged = () => {
      // Warm up voices list
      window.speechSynthesis.getVoices();
    };
  }

  // =========================================================================
  // Voice Input (MediaRecorder -> /transcribe with 30s limit and Gemini)
  // Cross-browser in Firefox, Chrome, Edge
  // =========================================================================
  const hasMediaSupport = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder);

  if (!hasMediaSupport) {
    if (micBtn) micBtn.style.display = "none";
    if (micFallback) {
      micFallback.style.display = "block";
      micFallback.textContent = "⚠️ Microphone recording is not supported in this browser. You can type freely!";
    }
  }

  if (micBtn) {
    micBtn.addEventListener("click", () => {
      if (isRecording) {
        stopRecording();
      } else {
        startRecording();
      }
    });
  }

  if (stopRecBtn) {
    stopRecBtn.addEventListener("click", () => {
      stopRecording();
    });
  }

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60).toString().padStart(2, "0");
    const secs = (seconds % 60).toString().padStart(2, "0");
    return `${mins}:${secs}`;
  }

  async function startRecording() {
    stopSpeech();
    cancelAutoSend();

    try {
      audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      console.warn("Chat mic permission error:", err);
      if (micBtn) micBtn.classList.remove("recording");
      if (recordingBanner) recordingBanner.style.display = "none";
      if (micFallback) {
        micFallback.style.display = "block";
        micFallback.textContent = "⚠️ Microphone access was denied. Please allow microphone permissions in your browser address bar to use voice.";
      }
      showChatNotice("Microphone permission was denied. Please allow microphone access.");
      return;
    }

    let options = {};
    if (typeof MediaRecorder.isTypeSupported === "function") {
      if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
        options = { mimeType: "audio/webm;codecs=opus" };
      } else if (MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")) {
        options = { mimeType: "audio/ogg;codecs=opus" };
      } else if (MediaRecorder.isTypeSupported("audio/mp4")) {
        options = { mimeType: "audio/mp4" };
      } else if (MediaRecorder.isTypeSupported("audio/webm")) {
        options = { mimeType: "audio/webm" };
      }
    }

    try {
      mediaRecorder = new MediaRecorder(audioStream, options);
    } catch (e) {
      mediaRecorder = new MediaRecorder(audioStream);
    }

    audioChunks = [];
    isRecording = true;
    recordingSeconds = 0;

    if (micBtn) {
      micBtn.classList.add("recording");
      micBtn.innerHTML = "⏹️";
      micBtn.title = "Stop Recording";
    }

    if (recordingBanner) {
      recordingBanner.style.display = "block";
    }

    if (recordingTimerEl) {
      recordingTimerEl.textContent = `00:00 / 00:30`;
    }

    // Live timer tick every second up to 30s
    recTimerInterval = setInterval(() => {
      recordingSeconds++;
      if (recordingTimerEl) {
        recordingTimerEl.textContent = `${formatTime(recordingSeconds)} / 00:30`;
      }
      if (recordingSeconds >= 30) {
        stopRecording();
      }
    }, 1000);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) {
        audioChunks.push(e.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const mimeType = mediaRecorder.mimeType || "audio/webm";
      const audioBlob = new Blob(audioChunks, { type: mimeType });

      // Clean stream
      if (audioStream) {
        audioStream.getTracks().forEach(t => t.stop());
        audioStream = null;
      }

      await sendChatAudioForTranscription(audioBlob);
    };

    mediaRecorder.start(200);

    // Hard auto-stop after 30 seconds
    autoStopTimer = setTimeout(() => {
      stopRecording();
    }, 30000);
  }

  function stopRecording() {
    if (autoStopTimer) {
      clearTimeout(autoStopTimer);
      autoStopTimer = null;
    }
    if (recTimerInterval) {
      clearInterval(recTimerInterval);
      recTimerInterval = null;
    }
    if (recordingBanner) {
      recordingBanner.style.display = "none";
    }
    if (micBtn) {
      micBtn.classList.remove("recording");
      micBtn.innerHTML = "🎤";
      micBtn.title = "Speak your question aloud";
    }
    isRecording = false;

    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
  }

  function isMeaningfulSpeech(rawText) {
    if (!rawText) return false;
    const text = rawText.trim();
    if (!text) return false;

    // Filter out brackets like [blank_audio], [silence], etc.
    const cleaned = text.replace(/\[.*?\]|\(.*?\)/g, "").trim();
    if (!cleaned) return false;

    // Must have at least letters or numbers (supports Unicode Latin, Tamil, Devanagari, Telugu, Malayalam)
    const hasWordChars = /[\p{L}\p{N}]/u.test(cleaned);
    if (!hasWordChars) return false;

    // Filter out strings that are just noise symbols like "..." or "???" or "- - -"
    if (/^[.\-_~*?!,;:/\\]+$/.test(cleaned)) return false;

    return true;
  }

  function showChatNotice(messageText) {
    if (!messagesContainer) return;
    const noticeDiv = document.createElement("div");
    noticeDiv.className = "chat-voice-notice";
    noticeDiv.innerHTML = `<span class="notice-icon">🎙️</span><span>${escapeHtml(messageText)}</span>`;
    messagesContainer.appendChild(noticeDiv);
    scrollToBottom();
    setTimeout(() => {
      noticeDiv.style.opacity = "0";
      setTimeout(() => noticeDiv.remove(), 500);
    }, 4500);
  }

  async function sendChatAudioForTranscription(blob) {
    // Check 4 MB limit
    if (blob.size > 4 * 1024 * 1024) {
      showChatNotice("Audio recording exceeded 4 MB limit. Please speak for a shorter time.");
      return;
    }

    if (textInput) {
      textInput.placeholder = "Transcribing your voice with Gemini...";
    }

    const formData = new FormData();
    let ext = "chat_rec.webm";
    if (blob.type.includes("ogg")) ext = "chat_rec.ogg";
    else if (blob.type.includes("mp4")) ext = "chat_rec.mp4";

    formData.append("audio", blob, ext);
    formData.append("question", "chat");

    const selectedLang = languageSelect ? languageSelect.value : "auto";
    formData.append("language", selectedLang);

    try {
      const response = await fetch("/transcribe", {
        method: "POST",
        body: formData
      });

      if (!response.ok && response.status !== 200) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const res = await response.json();
      if (textInput) {
        textInput.placeholder = "Ask about RAM, gaming, coding, distros...";
      }

      // Check for structured errors from server
      if (res.success === false) {
        const errorType = res.error_type || "";
        if (errorType === "no_key") {
          showChatNotice("⚠️ Gemini API key is not configured. Please set GEMINI_API_KEY in environment variables.");
        } else if (errorType === "quota_finished") {
          showChatNotice("⚠️ Gemini API quota exceeded. Please try again in a few moments.");
        } else if (errorType === "network_error") {
          showChatNotice("⚠️ Network error contacting transcription service. Please check your connection.");
        } else {
          showChatNotice(`⚠️ Voice transcription error: ${res.error || "Please try again."}`);
        }
        return;
      }

      // Check if meaningful transcript received
      if (res.success && res.transcript && isMeaningfulSpeech(res.transcript)) {
        const spokenText = res.transcript.trim();

        // 1. Show recognized text in the input box so user can fix it
        if (textInput) {
          textInput.value = spokenText;
          textInput.focus();
        }

        // 2. Show review banner and begin 3-second countdown before sending
        pendingVoiceMessage = true;
        autoSendSecondsLeft = 3;

        if (voicePreviewBar) {
          voicePreviewBar.style.display = "flex";
        }
        if (autoSendCountdownEl) {
          autoSendCountdownEl.textContent = autoSendSecondsLeft;
        }

        autoSendInterval = setInterval(() => {
          autoSendSecondsLeft--;
          if (autoSendCountdownEl) {
            autoSendCountdownEl.textContent = autoSendSecondsLeft;
          }

          if (autoSendSecondsLeft <= 0) {
            cancelAutoSend();
            // Automatically send to chat
            handleSendMessage(null, true);
          }
        }, 1000);

      } else {
        // Voice text is empty or noise: show required friendly notice and do NOT send to AI
        const noticeText = "I could not hear you clearly, please try again";
        showChatNotice(noticeText);
        if (textInput) {
          textInput.placeholder = noticeText;
          setTimeout(() => {
            textInput.placeholder = "Ask about RAM, gaming, coding, distros...";
          }, 3500);
        }
        if (isVoiceMode) {
          speakAssistantReply(noticeText);
        }
      }
    } catch (err) {
      console.error("Transcription network error:", err);
      showChatNotice("⚠️ Network error while transcribing audio. Please check your internet connection.");
      if (textInput) {
        textInput.placeholder = "Ask about RAM, gaming, coding, distros...";
      }
    }
  }
});
