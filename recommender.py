"""
Recommendation Engine for Linux Distribution Advisor.
Performs deterministic, multi-factor heuristic scoring based on user hardware,
experience level, primary computing goals, and personal preferences.
"""

from typing import Dict, Any, List, Tuple
from distro_data import DISTRIBUTIONS, get_distro_by_id

# RAM mapping helper to numeric gigabytes for comparison
RAM_LOOKUP = {
    "<2GB": 1.5,
    "2GB - 4GB": 4.0,
    "4GB - 8GB": 8.0,
    "8GB - 16GB": 16.0,
    "16GB+": 32.0
}

# Storage mapping helper to numeric gigabytes
STORAGE_LOOKUP = {
    "<20GB": 18,
    "20GB - 50GB": 40,
    "50GB - 100GB": 80,
    "100GB+": 250
}

def parse_ram_to_gb(ram_val: Any) -> float:
    """Normalize RAM input to numeric GB."""
    if isinstance(ram_val, (int, float)):
        return float(ram_val)
    ram_str = str(ram_val).strip()
    return RAM_LOOKUP.get(ram_str, 8.0)

def parse_storage_to_gb(storage_val: Any) -> int:
    """Normalize storage input to numeric GB."""
    if isinstance(storage_val, (int, float)):
        return int(storage_val)
    st_str = str(storage_val).strip()
    return STORAGE_LOOKUP.get(st_str, 50)

