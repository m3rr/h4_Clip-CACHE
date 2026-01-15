
# █▀▀ █░░ █ █▀█ ░ - █▀▀ ▄▀█ █▀▀ █░█ █▀▀
# █▄▄ █▄▄ █ █▀▀ ▄ - █▄▄ █▀█ █▄▄ █▀█ ██▄

> **Current Version:** v2.0.0 (Vault Edition)  
> **Status:** Deployment Ready  
> **Codename:** "Zero Memory" (With Exceptions)

## ⚠️ LICENSE WARNING
**This is NOT Free Open Source Software.**
This code is **Source-Available**. You can look, learn, and use it personally.
If you use this code to make money, you owe the author (h4) **50% of gross revenue**.
See [LICENSE.md](./LICENSE.md) for details.

---

## 💀 WHAT IS THIS?

**Clip-CACHE** isn't just another clipboard manager. It's a **Cyberpunk-infused, military-grade data retention system** built for power users who demand total control over their system's short-term memory. 

Most clipboard tools are ugly, bloated, or spy on you. We said "fuck that" and built something better.

We built this with a single philosophy: **Zero Memory**. Your computer should work for *you*, not the other way around. 

*   When you copy something, it should be there. 
*   When you want it gone, it should be **gone**. 
*   When you want it kept forever, it should be **Vaulted**.

Use it to hoard code snippets, track image assets, manage files, or just look cool while doing standard boring office work.

---

## ⚡ KEY FEATURES

### 🔒 The Vault (Physical Pinning)
**New in v2.0**: Pinning an item doesn't just "flag" it. It physically copies the data (Text, Image, or **Entire File**) into a secure `%LOCALAPPDATA%` vault.
*   **Deletion Safe**: If you pin a file and delete the original, the pinned item **still works**. It draws from the Vault.
*   **Auto-Sync**: Previews, Launches, and Copy operations automatically prioritize the Vault copy.
*   **Destructive Unpin**: Unpinning is a destructive action. It wipes the Vault copy. We warn you first.

### 🧠 The Brain (Clipboard Core)
-   **Universal Capture**: Grabs Text, Images, and File Paths instantly.
-   **Smart Filtering**: Auto-sorts your chaos into `TEXT`, `IMG`, and `FILES` tabs.
-   **Persistence**: Uses a local SQLite database history survives reboots.
-   **Infinite Scroll**: A custom-built kinetic scroller that feels like you're swiping through the void.

### 👻 Stealth & Incognito
-   **True Incognito Mode**: Use it to vanish. No System Tray icon. No Taskbar entry.
-   **Background Dominance**: Start silently with Windows.
-   **Global Hotkey**: `CTRL + SHIFT + NUMPAD +`. Summon the void instantly.

### ☢️ NUCLEAR ADMIN TOOLS
-   **RAM Purge**: "Gentle" sweep and "AGGRESSIVE" protocol.
-   **VRAM Reset**: Flush GPU memory.
-   **IP Stack Reset**: Nuke the DNS resolver.
-   **Process Killer**: A built-in Task Manager.

### 🎨 The Aesthetics
-   **50+ Themes**: From "Cyberpunk Neon" to "Deep Void Slate".
-   **Glassmorphism**: Real-time transparency and blur effects.
-   **Pulse Animation**: The window border breathes.

---

## 🛠️ INSTALLATION

### Option A: The Installer (Smart v2.0)
1.  **Compile It**: Run `iscc setup_script.iss` (Requires Inno Setup).
2.  **Run It**: `Clip-CACHE_Setup_v2.0.exe`.
3.  **Smart Logic**:
    *   **Auto-Detect**: Finds existing installs.
    *   **Options**: Offers to `REMOVE` (Uninstall) or `MODIFY/REPAIR` (Update) automatically.
    *   **Single Instance**: Prevents multiple installers or apps from running at once.

### Option B: The Source (Python)
If you trust no one and want to run raw code:
```bash
git clone https://github.com/h4-tools/Clip-CACHE.git
cd Clip-CACHE
pip install -r requirements.txt
python ClipCache_Launcher.py
```

---

## 🎮 HOW TO USE

1.  **Launch It**: Double click the `(b'.')b` icon.
2.  **Summon**: Hit `CTRL+SHIFT+NUMPAD +` or double-click the tray icon.
3.  **Pin (Vault)**: Click **PIN ITEM**. This creates a physical copy in the Vault.
    *   *Pro Tip*: You can now safely delete the original source file. The Vault has you covered.
4.  **Unpin**: Click **UNPIN ITEM**. Warning: This destroys the Vault copy.

### The "God Mode" Toggle
Go to **Settings (☰)** -> **System Tab** -> Toggle **DEBUG / GOD MODE**.

---

## 📁 TECHNICAL SPECS

-   **Version**: 2.0.0
-   **Language**: Python 3.11
-   **GUI Framework**: PyQt6 (Heavily modified with QSS)
-   **Database**: SQLite3
-   **Storage**: `%LOCALAPPDATA%\h4\Clip-CACHE\vault\`

### File Structure
```
/src
  /core       # The Brain (Vault, DB, Monitor)
  /ui         # The Face (Windows, Widgets)
  /assets     # The Soul (Icons, EULA)
  ClipCache_Launcher.py # The Key
```

---

## 🕊️ PHILOSOPHY: "Zero Memory" (Revised)

We believe software should be ephemeral unless told otherwise. 
Clip-CACHE uses a **FIFO** buffer. Old shit dies.
**EXCEPTION**: The Vault. What you Pin, you Keep. Physically. Forever (until you unpin).

---

## ⚖️ LEGAL & DISCLAIMER

**This tool is powerful.** Using "Aggressive RAM Clean" carries risks.
**Privacy**: We capture your clipboard. It's stored LOCALLY. We don't see it.
**Single Instance**: The app enforces a Highlander rule ("There can be only one").

---

### (b'.')b - h4 - {Be Your Best}
*Built with caffeine, hate, and Python.*
