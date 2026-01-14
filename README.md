
# █▀▀ █░░ █ █▀█ ░ - █▀▀ ▄▀█ █▀▀ █░█ █▀▀
# █▄▄ █▄▄ █ █▀▀ ▄ - █▄▄ █▀█ █▄▄ █▀█ ██▄

> **Current Version:** v1.0.0 (Nuclear Capable)  
> **Status:** Deployment Ready  
> **Codename:** "Zero Memory"

---

## 💀 WHAT IS THIS?

**Clip-CACHE** isn't just another clipboard manager. It's a **Cyberpunk-infused, military-grade data retention system** built for power users who demand total control over their system's short-term memory. 

Most clipboard tools are ugly, bloated, or spy on you. We said "fuck that" and built something better.

We built this with a single philosophy: **Zero Memory**. Your computer should work for *you*, not the other way around. When you copy something, it should be there. When you want it gone, it should be **gone**. When you want to see what your system is actually doing, you should have the tools to tear it apart.

Use it to hoard code snippets, track image assets, manage files, or just look cool while doing standard boring office work.

---

## ⚡ KEY FEATURES

### 🧠 The Brain (Clipboard Core)
-   **Universal Capture**: Grabs Text, Images, and File Paths instantly.
-   **Smart Filtering**: Auto-sorts your chaos into `TEXT`, `IMG`, and `FILES` tabs.
-   **Persistence**: Uses a local SQLite database (stored safely in `%LOCALAPPDATA%`) so your history survives reboots.
-   **Infinite Scroll**: A custom-built kinetic scroller that feels like you're swiping through the void.

### 👻 Stealth & Incognito
-   **True Incognito Mode**: When you toggle this on, the app vanishes. No System Tray icon. No Taskbar entry. It's running, it's watching, but it's invisible until you summon it.
-   **Background Dominance**: Option to start silently with Windows. You won't even know it's there until you need it.
-   **Global Hotkey**: `CTRL + SHIFT + NUMPAD +`. Use it. It brings the app from the shadows to the foreground in ms.

### ☢️ NUCLEAR ADMIN TOOLS
This is where we separate the toys from the tools. Included is a suite of "God Mode" utilities:
-   **RAM Purge**: One click to scream at the OS to release working sets. We have a "Gentle" sweep and an "AGGRESSIVE" protocol that might make Windows cry (but frees up gigs of RAM).
-   **VRAM Reset**: A risky little button that attempts to flush GPU memory. Use with caution.
-   **IP Stack Reset**: Internet acting up? Nuke the DNS resolver and Winsock catalog directly from the UI.
-   **Process Killer**: A built-in Task Manager that doesn't ask for permission.

### 🎨 The Aesthetics
-   **50+ Themes**: From "Cyberpunk Neon" to "Deep Void Slate". We have a theme engine that changes *everything*—window borders, accents, scrollbars, text flow.
-   **Glassmorphism**: Real-time transparency and blur effects (if your GPU can handle it).
-   **Pulse Animation**: The window border breathes. It's alive.
-   **Sound Design**: (Coming soon, maybe. We like silence).

---

## 🛠️ INSTALLATION

You have two choices. The easy way, or the dev way.

### Option A: The Installer (Recommended)
1.  Download the latest `Clip-CACHE_Setup_v1.0.exe`.
2.  Run it.
3.  It puts the binary in `%APPDATA%`, sets up your shortcuts, and adds the registry keys for startup.
4.  **Updates**: If you instal it again later, it detects the old version and asks if you want to `REPAIR/UPDATE` or `UNINSTALL`. Smart.

### Option B: The Source (Python)
If you trust no one and want to run raw code:
```bash
git clone https://github.com/h4-tools/Clip-CACHE.git
cd Clip-CACHE
pip install -r requirements.txt
python src/main.py
```
*Note: You'll need Python 3.10+ and a decent appreciation for `PyQt6`.*

---

## 🎮 HOW TO USE

1.  **Launch It**: Double click the `(b'.')b` icon.
2.  **Copy Stuff**: Just use Windows normally (`Ctrl+C`). We catch it all.
3.  **Summon**: Hit `CTRL+SHIFT+NUMPAD +` or double-click the tray icon.
4.  **Pin It**: Found a snippet you use every day? Click **PIN ITEM**. It moves to the `PINNED` tab and stays there forever, effectively shielding it from the "Clear All" nuke.
5.  **Nuke It**: Click `DELETE` to remove one item, or use the **Admin Panel** to `TABULA RASA` (Wipe everything).

### The "God Mode" Toggle
Go to **Settings (☰)** -> **System Tab**.
Toggle **DEBUG / GOD MODE**.
Congratulations, you now have an extra `ADMIN` tab in the main window. Start breaking things.

---

## 📁 TECHNICAL SPECS

-   **Language**: Python 3.11
-   **GUI Framework**: PyQt6 (Heavily modified with QSS)
-   **Database**: SQLite3
-   **Monitoring**: `psutil` & `win32api`
-   **Build System**: PyInstaller + Inno Setup 6

### File Structure
We keep it clean. No spaghetti code here (mostly).
```
/src
  /core       # The Brain (DB, Monitor, Logger)
  /ui         # The Face (Windows, Widgets, Styles)
  /assets     # The Soul (Icons, EULA, Privacy)
  main.py     # The Heartbeat
```

---

## 🕊️ PHILOSOPHY: "Zero Memory"

We believe software should be ephemeral unless told otherwise. 
Clip-CACHE uses a **FIFO** (First-In-First-Out) buffer for general history. Once you hit 100 items, the oldest one gets pushed into the void. This keeps your database small and the app fast.

We don't cloud sync. We don't phone home. Your clipboard is *your* business. The only logs we keep are crash reports on your Desktop because we're not psychics and sometimes bugs happen when you laucnh weird shit.

---

## ⚖️ LEGAL & DISCLAIMER

**This tool is powerful.** Using the "Aggressive RAM Clean" or "VRAM Reset" carries non-zero risks of crashing other apps. We aren't responsible if you lose your unsaved Word doc because you decided to nuke system memory while typing a thesis.

**Privacy**: We capture your clipboard. It's stored LOCALLY on your drive. If you copy a password, it's in the DB. If you're paranoid, hit the **"PURGE MEMORY"** button before you close the app.

---

### (b'.')b - h4 - {Be Your Best}
*Built with caffeine, hate, and Python.*
