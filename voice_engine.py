"""
Voice Assistant Engine for Linux Distribution Advisor.
Pre-loads the faster-whisper model once on startup and performs natural language
keyword matching to map voice transcriptions to form options.
"""

import os
import re
import tempfile
import logging
from typing import Optional, Tuple, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global singleton model reference
_WHISPER_MODEL = None

def get_whisper_model():
    """
    Load the whisper model (tiny, cpu, int8) once as a singleton.
    """
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            from faster_whisper import WhisperModel
            logger.info("Initializing faster-whisper model ('tiny', CPU, int8)...")
            # Using tiny model for rapid CPU transcription on any hardware
            _WHISPER_MODEL = WhisperModel("tiny", device="cpu", compute_type="int8")
            logger.info("faster-whisper model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load faster-whisper model: {e}")
            _WHISPER_MODEL = None
    return _WHISPER_MODEL

def transcribe_audio_file(file_path: str, language: Optional[str] = "en") -> str:
    """
    Transcribe an audio file using the pre-loaded Whisper model.
    Returns the recognized text string. If language is None, Whisper auto-detects language.
    """
    model = get_whisper_model()
    if model is None:
        raise RuntimeError("Whisper model is not available.")
    
    kwargs = {"beam_size": 3}
    if language:
        kwargs["language"] = language

    segments, info = model.transcribe(file_path, **kwargs)
    transcript = " ".join([seg.text for seg in segments]).strip()
    return transcript

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
    # so specific long phrases ("more than sixteen gb") match before ("sixteen gb")
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
