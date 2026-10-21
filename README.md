# 🐧 Linux Distribution Advisor

An intelligent, beginner-friendly web application built with **Python**, **Flask**, **SQLite**, and a **Global Voice & Text Linux Advisor Assistant** powered by **faster-whisper** and browser **SpeechSynthesis**. It assesses a user's computer hardware and workflow requirements to recommend the most suitable Linux distribution.

---

## 💬 Global Voice & Text Linux Advisor Assistant (Free, No API Key Needed)

Available in the bottom-right corner of **every page** (separate from the step-by-step quiz), this dedicated assistant helps users pick a Linux distribution conversationally via text or voice.

### 1. Interactive Chat Window
- **Floating Launcher Button**: Positioned in the corner of every page (`/`, `/distros`, `/compare`, `/guide`). Clicking opens a glassmorphic chat window.
- **Natural Conversation**: Users can type any question or speak directly into their microphone.

### 2. Cross-Browser Voice Input (Firefox, Chrome & Edge)
- **Zero `webkitSpeechRecognition`**: Uses standard `navigator.mediaDevices.getUserMedia` and `MediaRecorder` API to record voice across all modern browsers.
- **Local Neural Transcription**: Audio is sent to `POST /transcribe` where **`faster-whisper`** (`tiny` model in CPU `int8` mode, loaded once as a server singleton) turns speech into text.
- **Puts Text in Chat**: The transcribed voice is automatically placed into the chat input, just as if typed, and submitted.

### 3. Domain-Specific Intelligence (No Paid API)
- **Linux Distribution Focus Only**: The assistant is strictly specialized in helping users choose a Linux operating system. If asked unrelated trivia or off-topic questions (e.g. *"What is the capital of France?"*), it politely explains its scope and redirects the user to specify PC specs or computing goals.
- **Heuristic Parameter Extraction**: Automatically detects and extracts key variables from natural language:
  - **RAM size**: e.g., *"2GB"*, *"8GB"*, *"16 gigabytes"*, *"low memory"*.
  - **Purpose**: e.g., *"gaming on Steam"*, *"Python coding"*, *"office spreadsheets"*, *"school homework"*, *"security / pentesting"*, *"daily browsing"*.
  - **Hardware Age / CPU**: e.g., *"old 10-year-old laptop"*, *"dual core celeron"*, *"modern Ryzen 7"*, *"Raspberry Pi"*.
  - **Experience & Preference**: e.g., *"beginner switching from Windows"*, *"lightweight"*, *"customizable"*.
- **Scoring Engine Integration**: Runs the extracted signals through the project's multi-factor scoring model to determine the best match and top alternatives.
- **Follow-up Prompts**: If the user's message does not provide enough details (e.g. *"Help me choose a distro"*), the assistant asks a concise follow-up question (e.g. *"What will you use it for, and roughly how much RAM do you have?"*).
- **Multi-Turn Context**: Maintains conversational memory across follow-up queries.

### 4. Rich Assistant Replies & Voice Mode
- **Formatted Recommendation**: Displays the recommended distribution name, logo, match percentage, and customized explanation bullets directly inside the chat bubble, with quick links to view technical specs or compare.
- **Voice Mode Toggle (ON / OFF)**:
  - When Voice Mode is ON, the assistant automatically reads its answers aloud using browser `window.speechSynthesis` (slow, clear, friendly rate: `0.92`).
  - Users can also click the 🔊 button on any message to replay it.

### 5. Fallback Protection
- If microphone access is blocked or unavailable, the microphone icon is automatically hidden, and typing remains 100% operational.
- Real-time animated sound-wave banner displays while recording.

---

## 🎙️ Quiz Voice Assistant Features

In addition to the global chat assistant, the main 3-step questionnaire wizard features:
- **"🔊 Listen" button on each question**: Reads questions and choices aloud using `speechSynthesis`.
- **"🎤 Answer by Voice" button on each question**: Uses `MediaRecorder` + `faster-whisper` to auto-select radio cards based on spoken keywords (*"eight gb"*, *"coding"*, *"gaming"*, etc.).
- **"🔊 Listen to Result"**: Reads the final match score, reasons, and alternatives aloud.
- **Master Voice Toggle**: Lets users turn voice guidance on or off anytime.

---

## 🌟 Key Application Features

