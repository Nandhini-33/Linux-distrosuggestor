"""
Voice Assistant Engine for Linux Distribution Advisor.
Speech-to-text powered by Google Gemini API (google-genai) in-memory for online & Vercel deployment,
with optional lazy local faster-whisper fallback for offline development.
"""

import os
import re
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

# Global singleton model reference for optional local faster-whisper fallback only
_WHISPER_MODEL = None


def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from environment."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key and key != "your_key_here":
        return key
    return ""


def get_gemini_model() -> str:
    """Retrieve Gemini Model name from environment with free-tier Flash default."""
    return os.environ.get("GEMINI_MODEL", "").strip() or "gemini-2.5-flash"


def is_gemini_configured() -> bool:
    """Check if a valid Gemini API key is configured."""
    return bool(get_gemini_api_key())


def get_whisper_model():
    """
    Optional lazy loader for local faster-whisper fallback.
    Never run automatically at startup. Never run on Vercel.
    """
    global _WHISPER_MODEL
    # Never attempt on Vercel (read-only filesystem & RAM constraints)
    if os.environ.get("VERCEL"):
        return None

    if _WHISPER_MODEL is None:
        try:
            from faster_whisper import WhisperModel
            logger.info("Initializing optional local faster-whisper model ('tiny', CPU, int8)...")
            _WHISPER_MODEL = WhisperModel("tiny", device="cpu", compute_type="int8")
            logger.info("Local faster-whisper model loaded successfully.")
        except Exception as e:
            logger.warning(f"faster-whisper is not available for local fallback: {e}")
            _WHISPER_MODEL = None
    return _WHISPER_MODEL


def transcribe_audio_file(file_path: str, language: Optional[str] = "en") -> str:
    """
    Legacy helper kept for local testing fallback.
    """
    model = get_whisper_model()
    if model is None:
        raise RuntimeError("Whisper model is not available.")
    kwargs = {"beam_size": 3}
    if language:
        kwargs["language"] = language
    segments, info = model.transcribe(file_path, **kwargs)
    return " ".join([seg.text for seg in segments]).strip()


