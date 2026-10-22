"""
Comprehensive Linux Distribution Knowledge Base.
Contains detailed hardware requirements, target user levels, purpose strengths,
desktop environments, package managers, and nuanced pros/cons.
"""

DISTRIBUTIONS = [
    {
        "id": "linux-mint",
        "name": "Linux Mint",
        "tagline": "From freedom came elegance - the gold standard for Windows switchers",
        "family": "Ubuntu / Debian",
        "min_ram_gb": 2.0,
        "rec_ram_gb": 4.0,
        "min_storage_gb": 20,
        "rec_storage_gb": 50,
        "cpu_tier": "low", # low, mid, high
        "supported_arch": ["x86_64"],
        "target_experience": ["Beginner", "Intermediate"],
        "primary_purposes": ["General use", "Office", "Programming", "Education"],
        "preference_tags": ["Easy to use", "Lightweight", "Stable"],
        "desktop_environment": "Cinnamon (also MATE, XFCE)",
        "package_manager": "APT / Flatpak",
        "release_model": "Fixed (LTS-based, 6-month updates)",
        "beginner_score": 10,
        "pros": [
            "Familiar Windows-like interface with Cinnamon desktop",
            "Out-of-the-box multimedia codecs and driver manager",
            "Extremely stable base (Ubuntu LTS) without forced Snaps",
            "Gentle learning curve with high community support"
        ],
        "cons": [
            "Not rolling-release (newer software packages take longer)",
            "Visual styling feels slightly traditional/conservative to some",
            "No official Wayland support as default yet (in progress)"
        ],
        "website": "https://linuxmint.com",
        "docs_url": "https://linuxmint.com/documentation.php",
        "accent_color": "#87cf3e",
        "badge": "Top Pick for Beginners"
    },
    {
        "id": "ubuntu",
        "name": "Ubuntu",
        "tagline": "The world's most popular desktop Linux and cloud enterprise OS",
        "family": "Debian",
        "min_ram_gb": 4.0,
        "rec_ram_gb": 8.0,
        "min_storage_gb": 25,
        "rec_storage_gb": 60,
        "cpu_tier": "mid",
        "supported_arch": ["x86_64", "ARM64"],
        "target_experience": ["Beginner", "Intermediate", "Advanced"],
        "primary_purposes": ["Programming", "General use", "Office", "Education", "Gaming"],
        "preference_tags": ["Easy to use", "Stable"],
        "desktop_environment": "GNOME customized",
        "package_manager": "APT / Snap",
        "release_model": "Fixed (LTS every 2 years, regular every 6 months)",
        "beginner_score": 9,
        "pros": [
            "Huge global ecosystem; virtually every Linux tutorial works on Ubuntu",
            "Extensive commercial support and third-party software availability (Docker, Steam, VS Code)",
            "Predictable 5-year Long Term Support (LTS) lifecycle",
            "Strong multi-architecture support including Raspberry Pi & servers"
        ],
        "cons": [
            "Snap package store can have slower launch times for some desktop apps",
            "GNOME shell requires at least 4GB RAM to feel truly responsive",
            "Canonical telemetry enabled by default (opt-out available)"
        ],
        "website": "https://ubuntu.com",
        "docs_url": "https://help.ubuntu.com",
        "accent_color": "#E95420",
        "badge": "Most Popular & Widely Documented"
    },
    {
        "id": "zorin-os",
        "name": "Zorin OS",
        "tagline": "The ultimate bridge from Windows and macOS with stunning aesthetics",
        "family": "Ubuntu / Debian",
        "min_ram_gb": 2.0,
        "rec_ram_gb": 4.0,
        "min_storage_gb": 20,
        "rec_storage_gb": 40,
        "cpu_tier": "low",
        "supported_arch": ["x86_64"],
        "target_experience": ["Beginner"],
        "primary_purposes": ["General use", "Office", "Education"],
        "preference_tags": ["Easy to use", "Lightweight"],
        "desktop_environment": "Zorin Desktop (Custom GNOME / XFCE for Lite)",
        "package_manager": "APT / Flatpak / Snap",
        "release_model": "Fixed (LTS-based)",
        "beginner_score": 10,
        "pros": [
            "Zorin Appearance tool mimics Windows 11, Windows 7, or macOS in 1 click",
            "Built-in Windows App Support (WINE helper) detects .exe installers and suggests alternatives",
            "Zorin OS Lite edition revives older laptops with low specs",
            "Polished, modern typography and eye-candy interface"
        ],
        "cons": [
            "Pro edition with extra layouts costs money (Core and Lite are free)",
            "Slightly smaller dedicated forum community compared to pure Ubuntu",
            "Release cycle is tied to older Ubuntu LTS bases"
        ],
        "website": "https://zorin.com/os",
        "docs_url": "https://help.zorin.com",
        "accent_color": "#15A6F0",
        "badge": "Easiest Transition from Windows/Mac"
    },
    {
        "id": "pop-os",
        "name": "Pop!_OS",
        "tagline": "Engineered for STEM, gaming, developers, and creators by System76",
        "family": "Ubuntu",
        "min_ram_gb": 4.0,
        "rec_ram_gb": 8.0,
        "min_storage_gb": 20,
        "rec_storage_gb": 60,
        "cpu_tier": "mid",
        "supported_arch": ["x86_64", "ARM64"],
        "target_experience": ["Beginner", "Intermediate", "Advanced"],
        "primary_purposes": ["Gaming", "Programming", "General use"],
        "preference_tags": ["Easy to use", "Customizable"],
        "desktop_environment": "COSMIC (Rust-based) / GNOME",
        "package_manager": "APT / Flatpak",
        "release_model": "Semi-rolling / LTS",
        "beginner_score": 9,
        "pros": [
            "Dedicated ISO with proprietary NVIDIA graphics drivers pre-installed",
            "Built-in automatic window tiling and keyboard-driven workflow",
            "Pop!_Shop prioritizes Flatpaks instead of forced Canonical Snaps",
            "Full disk encryption enabled out-of-the-box by default"
        ],
        "cons": [
            "Requires at least 4GB RAM and a decent 64-bit CPU",
            "COSMIC desktop redesign transition currently underway",
            "Default installer uses systemd-boot instead of familiar GRUB"
        ],
        "website": "https://system76.com/pop",
        "docs_url": "https://support.system76.com",
        "accent_color": "#48B9C7",
        "badge": "Best for Gamers & Developers"
    },
    {
        "id": "fedora",
        "name": "Fedora Workstation",
        "tagline": "Leading-edge innovation, pure open source, and the upstream heart of Red Hat",
        "family": "Red Hat / Fedora",
        "min_ram_gb": 4.0,
        "rec_ram_gb": 8.0,
        "min_storage_gb": 20,
        "rec_storage_gb": 60,
        "cpu_tier": "mid",
        "supported_arch": ["x86_64", "ARM64"],
        "target_experience": ["Intermediate", "Advanced"],
        "primary_purposes": ["Programming", "General use", "Education", "Gaming"],
        "preference_tags": ["Cutting-edge", "Customizable"],
        "desktop_environment": "Pure GNOME (Wayland native)",
        "package_manager": "DNF / RPM / Flatpak",
        "release_model": "Fixed Rapid (New release every 6 months, supported 13 months)",
        "beginner_score": 7,
        "pros": [
            "First to receive modern Linux innovations (Wayland, PipeWire, systemd, btrfs)",
            "Pure, untainted upstream GNOME experience exactly as intended",
            "Outstanding developer tooling, container integration (Podman), and Linus Torvalds' distro of choice",
            "Backed by Red Hat / IBM enterprise engineering standards"
        ],
        "cons": [
            "Strict open-source stance requires enabling RPM Fusion for proprietary codecs/drivers",
            "Frequent kernel updates can occasionally trip third-party Wi-Fi/NVIDIA modules",
            "Short 13-month release lifecycle requires regular version upgrades"
        ],
        "website": "https://fedoraproject.org",
        "docs_url": "https://docs.fedoraproject.org",
        "accent_color": "#294172",
        "badge": "Best for Modern Developers"
    },
    {
        "id": "debian",
        "name": "Debian",
        "tagline": "The Universal Operating System - legendary stability and reliability",
        "family": "Debian (Independent Parent)",
        "min_ram_gb": 2.0,
        "rec_ram_gb": 4.0,
        "min_storage_gb": 15,
        "rec_storage_gb": 40,
        "cpu_tier": "low",
        "supported_arch": ["x86_64", "i386", "ARM64", "armhf", "RISC-V"],
        "target_experience": ["Intermediate", "Advanced"],
        "primary_purposes": ["Programming", "Education", "Office", "Security"],
        "preference_tags": ["Stable", "Lightweight", "Customizable"],
        "desktop_environment": "Choice during install (GNOME, XFCE, KDE, MATE, LXQt)",
        "package_manager": "APT",
        "release_model": "Fixed (Rock-solid ~2 year stable cycles)",
        "beginner_score": 6,
        "pros": [
            "Unrivaled reliability - runs on servers, international space station, and subsea cables",
            "Huge software repository with over 59,000 packages",
            "Very light on system resources; minimal background overhead",
            "Supports almost every CPU architecture ever made"
        ],
        "cons": [
            "Software packages are often older (prioritizes stability over latest features)",
            "Installer is slightly more technical than Ubuntu/Mint",
            "Requires basic terminal knowledge for non-free firmware post-install troubleshooting"
        ],
        "website": "https://www.debian.org",
        "docs_url": "https://www.debian.org/doc",
        "accent_color": "#A80030",
        "badge": "Unbeatable Rock-Solid Stability"
    },
    {
        "id": "lubuntu",
        "name": "Lubuntu",
        "tagline": "Fast and lightweight operating system designed to revive older machines",
        "family": "Ubuntu / Debian",
        "min_ram_gb": 1.0,
        "rec_ram_gb": 2.0,
        "min_storage_gb": 10,
        "rec_storage_gb": 25,
        "cpu_tier": "low",
        "supported_arch": ["x86_64"],
        "target_experience": ["Beginner", "Intermediate"],
        "primary_purposes": ["General use", "Office", "Education"],
        "preference_tags": ["Lightweight", "Easy to use"],
        "desktop_environment": "LXQt",
        "package_manager": "APT / Snap",
        "release_model": "Fixed (LTS-based)",
        "beginner_score": 8,
        "pros": [
            "Runs fluidly on older PCs and laptops with only 1GB to 2GB of RAM",
            "Retains full Ubuntu repository and software compatibility",
            "Clean, uncluttered LXQt desktop that doesn't waste CPU cycles",
            "Low energy consumption preserves laptop battery life"
        ],
        "cons": [
            "Basic visual aesthetics out of the box (minimal blur or eye-candy)",
            "Fewer flashy desktop animations or pre-installed widgets",
            "Default text editors and system tools are minimalistic"
        ],
        "website": "https://lubuntu.me",
        "docs_url": "https://manual.lubuntu.me",
        "accent_color": "#0068C6",
        "badge": "Best for Low-End & Older Hardware"
    },
    {
        "id": "manjaro",
        "name": "Manjaro Linux",
        "tagline": "The power and currency of Arch Linux made accessible for everyone",
        "family": "Arch",
        "min_ram_gb": 4.0,
        "rec_ram_gb": 8.0,
        "min_storage_gb": 30,
        "rec_storage_gb": 60,
        "cpu_tier": "mid",
        "supported_arch": ["x86_64", "ARM64"],
        "target_experience": ["Intermediate", "Advanced"],
        "primary_purposes": ["Gaming", "Programming", "General use"],
        "preference_tags": ["Cutting-edge", "Customizable"],
        "desktop_environment": "XFCE, KDE Plasma, or GNOME",
        "package_manager": "Pamac / Pacman / AUR / Flatpak",
        "release_model": "Rolling Release (Curated)",
        "beginner_score": 7,
        "pros": [
            "Access to the vast Arch User Repository (AUR) with simple GUI installer (Pamac)",
            "Automated hardware detection and easy kernel switching utility",
            "Always up-to-date graphics drivers, kernels, and Steam Proton compatibility",
            "Rolling release means you install once and never reinstall for upgrades"
        ],
        "cons": [
            "Rolling updates can occasionally require terminal intervention after major updates",
            "Holds Arch packages back by 1-2 weeks, which can cause minor AUR sync mismatches",
            "Requires user comfort reading update announcements"
        ],
        "website": "https://manjaro.org",
        "docs_url": "https://wiki.manjaro.org",
        "accent_color": "#35BF5C",
        "badge": "User-Friendly Rolling Release"
    },
    {
        "id": "arch-linux",
        "name": "Arch Linux",
        "tagline": "A lightweight and flexible Linux distribution that tries to Keep It Simple",
        "family": "Arch (Independent)",
        "min_ram_gb": 2.0,
        "rec_ram_gb": 8.0,
        "min_storage_gb": 20,
        "rec_storage_gb": 60,
        "cpu_tier": "low",
        "supported_arch": ["x86_64"],
        "target_experience": ["Advanced"],
        "primary_purposes": ["Programming", "Gaming", "General use"],
        "preference_tags": ["Customizable", "Cutting-edge", "Lightweight"],
        "desktop_environment": "User-configured (KDE, GNOME, Hyprland, i3)",
        "package_manager": "Pacman / AUR",
        "release_model": "Pure Rolling Release",
        "beginner_score": 2,
        "pros": [
            "Total control: You choose every single package and service installed",
            "The Arch Wiki is the most comprehensive Linux documentation on Earth",
            "Bleeding-edge software updates within hours of upstream release",
            "Zero bloatware - your machine runs only what you explicitly ordered"
        ],
        "cons": [
            "NOT recommended for beginners - text-based installation requires command line competence",
            "No graphical installer or default desktop provided without manual setup (or archinstall script)",
            "You are the system administrator: you must troubleshoot your own issues"
        ],
        "website": "https://archlinux.org",
        "docs_url": "https://wiki.archlinux.org",
        "accent_color": "#1793D1",
        "badge": "For Power Users & DIY Enthusiasts"
    },
    {
        "id": "kali-linux",
        "name": "Kali Linux",
        "tagline": "The premier advanced penetration testing and ethical hacking platform",
        "family": "Debian",
        "min_ram_gb": 4.0,
        "rec_ram_gb": 8.0,
        "min_storage_gb": 30,
        "rec_storage_gb": 80,
        "cpu_tier": "mid",
        "supported_arch": ["x86_64", "ARM64"],
        "target_experience": ["Advanced", "Intermediate"],
        "primary_purposes": ["Security"],
        "preference_tags": ["Customizable"],
        "desktop_environment": "XFCE (default), GNOME, KDE",
        "package_manager": "APT",
        "release_model": "Rolling (Debian Testing-based)",
        "beginner_score": 3,
        "pros": [
            "Comes with over 600 pre-installed tools for penetration testing and forensic analysis",
            "Maintained by cybersecurity company Offensive Security",
            "Specialized kernel patches for Wi-Fi packet injection and hardware wireless dongles",
            "Live USB persistence with encrypted LUKS nuke capability"
        ],
        "cons": [
            "NOT intended as a daily driver OS for homework, gaming, or general office use",
            "Security tools can conflict with standard desktop productivity workflows",
            "Beginners are prone to misconfiguring tools or triggering network security alerts",
            "Requires understanding of networking, protocols, and Linux CLI"
        ],
        "website": "https://www.kali.org",
        "docs_url": "https://www.kali.org/docs",
        "accent_color": "#557C93",
        "badge": "Specialized Cybersecurity Platform"
    },
    {
        "id": "opensuse-tumbleweed",
        "name": "openSUSE Tumbleweed",
        "tagline": "The automated quality-tested rolling release with enterprise-grade YaST tools",
        "family": "openSUSE (Independent)",
        "min_ram_gb": 4.0,
        "rec_ram_gb": 8.0,
        "min_storage_gb": 25,
        "rec_storage_gb": 60,
        "cpu_tier": "mid",
        "supported_arch": ["x86_64", "ARM64"],
        "target_experience": ["Intermediate", "Advanced"],
        "primary_purposes": ["Programming", "General use", "Office"],
        "preference_tags": ["Stable", "Cutting-edge", "Customizable"],
        "desktop_environment": "KDE Plasma (First-class), GNOME, XFCE",
        "package_manager": "Zypper / YaST / RPM / Flatpak",
        "release_model": "Rolling (with openQA automated test gates)",
        "beginner_score": 7,
        "pros": [
            "Automated openQA testing guarantees packages don't break before release",
            "YaST Control Center provides comprehensive GUI management of the entire OS",
            "Btrfs snapshots with Snapper let you roll back updates instantly from the boot menu if something goes wrong",
            "First-class KDE Plasma integration and German enterprise engineering"
        ],
        "cons": [
            "Smaller desktop user base in North America compared to Ubuntu/Fedora",
            "Zypper package manager is slightly slower than DNF or Pacman",
            "Software installation via Open Build Service (OBS) has a minor learning curve"
        ],
        "website": "https://www.opensuse.org",
        "docs_url": "https://doc.opensuse.org",
        "accent_color": "#73BA25",
        "badge": "Safest Rolling Release with Snapshots"
    },
    {
        "id": "puppy-linux",
        "name": "Puppy Linux",
        "tagline": "Ultra-lightweight Linux that loads completely into your computer RAM",
        "family": "Independent / Ubuntu-compatible",
        "min_ram_gb": 0.5,
        "rec_ram_gb": 1.0,
        "min_storage_gb": 5,
        "rec_storage_gb": 15,
        "cpu_tier": "low",
        "supported_arch": ["x86_64", "i386"],
        "target_experience": ["Beginner", "Intermediate"],
        "primary_purposes": ["General use", "Education"],
        "preference_tags": ["Lightweight", "Easy to use"],
        "desktop_environment": "JWM (Joe's Window Manager) / ROX",
        "package_manager": "Puppy Package Manager (PPM)",
        "release_model": "Fixed",
        "beginner_score": 6,
        "pros": [
            "Runs entirely in RAM, making it blisteringly fast even on 15-year-old laptops",
            "ISO size is under 600MB; boots easily from tiny USB flash drives",
            "Great for data recovery and reviving legacy family computers",
            "Does not alter existing hard drive without explicit confirmation"
        ],
        "cons": [
            "Quirky desktop conventions and dated graphical appearance",
            "Historically ran as root user by default (modern versions improved this)",
            "Not suited for heavy modern multi-tasking or modern gaming"
        ],
        "website": "https://puppylinux-woof-ce.github.io",
        "docs_url": "https://wikka.puppylinux.com",
        "accent_color": "#4A708B",
        "badge": "Ultra-Light Rescue & Legacy Revival"
    },
    {
        "id": "endeavouros",
        "name": "EndeavourOS",
        "tagline": "A terminal-centric, friendly Arch-based distro with a vibrant community",
        "family": "Arch",
        "min_ram_gb": 4.0,
        "rec_ram_gb": 8.0,
        "min_storage_gb": 20,
        "rec_storage_gb": 50,
        "cpu_tier": "mid",
        "supported_arch": ["x86_64", "ARM64"],
        "target_experience": ["Intermediate", "Advanced"],
        "primary_purposes": ["Programming", "Gaming", "General use"],
        "preference_tags": ["Cutting-edge", "Customizable"],
        "desktop_environment": "XFCE (default), KDE Plasma, GNOME, etc.",
        "package_manager": "Pacman / yay (AUR)",
        "release_model": "Rolling Release",
        "beginner_score": 5,
        "pros": [
            "Easy Calamares graphical installer for an authentic Arch Linux foundation",
            "Direct access to the Arch User Repository (AUR) with pre-configured yay helper",
            "Welcoming, active, and patient community forum that helps new Arch users",
            "Minimalist install with no unnecessary bloatware"
        ],
        "cons": [
            "Terminal-centric approach expects user to read and use terminal for maintenance",
            "Bleeding-edge rolling updates occasionally require manual pacman intervention",
            "Not suited for complete beginners who want a plug-and-play GUI system"
        ],
        "website": "https://endeavouros.com",
        "docs_url": "https://discovery.endeavouros.com",
        "accent_color": "#7B3F9A",
        "badge": "Best Friendly Gateway to Arch Linux"
    }
]

def get_all_distros():
    """Return all distro dictionaries."""
    return DISTRIBUTIONS

def get_distro_by_id(distro_id):
    """Find a distro by its unique string id."""
    for d in DISTRIBUTIONS:
        if d["id"] == distro_id:
            return d
    return None