- **Multi-Vector Recommendation Engine**: Accurately analyzes RAM, Storage, CPU architecture, Computer experience level, Previous Linux history, Primary purpose, and Philosophy preferences (not random selection).
- **Match Score & Dynamic Explanations**: Computes a percentage match score (with an animated radial score meter) and generates 4 tailored, contextual reasons detailing why that distribution fits their specific hardware and goals.
- **Top Pick + 2 Alternatives**: Recommends the #1 best match alongside 2 strong alternative distributions with their individual match scores.
- **Nuanced Pros & Cons**: Provides balanced, honest advantages and trade-offs for every distribution.
- **Safety Advisories**: Includes safeguards for newcomers (e.g., warns against daily-driving Kali Linux or unguided Arch installations, advising safer alternatives like Mint/Ubuntu or virtual machines).
- **Distro Explorer & Comparison Tool**: Full searchable catalog with live filters and a side-by-side spec comparison matrix.
- **Beginner's Launchpad**: Step-by-step instructions for creating a bootable USB using Rufus/Ventoy, accessing BIOS/UEFI boot menus, trying Live sessions risk-free, and dual-booting alongside Windows.
- **Modern UI & Aesthetics**: Dark and light mode toggle, glassmorphic cards, responsive mobile/desktop layouts, and zero external image dependencies (all SVG vector logos built-in).
- **SQLite History & Trends**: Logs recommendations and generates community popularity stats.

---

## 📁 Project Structure

```text
distrosuggestor/
├── app.py                     # Flask application entry point, API routes, /transcribe & /api/chat_advisor
├── chat_advisor.py            # Free NLP heuristic parameter extraction & chat logic
├── voice_engine.py            # faster-whisper singleton loader & keyword-to-option mapper
├── recommender.py             # Multi-factor algorithmic scoring and reasoning engine
├── distro_data.py             # Knowledge base of 12+ Linux distributions and specs
├── database.py                # SQLite persistence layer for sessions and analytics
├── requirements.txt           # Python dependency requirements (Flask, faster-whisper, av<14)
├── test_advisor.py            # Automated test suite (scoring logic, endpoints, voice, chat)
├── distro_advisor.db          # Auto-generated SQLite database
├── static/
│   ├── css/
│   │   └── style.css          # Design system, glassmorphism, voice bars & floating chat widget
│   ├── js/
│   │   ├── app.js             # Quiz wizard controller, SpeechSynthesis, MediaRecorder
│   │   ├── chat_assistant.js  # Global floating voice and text chat assistant controller
│   │   └── compare.js         # Side-by-side comparison dropdown controller
│   └── images/
│       └── distros/           # Crisp vector SVG logos for every distribution
│           ├── arch-linux.svg
│           ├── debian.svg
│           ├── fedora.svg
│           ├── kali-linux.svg
│           ├── linux-mint.svg
│           ├── lubuntu.svg
│           ├── manjaro.svg
│           ├── opensuse-tumbleweed.svg
│           ├── pop-os.svg
│           ├── puppy-linux.svg
│           ├── ubuntu.svg
│           └── zorin-os.svg
└── templates/
    ├── base.html              # Core layout with navigation, dark/light mode & chat widget
    ├── chat_widget.html       # Floating chat assistant launcher and panel template
    ├── index.html             # Advisor questionnaire wizard, voice controls, and results
    ├── distros.html           # Full searchable and filterable distro catalog
    ├── distro_detail.html     # Deep-dive profile page for individual distributions
    ├── compare.html           # Side-by-side 2- or 3-way distro comparison
    └── guide.html             # Beginner's USB, BIOS, and terminal guide
```

---

## 🚀 Instructions to Run the Application on Linux

Follow these step-by-step instructions on any Linux distribution (Ubuntu, Debian, Linux Mint, Fedora, Arch, openSUSE):

### 1. Install Prerequisites

Ensure Python 3, pip, and venv are installed on your Linux system:

**On Ubuntu / Debian / Linux Mint / Pop!_OS:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

**On Fedora / RHEL:**
```bash
sudo dnf install -y python3 python3-pip git
```

**On Arch Linux / Manjaro:**
```bash
sudo pacman -Syu python python-pip git
```

**On openSUSE:**
```bash
sudo zypper install python3 python3-pip git
```

---

### 2. Set Up the Project

Navigate to your project directory:

```bash
cd /path/to/distrosuggestor
```

Create an isolated Python virtual environment:
```bash
python3 -m venv venv
```

Activate the virtual environment:
```bash
source venv/bin/activate
```

*(Your terminal prompt will now show `(venv)`).*

---

### 3. Install Python Dependencies

Install the required packages using `pip`:
```bash
pip install -r requirements.txt
```

---

### 4. Run the Automated Tests

Verify that the algorithmic scoring, voice keyword matcher, chat advisor, and Flask routes are functional:
```bash
python3 test_advisor.py
```
*Expected output: `Ran 11 tests ... OK`*

---

### 5. Launch the Web Application

To run the application locally:
```bash
python3 app.py
```

Open your web browser (**Firefox**, **Chrome**, or **Edge**) and navigate to:
```text
http://localhost:5000
```

- Click the floating **🐧 Ask Linux Advisor** button in the bottom right corner of any page to open the Voice & Text Assistant!
- You can also take the full step-by-step quiz or browse distributions and comparisons.

---

## 🛡️ License

This project is licensed under the open-source MIT License.