def evaluate_distro(distro: Dict[str, Any], user_input: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Score a single distro against the user's answers.
    Returns (score, list_of_specific_reason_bullets).
    Max theoretical score ~ 100 points.
    """
    score = 50.0  # Base score
    reasons = []

    user_ram_gb = parse_ram_to_gb(user_input.get("ram", "4GB - 8GB"))
    user_storage_gb = parse_storage_to_gb(user_input.get("storage", "20GB - 50GB"))
    experience = user_input.get("experience", "Beginner")
    purpose = user_input.get("purpose", "General use")
    cpu = user_input.get("cpu", "Mid-range Quad Core")
    preference = user_input.get("preference", "Easy to use")
    prev_exp = user_input.get("prev_experience", "None / First time")

    # 1. RAM Hardware Evaluation (Max +/- 18 pts)
    if user_ram_gb < distro["min_ram_gb"]:
        score -= 40.0  # Severe mismatch - won't run smoothly
    elif user_ram_gb >= distro["rec_ram_gb"]:
        score += 15.0
        if user_ram_gb <= 4.0 and distro["min_ram_gb"] <= 2.0:
            reasons.append(f"Ideal fit for your {user_input.get('ram', 'low')} RAM; operates cleanly without freezing.")
        elif user_ram_gb >= 16.0:
            reasons.append(f"Takes full advantage of your generous {user_input.get('ram')} RAM for heavy multitasking.")
    else:
        score += 6.0

    # 2. Storage Evaluation (Max +/- 8 pts)
    if user_storage_gb < distro["min_storage_gb"]:
        score -= 25.0
    elif user_storage_gb >= distro["rec_storage_gb"]:
        score += 8.0
    else:
        score += 3.0

    # 3. CPU Tier Suitability (Max +/- 10 pts)
    is_low_cpu = "Older" in cpu or "Low-end" in cpu or "Atom" in cpu or "Celeron" in cpu
    is_arm = "ARM" in cpu or "Raspberry" in cpu
    is_high_cpu = "High-end" in cpu or "Ryzen 7" in cpu or "i7" in cpu

    if is_low_cpu:
        if distro["cpu_tier"] == "low" or distro["id"] in ["lubuntu", "puppy-linux", "linux-mint", "debian", "zorin-os"]:
            score += 14.0
            reasons.append(f"Lightweight architecture tailored for your {cpu.split('(')[0].strip()} processor.")
        else:
            score -= 12.0
    elif is_arm:
        if "ARM64" in distro.get("supported_arch", []):
            score += 10.0
            reasons.append(f"Official first-class ARM architecture images ready for your device.")
        else:
            score -= 20.0
    elif is_high_cpu:
        score += 8.0

    # 4. User Experience Alignment (Max +/- 25 pts)
    is_beginner = experience == "Beginner"
    is_intermediate = experience == "Intermediate"
    is_advanced = experience == "Advanced"

    if is_beginner:
        if distro["id"] in ["arch-linux"]:
            score -= 60.0  # Extreme penalty for beginner on pure Arch
        elif distro["id"] in ["kali-linux"]:
            score -= 50.0  # Extreme penalty for beginner daily driving Kali
        else:
            score += (distro["beginner_score"] * 2.2)
            if distro["beginner_score"] >= 9:
                reasons.append(f"World-class beginner friendliness with GUI installers, driver managers, and familiar menus.")
    elif is_intermediate:
        if distro["id"] in ["fedora", "pop-os", "manjaro", "opensuse-tumbleweed", "debian"]:
            score += 18.0
            reasons.append(f"Provides the perfect blend of modern flexibility and control for intermediate users.")
        elif distro["id"] in ["arch-linux", "kali-linux"]:
            score += 5.0
        else:
            score += 10.0
    elif is_advanced:
        if distro["id"] in ["arch-linux", "fedora", "debian", "opensuse-tumbleweed"]:
            score += 24.0
            reasons.append(f"Unrestricted power, upstream packages, and granular system customization for advanced users.")
        elif distro["id"] == "kali-linux" and purpose == "Security":
            score += 28.0
            reasons.append(f"Industry standard penetration testing suite with live injection and forensic tools.")
        else:
            score += 8.0

    # 5. Purpose Alignment (Max +/- 25 pts)
    distro_purposes = distro.get("primary_purposes", [])
    if purpose in distro_purposes:
        score += 20.0
        if purpose == "Gaming":
            if distro["id"] in ["pop-os", "manjaro", "fedora", "ubuntu"]:
                score += 8.0
                reasons.append(f"Optimized for gaming with out-of-the-box graphics drivers, Steam compatibility, and Wine/Proton.")
        elif purpose == "Programming":
            if distro["id"] in ["fedora", "ubuntu", "pop-os", "arch-linux", "debian"]:
                score += 8.0
                reasons.append(f"First-class developer ecosystem with instant access to compilers, Git, Docker, and IDEs.")
        elif purpose == "Office":
            reasons.append(f"Bundled with LibreOffice, PDF viewers, and dependable cloud storage / printer drivers.")
        elif purpose == "Education":
            reasons.append(f"Safe, reliable platform packed with educational apps, coding tutorials, and broad documentation.")
        elif purpose == "Security":
            if distro["id"] == "kali-linux":
                score += 15.0
            elif distro["id"] in ["debian", "ubuntu", "fedora"]:
                score += 10.0
                reasons.append(f"Solid security baseline with AppArmor/SELinux and safe sandbox containment.")
        elif purpose == "General use":
            reasons.append(f"Effortless daily web browsing, video streaming, email, and media playback.")
    else:
        score -= 8.0

    # 6. Preference Alignment (Max +/- 15 pts)
    pref_tags = distro.get("preference_tags", [])
    if preference in pref_tags:
        score += 14.0
        if preference == "Easy to use":
            reasons.append(f"Matches your '{preference}' preference with intuitive menus and zero required terminal usage.")
        elif preference == "Lightweight":
            reasons.append(f"Extremely fast and battery-friendly desktop environment that conserves RAM and CPU.")
        elif preference == "Customizable":
            reasons.append(f"Deep customization options allowing you to transform every pixel, shortcut, and theme.")
        elif preference == "Rock-solid stability" and ("Stable" in pref_tags):
            score += 6.0
            reasons.append(f"Battle-tested software repositories that will not break during critical tasks.")
        elif preference == "Cutting-edge" and ("Cutting-edge" in pref_tags):
            score += 6.0
            reasons.append(f"Fresh rolling kernel and the absolute latest application releases.")
    else:
        # Check partial tags
        if preference == "Rock-solid stability" and "Stable" in pref_tags:
            score += 12.0
            reasons.append(f"Proven stability with long-term security backports.")

    # 7. Previous Experience Fine-tuning
    if "None" in prev_exp and distro["id"] in ["linux-mint", "zorin-os", "ubuntu"]:
        score += 8.0
        reasons.append(f"Smooth on-ramp for first-time Linux adopters with no prior terminal experience needed.")
    elif "VM" in prev_exp and distro["id"] in ["fedora", "pop-os", "manjaro"]:
        score += 5.0
    elif "Daily driver" in prev_exp and distro["id"] in ["arch-linux", "fedora", "debian"]:
        score += 7.0

    # Deduplicate and ensure at least 3 compelling reasons
    unique_reasons = []
    for r in reasons:
        if r not in unique_reasons:
            unique_reasons.append(r)

    if len(unique_reasons) < 3:
        unique_reasons.append(f"Features the reliable {distro['desktop_environment']} desktop and {distro['package_manager']} package manager.")
        unique_reasons.append(f"Active global community with thousands of tutorials and helpful forum members.")

    return max(0.0, score), unique_reasons[:4]


def calculate_recommendation(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point: scores all distributions, calculates match percentages,
    selects top recommendation + 2 alternatives, and builds warnings if needed.
    """
    scored_distros = []
    for distro in DISTRIBUTIONS:
        score, reasons = evaluate_distro(distro, user_input)
        scored_distros.append({
            "distro": distro,
            "raw_score": score,
            "reasons": reasons
        })

    # Sort descending by raw score
    scored_distros.sort(key=lambda x: x["raw_score"], reverse=True)

    top_item = scored_distros[0]
    second_item = scored_distros[1] if len(scored_distros) > 1 else None
    third_item = scored_distros[2] if len(scored_distros) > 2 else None

    # Calculate calibrated match percentage (top match ranges from 88% - 99%)
    top_raw = top_item["raw_score"]
    # Reference max expected raw score ~ 125
    top_percent = min(99, max(84, int(round((top_raw / 125.0) * 100))))
    
    # Calculate relative percentages for alternatives
    second_percent = max(65, min(top_percent - 2, int(round((second_item["raw_score"] / top_raw) * top_percent)))) if second_item else 80
    third_percent = max(55, min(second_percent - 3, int(round((third_item["raw_score"] / top_raw) * top_percent)))) if third_item else 72

    # Special Security / Beginner warning
    advisory_warning = None
    user_purpose = user_input.get("purpose", "")
    user_exp = user_input.get("experience", "")
    if user_purpose == "Security" and user_exp == "Beginner":
        advisory_warning = (
            "Special Note on Cybersecurity: Kali Linux is designed specifically for licensed penetration testers "
            "and lacks safety nets for daily computer use. For beginners interested in security, we recommend starting "
            "with Linux Mint or Ubuntu to master the Linux terminal, then running Kali inside a virtual machine (VirtualBox)."
        )

    return {
        "best_match": {
            **top_item["distro"],
            "match_percentage": top_percent,
            "reasons": top_item["reasons"]
        },
        "alternatives": [
            {
                **second_item["distro"],
                "match_percentage": second_percent,
                "reasons": second_item["reasons"][:3]
            },
            {
                **third_item["distro"],
                "match_percentage": third_percent,
                "reasons": third_item["reasons"][:3]
            }
        ],
        "advisory_warning": advisory_warning,
        "user_profile": user_input
    }