def transcribe_with_gemini(
    audio_bytes: bytes,
    mime_type: str = "audio/webm",
    language_hint: Optional[str] = None
) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """
    Transcribe audio bytes using Google Gemini API in-memory.
    Never saves audio to disk.
    Returns: (success: bool, transcript: str, error_type: Optional[str], error_message: Optional[str])
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return False, "", "no_key", "Gemini API key is not configured. Please set GEMINI_API_KEY in your environment variables."

    model_name = get_gemini_model()

    # Exact required system instruction
    base_instruction = (
        "Transcribe this audio exactly in the language spoken. "
        "Do not translate. Return only the spoken text. "
        "If there is no clear speech, return an empty string."
    )

    hint_map = {
        "en": "The spoken language is English.",
        "ta": "The spoken language is Tamil (தமிழ்). Transcribe in Tamil script or spoken words as spoken.",
        "hi": "The spoken language is Hindi (हिन्दी). Transcribe in Devanagari script or spoken words as spoken.",
        "ml": "The spoken language is Malayalam (മലയാളം). Transcribe in Malayalam script or spoken words as spoken.",
        "te": "The spoken language is Telugu (తెలుగు). Transcribe in Telugu script or spoken words as spoken."
    }

    prompt = base_instruction
    if language_hint and language_hint.lower() in hint_map:
        prompt += f" Hint: {hint_map[language_hint.lower()]}"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)

        response = client.models.generate_content(
            model=model_name,
            contents=[audio_part, prompt]
        )

        raw_text = (response.text or "").strip()
        # Clean any accidental outer quotes wrapping the result
        if (raw_text.startswith('"') and raw_text.endswith('"')) or (raw_text.startswith("'") and raw_text.endswith("'")):
            raw_text = raw_text[1:-1].strip()

        return True, raw_text, None, None

    except Exception as e:
        err_str = str(e)
        logger.error(f"Gemini transcription error: {err_str}")

        # Check for quota exceeded (429 or RESOURCE_EXHAUSTED)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
            return False, "", "quota_finished", "Gemini API quota exceeded. Please try again in a few moments or check your API key quota."

        # Check for network or connection issues
        if "connection" in err_str.lower() or "timeout" in err_str.lower() or "failed to resolve" in err_str.lower():
            return False, "", "network_error", "Network error while connecting to transcription service. Please check your internet connection."

        # Check for invalid key
        if "API_KEY_INVALID" in err_str or "key not valid" in err_str.lower():
            return False, "", "no_key", "Gemini API key is invalid. Please verify your GEMINI_API_KEY."

        return False, "", "transcription_error", f"Transcription service error: {err_str}"


def transcribe_audio(
    audio_bytes: bytes,
    mime_type: str = "audio/webm",
    language_hint: Optional[str] = None,
    question_key: Optional[str] = None
) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """
    Main entry point for audio transcription.
    Processes audio completely in memory (never saved to disk).
    Tries Gemini in-memory first.
    If no Gemini key and running locally (not on Vercel), attempts optional faster-whisper fallback.
    Returns: (success: bool, transcript: str, error_type: Optional[str], error_message: Optional[str])
    """
    if not audio_bytes:
        return False, "", "empty_audio", "No audio data received."

    # Enforce strict 4 MB limit
    if len(audio_bytes) > 4 * 1024 * 1024:
        return False, "", "file_too_large", "Audio recording exceeds the 4 MB limit."

    # Normalize mime_type
    clean_mime = mime_type.lower()
    if "webm" in clean_mime:
        clean_mime = "audio/webm"
    elif "ogg" in clean_mime:
        clean_mime = "audio/ogg"
    elif "mp4" in clean_mime or "m4a" in clean_mime:
        clean_mime = "audio/mp4"
    elif "wav" in clean_mime:
        clean_mime = "audio/wav"
    else:
        clean_mime = "audio/webm"

    # Primary: Gemini API
    api_key = get_gemini_api_key()
    if api_key:
        return transcribe_with_gemini(audio_bytes, clean_mime, language_hint)

    # Optional local fallback (only if NOT on Vercel and faster-whisper is installed)
    if not os.environ.get("VERCEL"):
        try:
            model = get_whisper_model()
            if model is not None:
                import tempfile
                suffix = ".webm" if "webm" in clean_mime else (".ogg" if "ogg" in clean_mime else ".wav")
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp_path = tmp.name
                    tmp.write(audio_bytes)
                try:
                    lang = None if language_hint in ("auto", None) else language_hint
                    transcript = transcribe_audio_file(tmp_path, language=lang)
                    return True, transcript, None, None
                finally:
                    if os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
        except Exception as local_err:
            logger.warning(f"Local whisper fallback failed: {local_err}")

    # Neither Gemini key nor working local whisper
    return False, "", "no_key", "Gemini API key is not configured. Please set GEMINI_API_KEY in your environment variables."


# Keyword matching rules for each questionnaire field
KEYWORD_MAPPINGS = {
    "ram": [
        ("<2GB", [
            "less than 2", "under 2", "<2", "below 2", "1 gb", "1 gig", "one gb",
            "one gigabyte", "1.5 gb", "tiny ram", "minimum ram", "lowest"
        ]),
        ("2GB - 4GB", [
            "2 to 4", "2-4", "two to four", "2 gb", "two gb", "2 gigabytes", "3 gb",
            "three gb", "4 gb", "four gb", "budget ram", "budget laptop"
        ]),
        ("4GB - 8GB", [
            "4 to 8", "4-8", "four to eight", "6 gb", "six gb", "8 gb", "eight gb",
            "8 gig", "8 gigabytes", "eight gigabytes", "standard", "average", "normal"
        ]),
        ("8GB - 16GB", [
            "8 to 16", "8-16", "eight to sixteen", "12 gb", "twelve gb", "16 gb",
            "sixteen gb", "sixteen gigabytes", "multitask", "fast ram", "heavy"
        ]),
        ("16GB+", [
            "16 plus", "16 or more", "more than 16", "more than sixteen", "over 16",
            "over sixteen", "above 16", "above sixteen", "32 gb", "thirty two",
            "64 gb", "high end ram", "monster", "maximum"
        ])
    ],
    "storage": [
        ("<20GB", [
            "less than 20", "under 20", "<20", "below 20", "10 gb", "15 gb",
            "small storage", "tight", "small drive", "small usb"
        ]),
        ("20GB - 50GB", [
            "20 to 50", "20-50", "twenty to fifty", "30 gb", "40 gb", "50 gb",
            "fifty gb", "dual boot", "dual boot partition"
        ]),
        ("50GB - 100GB", [
            "50 to 100", "50-100", "fifty to one hundred", "60 gb", "80 gb",
            "100 gb", "hundred gb", "comfortable", "plenty"
        ]),
        ("100GB+", [
            "100 plus", "more than 100", "more than hundred", "over 100", "over hundred",
            "above 100", "hundred plus", "200 gb", "500 gb", "terabyte", "1 tb", "one tb", "huge", "dedicated drive"
        ])
    ],
    "cpu": [
        ("Older / Low-end Dual Core (Atom, Celeron, Core 2 Duo)", [
            "older", "low end", "budget", "celeron", "atom", "dual core", "pentium",
            "core 2 duo", "core two", "slow cpu", "old laptop", "athlon", "two core"
        ]),
        ("Mid-range Quad Core (Intel i3/i5, AMD Ryzen 3/5)", [
            "mid range", "quad core", "four core", "i3", "i5", "core i3", "core i5",
            "intel i5", "intel i3", "ryzen 3", "ryzen 5", "amd ryzen", "standard cpu"
        ]),
        ("High-end Multi-core (Intel i7/i9, AMD Ryzen 7/9)", [
            "high end", "multi core", "many cores", "i7", "i9", "core i7", "core i9",
            "intel i7", "intel i9", "ryzen 7", "ryzen 9", "workstation", "gaming cpu", "fastest"
        ]),
        ("ARM / Raspberry Pi", [
            "arm", "raspberry", "raspberry pi", "single board", "pi 4", "pi 5",
            "apple silicon", "m1", "m2", "m3", "asahi"
        ])
    ],
    "experience": [
        ("Beginner", [
            "beginner", "newbie", "starter", "novice", "new", "first time", "simple",
            "windows user", "mac user", "not technical", "no coding", "basic"
        ]),
        ("Intermediate", [
            "intermediate", "medium", "casual", "average", "some experience",
            "know some terminal", "troubleshoot", "moderate"
        ]),
        ("Advanced", [
            "advanced", "power user", "expert", "pro", "terminal", "sysadmin",
            "developer", "engineer", "geek", "experienced", "custom kernel"
        ])
    ],
    "prev_experience": [
        ("None / First time", [
            "none", "first time", "never used", "zero", "never", "no experience",
            "brand new", "first timer"
        ]),
        ("Tested in VM or Live USB", [
            "vm", "virtual machine", "virtualbox", "live usb", "tested", "test",
            "tried in vm", "usb boot"
        ]),
        ("Dual boot or casual user", [
            "dual boot", "casual", "installed before", "used it sometimes", "dual booting"
        ]),
        ("Daily driver / Server experience", [
            "daily driver", "server", "production", "vps", "used for years",
            "work linux", "main os"
        ])
    ],
    "purpose": [
        ("Programming", [
            "programming", "coding", "developer", "development", "python", "javascript",
            "c++", "software", "web dev", "code", "coder", "docker", "vs code"
        ]),
        ("Gaming", [
            "gaming", "games", "game", "steam", "gamer", "play games", "proton",
            "graphics", "gpu", "lutris"
        ]),
        ("Office", [
            "office", "work", "documents", "spreadsheets", "word", "excel",
            "libreoffice", "pdf", "printing", "business"
        ]),
        ("Education", [
            "education", "school", "college", "study", "student", "homework",
            "learning", "university", "classes"
        ]),
        ("Security", [
            "security", "hacking", "pentesting", "penetration testing", "ethical hacking",
            "cybersecurity", "cyber", "kali", "forensics", "infosec"
        ]),
        ("General use", [
            "general", "general use", "browsing", "youtube", "netflix", "web",
            "casual", "daily", "internet", "movies", "everyday"
        ])
    ],
    "preference": [
        ("Easy to use", [
            "easy", "easy to use", "simple", "user friendly", "out of the box",
            "familiar", "convenient", "straightforward"
        ]),
        ("Lightweight", [
            "lightweight", "fast", "light", "speed", "battery", "low ram",
            "feather", "responsive", "quick", "snappy"
        ]),
        ("Customizable", [
            "customizable", "customize", "tweak", "themes", "flexibility", "control",
            "custom", "configure", "tailor"
        ]),
        ("Rock-solid stability", [
            "stability", "stable", "rock solid", "never crash", "rock solid stability",
            "reliable", "dependable", "long term"
        ]),
        ("Cutting-edge", [
            "cutting edge", "latest", "rolling", "newest", "bleeding edge",
            "fresh", "up to date", "modern"
        ])
    ]
}


def match_voice_to_option(question_key: str, transcript: str) -> Optional[str]:
    """
    Match spoken transcript to the nearest valid option value for question_key.
    Returns matched option string or None if unmapped.
    """
    if not transcript or question_key not in KEYWORD_MAPPINGS:
        return None

    norm_text = transcript.lower().strip()
    norm_text = re.sub(r"[^\w\s\+\<\>\-]", " ", norm_text)

    options = KEYWORD_MAPPINGS[question_key]

    # Check for direct option name match
    for option_val, _ in options:
        if option_val.lower() == norm_text or f" {option_val.lower()} " in f" {norm_text} ":
            return option_val

    # Collect all (kw, option_val) and sort by kw length descending
    all_kws = []
    for option_val, keywords in options:
        for kw in keywords:
            all_kws.append((kw, option_val))
    all_kws.sort(key=lambda x: len(x[0]), reverse=True)

    for kw, option_val in all_kws:
        if kw in norm_text:
            return option_val

    # Token overlap fallback
    tokens = set(norm_text.split())
    best_option = None
    best_matches = 0

    for option_val, keywords in options:
        count = 0
        for kw in keywords:
            kw_tokens = set(kw.split())
            if kw_tokens.issubset(tokens):
                count += len(kw_tokens) * 2
            elif len(kw_tokens.intersection(tokens)) > 0:
                count += 1
        if count > best_matches and count >= 2:
            best_matches = count
            best_option = option_val

    return best_option
