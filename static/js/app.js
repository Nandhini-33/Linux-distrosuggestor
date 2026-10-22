/**
 * Linux Distribution Advisor - Interactive Client Controller & Cross-Browser Voice Assistant
 * Supports Firefox, Chrome, Edge using SpeechSynthesis & MediaRecorder (No webkitSpeechRecognition)
 */

document.addEventListener("DOMContentLoaded", () => {
  // =========================================================================
  // 1. Theme Toggle Controller
  // =========================================================================
  const themeToggle = document.getElementById("themeToggle");
  const storedTheme = localStorage.getItem("distro_advisor_theme") || "dark";
  document.documentElement.setAttribute("data-theme", storedTheme);
  updateThemeIcon(storedTheme);

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const nextTheme = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", nextTheme);
      localStorage.setItem("distro_advisor_theme", nextTheme);
      updateThemeIcon(nextTheme);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    themeToggle.innerHTML = theme === "dark" 
      ? `<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>`
      : `<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>`;
  }

  // =========================================================================
  // 2. Voice Assistant Settings & SpeechSynthesis Controller
  // =========================================================================
  let isVoiceAssistantEnabled = localStorage.getItem("distro_advisor_voice") !== "false";
  const voiceToggle = document.getElementById("voiceAssistantToggle");
  const voiceBadge = document.querySelector(".voice-badge");
  const voiceStatusText = document.getElementById("voiceStatusText");
  const voiceToast = document.getElementById("voiceToast");

  if (voiceToggle) {
    voiceToggle.checked = isVoiceAssistantEnabled;
    updateVoiceUI();
    voiceToggle.addEventListener("change", () => {
      isVoiceAssistantEnabled = voiceToggle.checked;
      localStorage.setItem("distro_advisor_voice", isVoiceAssistantEnabled);
      updateVoiceUI();
      if (!isVoiceAssistantEnabled) {
        stopAllSpeech();
        stopActiveRecording();
      } else {
        showVoiceToast("Voice Assistant Enabled: Audio speech & mic active.", "success");
      }
    });
  }

  function updateVoiceUI() {
    if (!voiceBadge || !voiceStatusText) return;
    if (isVoiceAssistantEnabled) {
      voiceBadge.classList.remove("off");
      voiceStatusText.textContent = "Voice Assistant: Active";
    } else {
      voiceBadge.classList.add("off");
      voiceStatusText.textContent = "Voice Assistant: Off";
    }
  }

  // Scripted read texts for each of the 7 questions in quiz order
  const QUESTION_SCRIPTS = {
    ram: "Question 1: Available RAM Size. Your options are: Less than 2 gigabytes; 2 to 4 gigabytes; 4 to 8 gigabytes; 8 to 16 gigabytes; or 16 gigabytes or more.",
    experience: "Question 2: Computer Experience Level. Your options are: Beginner; Intermediate; or Advanced Power User.",
    purpose: "Question 3: Main Purpose. Your options are: Programming; Gaming; Office; Education; Security; or General Use.",
    cpu: "Question 4: Processor CPU Tier. Your options are: Older Budget Dual Core; Mid-range Quad Core; High-End Multi-Core; or ARM Single Board Computer.",
    storage: "Question 5: Available Storage Space. Your options are: Less than 20 gigabytes; 20 to 50 gigabytes; 50 to 100 gigabytes; or 100 gigabytes or more.",
    preference: "Question 6: Preference. Your options are: Easy to Use; Lightweight; or Customizable.",
    prev_experience: "Question 7: Previous Linux Experience. Your options are: None or First Timer; Tested in Virtual Machine or Live USB; Dual Boot or Casual User; or Daily Driver and Server Experience."
  };

  // Speaks text aloud using SpeechSynthesis
  function speakText(text, onStart, onEnd) {
    if (!("speechSynthesis" in window)) {
      console.warn("SpeechSynthesis not supported in this browser.");
      if (onEnd) onEnd();
      return;
    }

    window.speechSynthesis.cancel(); // Stop any pending utterances
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Slow, clear, friendly speaking speed as requested
    utterance.rate = 0.92;
    utterance.pitch = 1.0;
    utterance.lang = "en-US";

    // Attempt to pick a natural English voice
    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length > 0) {
      const preferred = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("Zira") || v.name.includes("Samantha")));
      if (preferred) utterance.voice = preferred;
    }

    utterance.onstart = () => { if (onStart) onStart(); };
    utterance.onend = () => { if (onEnd) onEnd(); };
    utterance.onerror = (e) => {
      console.warn("Speech synthesis error:", e);
      if (onEnd) onEnd();
    };

    window.speechSynthesis.speak(utterance);
  }

  function stopAllSpeech() {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    document.querySelectorAll(".speak-question-btn").forEach(btn => btn.classList.remove("speaking"));
    const readingStatus = document.getElementById("voiceReadingStatus");
    const stopAudioBtn = document.getElementById("stopAudioBtn");
    if (readingStatus) readingStatus.style.display = "none";
    if (stopAudioBtn) stopAudioBtn.style.display = "none";
  }

  // Question speaker buttons click handlers
  const speakButtons = document.querySelectorAll(".speak-question-btn");
  speakButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const qId = btn.dataset.questionId;
      const script = QUESTION_SCRIPTS[qId];

      if (btn.classList.contains("speaking")) {
        stopAllSpeech();
        return;
      }

      stopAllSpeech();
      btn.classList.add("speaking");

      speakText(script, 
        () => { btn.classList.add("speaking"); },
        () => { btn.classList.remove("speaking"); }
      );
    });
  });

  // =========================================================================
  // 3. Microphone Audio Recording via MediaRecorder (Cross-Browser, No webkitSpeechRecognition)
  // =========================================================================
  let mediaRecorder = null;
  let audioStream = null;
  let audioChunks = [];
  let currentRecordingBtn = null;
  let autoStopTimer = null;
  let recTimerInterval = null;
  let recordingSeconds = 0;

  const listeningBanner = document.getElementById("listeningBanner");
  const micFallbackAlert = document.getElementById("micFallbackAlert");
  const activeStopBtn = document.getElementById("activeStopRecordingBtn");
  const quizRecordingTimerEl = document.getElementById("quizRecordingTimer");
  const quizLangSelect = document.getElementById("quizLanguageSelect");

  // Sync language selector with localStorage
  if (quizLangSelect) {
    const savedLang = localStorage.getItem("distro_advisor_lang") || "auto";
    quizLangSelect.value = savedLang;
    quizLangSelect.addEventListener("change", () => {
      localStorage.setItem("distro_advisor_lang", quizLangSelect.value);
      const chatLang = document.getElementById("chatLanguageSelect");
      if (chatLang) chatLang.value = quizLangSelect.value;
    });
  }

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60).toString().padStart(2, "0");
    const secs = (seconds % 60).toString().padStart(2, "0");
    return `${mins}:${secs}`;
  }

  // Check if getUserMedia & MediaRecorder are supported
  const hasAudioSupport = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder);

  if (!hasAudioSupport) {
    showMicFallback("Microphone audio recording is not supported in this browser environment. The form is fully functional via touch or click.");
  }

  function showMicFallback(reason) {
    if (micFallbackAlert) {
      micFallbackAlert.style.display = "flex";
      const reasonEl = document.getElementById("micFallbackReason");
      if (reasonEl && reason) reasonEl.textContent = reason;
    }
    // Hide microphone buttons gracefully
    document.querySelectorAll(".record-question-btn").forEach(btn => btn.style.display = "none");
  }

  const recordButtons = document.querySelectorAll(".record-question-btn");
  recordButtons.forEach(btn => {
    btn.addEventListener("click", async () => {
      const questionName = btn.dataset.questionName;

      // If already recording this question, click acts as Stop
      if (btn.classList.contains("recording")) {
        stopActiveRecording();
        return;
      }

      // Stop any other active recording or speech
      stopActiveRecording();
      stopAllSpeech();

      try {
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      } catch (err) {
        console.warn("Microphone access error:", err);
        showMicFallback("Microphone permission was denied or blocked. You can still use the questionnaire with mouse or touch.");
        showVoiceToast("Microphone access was denied. Please allow microphone permissions or use mouse selection.", "error");
        return;
      }

      // Determine supported mimeType across Chrome, Edge, and Firefox
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
      recordingSeconds = 0;
      currentRecordingBtn = btn;
      btn.classList.add("recording");
      btn.innerHTML = `<span class="icon">⏹️</span> Stop`;

      if (listeningBanner) {
        listeningBanner.style.display = "block";
        const titleEl = document.getElementById("listeningTitle");
        if (titleEl) titleEl.textContent = `Listening for: Question on ${questionName.toUpperCase()}...`;
      }

      if (quizRecordingTimerEl) {
        quizRecordingTimerEl.textContent = `00:00 / 00:30`;
      }

      // Live 1-second interval timer up to 30 seconds
      recTimerInterval = setInterval(() => {
        recordingSeconds++;
        if (quizRecordingTimerEl) {
          quizRecordingTimerEl.textContent = `${formatTime(recordingSeconds)} / 00:30`;
        }
        if (recordingSeconds >= 30) {
          stopActiveRecording();
        }
      }, 1000);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const mimeType = mediaRecorder.mimeType || "audio/webm";
        const audioBlob = new Blob(audioChunks, { type: mimeType });

        // Cleanup tracks
        if (audioStream) {
          audioStream.getTracks().forEach(track => track.stop());
          audioStream = null;
        }

        // Send audio to /transcribe endpoint
        await uploadAndProcessAudio(audioBlob, questionName);
      };

      mediaRecorder.start(200);

      // Auto-stop after 30 seconds
      autoStopTimer = setTimeout(() => {
        stopActiveRecording();
      }, 30000);
    });
  });

  function stopActiveRecording() {
    if (autoStopTimer) {
      clearTimeout(autoStopTimer);
      autoStopTimer = null;
    }
    if (recTimerInterval) {
      clearInterval(recTimerInterval);
      recTimerInterval = null;
    }
    if (listeningBanner) {
      listeningBanner.style.display = "none";
    }
    if (currentRecordingBtn) {
      currentRecordingBtn.classList.remove("recording");
      currentRecordingBtn.innerHTML = `<span class="icon">🎤</span> Answer by Voice`;
      currentRecordingBtn = null;
    }
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
  }

  if (activeStopBtn) {
    activeStopBtn.addEventListener("click", () => {
      stopActiveRecording();
    });
  }

  // Send audio to /transcribe and match option
  async function uploadAndProcessAudio(blob, questionName) {
    // 4 MB size limit check
    if (blob.size > 4 * 1024 * 1024) {
      showVoiceToast("Audio recording exceeded 4 MB limit. Please speak for a shorter time.", "error");
      return;
    }

    showVoiceToast("Transcribing voice answer with Gemini AI...", "info", 3000);

    const formData = new FormData();
    let ext = "recording.webm";
    if (blob.type.includes("ogg")) ext = "recording.ogg";
    else if (blob.type.includes("mp4")) ext = "recording.mp4";

    formData.append("audio", blob, ext);
    formData.append("question", questionName);

    const selectedLang = quizLangSelect ? quizLangSelect.value : "auto";
    formData.append("language", selectedLang);

    try {
      const response = await fetch("/transcribe", {
        method: "POST",
        body: formData
      });

      if (!response.ok && response.status !== 200) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        const errorType = data.error_type || "";
        let friendlyMsg = data.error || "Transcription failed";
        if (errorType === "no_key") {
          friendlyMsg = "Gemini API key is not configured. Please set GEMINI_API_KEY in environment variables.";
        } else if (errorType === "quota_finished") {
          friendlyMsg = "Gemini API quota exceeded. Please try again in a few moments.";
        } else if (errorType === "network_error") {
          friendlyMsg = "Network error communicating with transcription service.";
        }
        showVoiceToast(`⚠️ ${friendlyMsg}`, "error", 4500);
        if (isVoiceAssistantEnabled) {
          speakText("Sorry, please try again.");
        }
        return;
      }

      const transcript = (data.transcript || "").trim();
      const matched = data.matched;
      const optionValue = data.option_value;

      if (matched && optionValue) {
        // Auto-select matched option in the UI
        selectOptionByValue(questionName, optionValue);
        showVoiceToast(`✓ Voice matched: "${transcript}" → Selected: ${optionValue}`, "success", 4500);

        if (isVoiceAssistantEnabled) {
          speakText(`Selected ${optionValue}`);
        }
      } else {
        const heardMsg = transcript ? `Heard: "${transcript}".` : "I could not hear you clearly, please try again.";
        showVoiceToast(heardMsg, "error", 4500);

        if (isVoiceAssistantEnabled) {
          speakText("I could not hear you clearly, please try again.");
        }
      }
    } catch (err) {
      console.error("Transcribe request error:", err);
      showVoiceToast("Network error communicating with server voice transcription.", "error");
      if (isVoiceAssistantEnabled) {
        speakText("Sorry, please try again.");
      }
    }
  }

  function selectOptionByValue(questionName, optionValue) {
    const groupInputs = document.querySelectorAll(`input[name='${questionName}']`);
    let matchedInput = null;
    groupInputs.forEach(input => {
      const card = input.closest(".option-card");
      if (input.value === optionValue) {
        input.checked = true;
        matchedInput = input;
        if (card) {
          card.classList.add("selected", "voice-matched");
          card.scrollIntoView({ behavior: "smooth", block: "nearest" });
          setTimeout(() => card.classList.remove("voice-matched"), 1500);
        }
      } else {
        input.checked = false;
        if (card) card.classList.remove("selected");
      }
    });

    if (matchedInput) {
      hideValidationMsg();
      updateNavButtonsState();

      // Voice answer's own select may change the question after speaking
      if (autoAdvanceTimer) clearTimeout(autoAdvanceTimer);
      autoAdvanceTimer = setTimeout(() => {
        autoAdvanceTimer = null;
        if (currentStep < totalSteps) {
          goToStep(currentStep + 1);
        } else {
          handleQuizSubmit();
        }
      }, 1200);
    }
  }

  // Toast feedback helper
  function showVoiceToast(message, type = "info", duration = 3500) {
    if (!voiceToast) return;
    voiceToast.textContent = message;
    voiceToast.className = `voice-toast ${type}`;
    voiceToast.style.display = "flex";

    if (voiceToast._timer) clearTimeout(voiceToast._timer);
    voiceToast._timer = setTimeout(() => {
      voiceToast.style.display = "none";
    }, duration);
  }

  // =========================================================================
  // 4. Wizard Step Navigation & Option Selection (1 Question per Step)
  // =========================================================================
  const wizardForm = document.getElementById("advisorWizard");
  if (!wizardForm) return;

  let currentStep = 1;
  const totalSteps = 7;
  let autoAdvanceTimer = null;

  const nextBtn = document.getElementById("nextStepBtn");
  const prevBtn = document.getElementById("prevStepBtn");
  const submitBtn = document.getElementById("submitQuizBtn");
  const progressFill = document.getElementById("progressFill");
  const quizStepLabel = document.getElementById("quizStepLabel");
  const quizStepPercent = document.getElementById("quizStepPercent");
  const quizValidationMsg = document.getElementById("quizValidationMsg");

  function hideValidationMsg() {
    if (quizValidationMsg) quizValidationMsg.style.display = "none";
  }

  function showValidationMsg(msg = "Please select an answer to continue.") {
    if (quizValidationMsg) {
      quizValidationMsg.innerHTML = `<span>⚠️ ${msg}</span>`;
      quizValidationMsg.style.display = "flex";
    }
    showVoiceToast(msg, "info", 3000);
    const activeStepEl = document.getElementById(`step-${currentStep}`);
    if (activeStepEl) {
      const grid = activeStepEl.querySelector(".options-grid");
      if (grid) {
        grid.classList.remove("quiz-shake");
        void grid.offsetWidth; // re-trigger CSS shake animation
        grid.classList.add("quiz-shake");
      }
    }
  }

  function updateNavButtonsState() {
    const activeStepEl = document.getElementById(`step-${currentStep}`);
    const hasSelection = !!(activeStepEl && activeStepEl.querySelector("input[type='radio']:checked"));

    if (nextBtn) {
      if (hasSelection) {
        nextBtn.removeAttribute("disabled");
        nextBtn.classList.remove("btn-disabled");
      } else {
        nextBtn.setAttribute("disabled", "true");
        nextBtn.classList.add("btn-disabled");
      }
    }

    if (submitBtn) {
      if (hasSelection) {
        submitBtn.removeAttribute("disabled");
        submitBtn.classList.remove("btn-disabled");
      } else {
        submitBtn.setAttribute("disabled", "true");
        submitBtn.classList.add("btn-disabled");
      }
    }
  }

  function onOptionSelected() {
    // Selecting an option ONLY highlights it and enables the Next button.
    // It must NEVER automatically advance to the next question.
    if (autoAdvanceTimer) {
      clearTimeout(autoAdvanceTimer);
      autoAdvanceTimer = null;
    }
    hideValidationMsg();
    updateNavButtonsState();
  }

  // Visual card selection listeners
  const optionCards = document.querySelectorAll(".option-card");
  optionCards.forEach(card => {
    card.addEventListener("click", (e) => {
      // Stop event bubbling so clicking an option never triggers navigation buttons
      e.stopPropagation();

      // Cancel any pending timers
      if (autoAdvanceTimer) {
        clearTimeout(autoAdvanceTimer);
        autoAdvanceTimer = null;
      }

      const radio = card.querySelector("input[type='radio']");
      if (!radio) return;
      const groupName = radio.name;

      // Deselect siblings in same group
      document.querySelectorAll(`input[name='${groupName}']`).forEach(input => {
        const parent = input.closest(".option-card");
        if (parent) parent.classList.remove("selected");
        input.checked = false;
      });

      // Select clicked card
      card.classList.add("selected");
      radio.checked = true;

      onOptionSelected();
    });
  });

  function goToStep(stepNum) {
    if (autoAdvanceTimer) {
      clearTimeout(autoAdvanceTimer);
      autoAdvanceTimer = null;
    }
    stopAllSpeech();
    stopActiveRecording();
    hideValidationMsg();

    currentStep = stepNum;
    updateWizardUI();
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (autoAdvanceTimer) {
        clearTimeout(autoAdvanceTimer);
        autoAdvanceTimer = null;
      }
      const activeStepEl = document.getElementById(`step-${currentStep}`);
      const isSelected = !!(activeStepEl && activeStepEl.querySelector("input[type='radio']:checked"));
      if (!isSelected) {
        showValidationMsg("Please select an answer before moving forward.");
        return;
      }
      if (currentStep < totalSteps) {
        goToStep(currentStep + 1);
      }
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (autoAdvanceTimer) {
        clearTimeout(autoAdvanceTimer);
        autoAdvanceTimer = null;
      }
      if (currentStep > 1) {
        goToStep(currentStep - 1);
      }
    });
  }

  function updateWizardUI() {
    // Hide all steps, show current step
    document.querySelectorAll(".wizard-step").forEach(s => s.classList.remove("active"));
    const activeStep = document.getElementById(`step-${currentStep}`);
    if (activeStep) activeStep.classList.add("active");

    // Progress bar & label (e.g. "Question 3 of 7" and "43%")
    const percent = Math.round((currentStep / totalSteps) * 100);
    if (quizStepLabel) {
      quizStepLabel.textContent = `Question ${currentStep} of ${totalSteps}`;
    }
    if (quizStepPercent) {
      quizStepPercent.textContent = `${percent}%`;
    }
    if (progressFill) {
      progressFill.style.width = `${(currentStep / totalSteps) * 100}%`;
      const track = progressFill.closest(".progress-track");
      if (track) track.setAttribute("aria-valuenow", currentStep);
    }

    // Button display & state
    if (prevBtn) prevBtn.style.display = currentStep === 1 ? "none" : "inline-flex";
    if (nextBtn) nextBtn.style.display = currentStep === totalSteps ? "none" : "inline-flex";
    if (submitBtn) submitBtn.style.display = currentStep === totalSteps ? "inline-flex" : "none";

    // Refresh disabled state depending on whether current question was answered
    updateNavButtonsState();

    // Scroll advisor card into view if offscreen
    const card = document.querySelector(".advisor-card");
    if (card) {
      const rect = card.getBoundingClientRect();
      if (rect.top < 0 || rect.top > 250) {
        card.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }
  }

  // =========================================================================
  // 5. Form Submission & Result Rendering
  // =========================================================================
  let lastRecommendationResult = null;

  async function handleQuizSubmit() {
    if (autoAdvanceTimer) {
      clearTimeout(autoAdvanceTimer);
      autoAdvanceTimer = null;
    }
    stopAllSpeech();
    stopActiveRecording();

    const activeStepEl = document.getElementById(`step-${currentStep}`);
    const isSelected = !!(activeStepEl && activeStepEl.querySelector("input[type='radio']:checked"));
    if (!isSelected) {
      showValidationMsg("Please select an answer before getting your recommendation.");
      return;
    }

    const formData = new FormData(wizardForm);
    const payload = {
      ram: formData.get("ram"),
      storage: formData.get("storage"),
      cpu: formData.get("cpu"),
      experience: formData.get("experience"),
      prev_experience: formData.get("prev_experience"),
      purpose: formData.get("purpose"),
      preference: formData.get("preference")
    };

    // Show loading overlay
    const wizardStepsContainer = document.getElementById("wizardFormContainer");
    const loadingOverlay = document.getElementById("advisorLoading");
    const resultContainer = document.getElementById("resultContainer");
    const mainCard = document.getElementById("advisorMainCard");

    if (wizardStepsContainer) wizardStepsContainer.style.display = "none";
    if (loadingOverlay) loadingOverlay.style.display = "block";

    const loadingMessages = [
      "Analyzing CPU architecture & RAM ceilings...",
      "Evaluating software package ecosystems...",
      "Scoring desktop environment overheads...",
      "Synthesizing your personalized match..."
    ];
    let msgIdx = 0;
    const loadingTextEl = document.getElementById("loadingSubText");
    const interval = setInterval(() => {
      msgIdx = (msgIdx + 1) % loadingMessages.length;
      if (loadingTextEl) loadingTextEl.textContent = loadingMessages[msgIdx];
    }, 350);

    try {
      const response = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      clearInterval(interval);

      if (data.success) {
        lastRecommendationResult = data.data;
        renderResults(data.data);
        if (loadingOverlay) loadingOverlay.style.display = "none";
        if (mainCard) mainCard.classList.add("has-results");
        if (resultContainer) {
          resultContainer.classList.add("active");
          resultContainer.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      } else {
        alert("Error calculating recommendations. Please try again.");
        if (wizardStepsContainer) wizardStepsContainer.style.display = "block";
        if (loadingOverlay) loadingOverlay.style.display = "none";
      }
    } catch (err) {
      clearInterval(interval);
      console.error("Submission failed:", err);
      wizardForm.submit();
    }
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", (e) => {
      e.preventDefault();
      handleQuizSubmit();
    });
  }

  function renderResults(res) {
    const best = res.best_match;
    const alts = res.alternatives || [];
    const warning = res.advisory_warning;

    // Best match fields
    document.getElementById("resDistroName").textContent = best.name;
    document.getElementById("resTagline").textContent = best.tagline;
    document.getElementById("resLogo").src = `/static/images/distros/${best.id}.svg`;
    document.getElementById("resLogo").alt = best.name;
    document.getElementById("resBadge").textContent = best.badge || "Top Recommended Match";

    // Specs
    document.getElementById("specRam").textContent = `${best.min_ram_gb}GB Min / ${best.rec_ram_gb}GB Rec`;
    document.getElementById("specStorage").textContent = `${best.min_storage_gb}GB Min / ${best.rec_storage_gb}GB Rec`;
    document.getElementById("specDE").textContent = best.desktop_environment;
    document.getElementById("specPkg").textContent = best.package_manager;
    document.getElementById("specFamily").textContent = best.family;
    document.getElementById("specRelease").textContent = best.release_model;

    // Website button
    const siteBtn = document.getElementById("resWebsiteBtn");
    if (siteBtn) siteBtn.href = best.website;

    // Reasons
    const reasonsList = document.getElementById("resReasonsList");
    reasonsList.innerHTML = "";
    (best.reasons || []).forEach(r => {
      const li = document.createElement("li");
      li.className = "reason-item";
      li.innerHTML = `<span class="reason-bullet">✓</span><span>${r}</span>`;
      reasonsList.appendChild(li);
    });

    // Pros & Cons
    const prosList = document.getElementById("resProsList");
    prosList.innerHTML = "";
    (best.pros || []).forEach(p => {
      const li = document.createElement("li");
      li.innerHTML = `<span>+</span><span>${p}</span>`;
      prosList.appendChild(li);
    });

    const consList = document.getElementById("resConsList");
    consList.innerHTML = "";
    (best.cons || []).forEach(c => {
      const li = document.createElement("li");
      li.innerHTML = `<span>-</span><span>${c}</span>`;
      consList.appendChild(li);
    });

    // Advisory warning
    const advBox = document.getElementById("resAdvisoryBox");
    if (warning) {
      advBox.style.display = "flex";
      document.getElementById("resAdvisoryText").textContent = warning;
    } else {
      advBox.style.display = "none";
    }

    // Gauge Score Animation
    const gaugeText = document.getElementById("gaugeScoreText");
    const gaugeCircle = document.getElementById("gaugeCircle");
    const targetPercent = best.match_percentage;

    gaugeText.textContent = `${targetPercent}%`;
    const circumference = 2 * Math.PI * 36; // r=36 -> ~226
    const offset = circumference - (targetPercent / 100) * circumference;
    setTimeout(() => {
      gaugeCircle.style.strokeDashoffset = offset;
    }, 150);

    // Alternatives
    const altsContainer = document.getElementById("resAlternativesGrid");
    altsContainer.innerHTML = "";
    alts.forEach(alt => {
      const altCard = document.createElement("div");
      altCard.className = "alt-card";
      altCard.innerHTML = `
        <div>
          <div class="alt-top">
            <div class="alt-identity">
              <img src="/static/images/distros/${alt.id}.svg" alt="${alt.name}" class="alt-logo">
              <div>
                <h4 class="alt-name">${alt.name}</h4>
                <span class="spec-key">${alt.family}</span>
              </div>
            </div>
            <span class="alt-match-tag">${alt.match_percentage}% Match</span>
          </div>
          <p class="alt-tagline">${alt.tagline}</p>
          <ul class="alt-reasons">
            ${(alt.reasons || []).map(r => `<li>${r}</li>`).join("")}
          </ul>
        </div>
        <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
          <a href="/distro/${alt.id}" class="btn btn-secondary" style="flex: 1; justify-content: center; font-size: 0.85rem; padding: 0.5rem;">View Profile</a>
          <a href="${alt.website}" target="_blank" rel="noopener" class="btn btn-primary" style="flex: 1; justify-content: center; font-size: 0.85rem; padding: 0.5rem;">Website</a>
        </div>
      `;
      altsContainer.appendChild(altCard);
    });

    // Compare with alternatives link
    const compareLink = document.getElementById("compareLink");
    if (compareLink && alts.length >= 2) {
      compareLink.href = `/compare?d1=${best.id}&d2=${alts[0].id}&d3=${alts[1].id}`;
    }
  }

  // =========================================================================
  // 6. Voice Result Reader ("Listen to Result" & "Stop Audio")
  // =========================================================================
  const listenResultBtn = document.getElementById("listenResultBtn");
  const stopAudioBtn = document.getElementById("stopAudioBtn");
  const readingStatus = document.getElementById("voiceReadingStatus");

  if (listenResultBtn) {
    listenResultBtn.addEventListener("click", () => {
      // Find details from DOM if not in variable
      const name = document.getElementById("resDistroName")?.textContent || "your recommended distribution";
      const percent = document.getElementById("gaugeScoreText")?.textContent || "95%";
      const tagline = document.getElementById("resTagline")?.textContent || "";
      
      const reasonsEls = document.querySelectorAll("#resReasonsList .reason-item span:nth-child(2)");
      const reasons = Array.from(reasonsEls).map(el => el.textContent.trim()).slice(0, 3);
      const reasonsText = reasons.length > 0 ? `Key reasons for this recommendation: ${reasons.join(". ")}.` : "";

      const altNames = Array.from(document.querySelectorAll("#resAlternativesGrid .alt-name")).map(el => el.textContent.trim());
      const altTags = Array.from(document.querySelectorAll("#resAlternativesGrid .alt-match-tag")).map(el => el.textContent.trim());
      let altsText = "";
      if (altNames.length >= 2) {
        altsText = `Your two alternative distributions are ${altNames[0]} with ${altTags[0] || 'high'} match, and ${altNames[1]} with ${altTags[1] || 'good'} match.`;
      }

      const fullResultText = `Your best Linux distribution match is ${name}, with a ${percent} match score. ${tagline}. ${reasonsText} ${altsText}`;

      stopAllSpeech();

      speakText(fullResultText, 
        () => {
          if (stopAudioBtn) stopAudioBtn.style.display = "inline-flex";
          if (readingStatus) readingStatus.style.display = "inline-flex";
        },
        () => {
          if (stopAudioBtn) stopAudioBtn.style.display = "none";
          if (readingStatus) readingStatus.style.display = "none";
        }
      );
    });
  }

  if (stopAudioBtn) {
    stopAudioBtn.addEventListener("click", () => {
      stopAllSpeech();
    });
  }

  // Retake button ("Take Questionnaire Again / Start Again")
  const retakeBtn = document.getElementById("retakeQuizBtn");
  if (retakeBtn) {
    retakeBtn.addEventListener("click", () => {
      stopAllSpeech();
      stopActiveRecording();
      if (autoAdvanceTimer) {
        clearTimeout(autoAdvanceTimer);
        autoAdvanceTimer = null;
      }

      const wizardStepsContainer = document.getElementById("wizardFormContainer");
      const resultContainer = document.getElementById("resultContainer");
      const mainCard = document.getElementById("advisorMainCard");

      // Reset form selections and card highlights
      if (wizardForm) wizardForm.reset();
      document.querySelectorAll(".option-card").forEach(c => c.classList.remove("selected", "voice-matched"));

      if (mainCard) mainCard.classList.remove("has-results");
      if (resultContainer) resultContainer.classList.remove("active");
      if (wizardStepsContainer) wizardStepsContainer.style.display = "block";

      currentStep = 1;
      updateWizardUI();

      if (mainCard) mainCard.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
});
