# 🪔 DIWALI • Festival of Light

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![Library](https://img.shields.io/badge/pygame-2.0%2B-brightgreen.svg)
![Assets](https://img.shields.io/badge/assets-100%25%20procedural-orange.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

An interactive, procedurally generated Diwali celebration animation built entirely in Python using `pygame`. 

Every visual element—from the flickering clay *diyas* and intricate floor *rangoli* to the floating sky lanterns and multi-pattern fireworks—is calculated and rendered dynamically through code. **No external images, fonts, or audio downloads are required.**

---

## 📖 Table of Contents

1. [Overview & Highlights](#-overview--highlights)
2. [Visual & Technical Architecture](#-visual--technical-architecture)
3. [Prerequisites & Installation](#-prerequisites--installation)
4. [Running the Application](#-running-the-application)
5. [Command-Line Arguments](#-command-line-arguments)
6. [Interactive Controls](#-interactive-controls)
7. [Scene Timeline (Cinematic Intro)](#-scene-timeline-cinematic-intro)
8. [Web Deployment (Pygame to Browser)](#-web-deployment-pygame-to-browser)
9. [Project Structure](#-project-structure)
10. [Troubleshooting](#-troubleshooting)
11. [License](#-license)

---

## ✨ Overview & Highlights

* **Zero External Dependencies (Asset-Free):** Everything is drawn mathematically using polygons, parametric curves, ellipses, and custom surface blitting.
* **Custom Additive Lighting Engine:** Implements radial light falloff surfaces cached in memory and blended onto a dedicated lighting layer via `pygame.BLEND_RGB_ADD`.
* **Physics-Based Firework System:** Features four distinct firework explosion patterns (**Peony**, **Ring**, **Willow**, and parametric **Heart**) with air drag, gravity, and glowing spark trails.
* **Cinematic Staggered Reveal:** Uses smoothstep easing (`3t² - 2t³`) to gradually fade in 9 distinct scene layers over the first 7 seconds.
* **Personalized Greetings:** Pass any name via the command line to render a custom `"With love, <Name>"` signature right into the centerpiece.
* **Responsive Scaling:** Automatically scales the native `1280x800` canvas to fit any window size or fullscreen monitor while preserving the aspect ratio with clean letterboxing.
* **Built-In Snapshot Utility:** Press a single key (`S`) to save a lossless, timestamped `.png` render of the current canvas into a local `diwali_snapshots/` folder.

---

## 🎨 Visual & Technical Architecture

### 1. Background & Skyline
* Renders a vertical night-sky gradient transitioning from deep midnight blue `(5, 8, 27)` to warm twilight violet `(32, 12, 43)`.
* Generates a deterministic procedural city skyline (using a fixed seed `random.Random(41)`) complete with pitched roofs, lit windows, and an ornate golden border frame.

### 2. Procedural Rangoli Mandala
* Pre-renders a `440x440` symmetrical mandala using polar coordinates and sinusoidal petal curves across 5 concentric rings, then perspective-scales it (`0.43` vertical ratio) onto the floor with a subtle breathing animation.

### 3. Flickering Clay Diyas
* Drawn across the foreground with multi-layered flames (outer orange, mid gold, inner white-hot core).
* Flames sway and flicker organically by combining dual-frequency sine waves (`9 rad/s` and `17 rad/s`).

### 4. Sky Lanterns & Festive String Lights
* **String Lights:** 4 catenary-style hanging light segments across the top border that pulse rhythmically across a 6-color festive palette.
* **Sky Lanterns:** 12 glowing paper lanterns that drift upward continuously while oscillating horizontally.

---

## 🛠 Prerequisites & Installation

### System Requirements
* **Python:** `3.7` or higher (`3.9+` recommended)
* **OS:** Windows, macOS, or Linux

### Step 1: Clone or Download
Save the Python script as `diwali_animation_ultimate.py` in your working directory.

### Step 2: Install Pygame
Open your terminal or command prompt and install `pygame`:

```bash
python -m pip install pygame
```
*(Note: On some Linux/macOS setups, you may need to use `python3 -m pip install pygame`)*

---

## 🚀 Running the Application

### Standard Launch
Run the script with default settings (High quality, generic greeting):

```bash
python diwali_animation_ultimate.py
```

### Personalized Greeting Launch
Add your name (or a recipient's name) to customize the centerpiece text:

```bash
python diwali_animation_ultimate.py --name "Aarav & Family"
```

### Low-Spec / Battery-Saver Launch
If running on integrated graphics or older hardware, use the `low` quality preset to reduce the particle cap and disable secondary spark glow passes:

```bash
python diwali_animation_ultimate.py --name "Your Name" --quality low
```

---

## ⚙️ Command-Line Arguments

| Argument | Type / Choices | Default | Description |
| :--- | :--- | :--- | :--- |
| `--name` | `str` *(max 42 chars)* | `""` | Replaces the default subtitle with `With love, <Name>` in gold serif typography. |
| `--quality` | `high` \| `low` | `high` | **`high`**: 1,800 max particles, 95 sparks/explosion, particle glow enabled.<br>**`low`**: 700 max particles, 48 sparks/explosion, particle glow disabled. |
| `-h`, `--help` | Flag | N/A | Displays the help message and exits. |

---

## 🎮 Interactive Controls

Once the window is open, you can control the show in real time using your mouse and keyboard:

| Key / Input | Function | Details |
| :--- | :--- | :--- |
| **Left Mouse Click** | **Spawn Firework** | Immediately detonates a random firework (`peony`, `ring`, `willow`, or `heart`) at the exact cursor coordinates. |
| **`SPACE`** | **Grand Finale** | Launches 3 immediate rockets and triggers a 5-second high-frequency firework barrage. |
| **`P`** | **Pause / Resume** | Freezes all physics, timers, and animations (`PAUSED` indicator appears at the top). |
| **`A`** | **Toggle Autoplay** | Turns automatic background rocket launches on or off. |
| **`F`** | **Toggle Fullscreen** | Switches seamlessly between Fullscreen mode and Resizable Windowed mode. |
| **`S`** | **Take Snapshot** | Saves the current `1280x800` scene to `./diwali_snapshots/diwali_YYYYMMDD_HHMMSS_xxxxxx.png`. |
| **`H`** | **Toggle HUD Help** | Hides or reveals the bottom control bar for clean screen recordings or screenshots. |
| **`ESC`** | **Exit** | Cleanly closes the Pygame window and terminates the program. |

---

## 🎬 Scene Timeline (Cinematic Intro)

When the script starts, the animation builds up gradually using an eased timeline:

| Time (Seconds) | Layer Revealed | Description |
| :---: | :--- | :--- |
| `0.0s` | **Background** | Night sky gradient, city silhouette, and golden frame appear. |
| `0.2s – 2.0s` | **Stars** | 125 twinkling stars fade into the upper sky. |
| `1.3s – 3.0s` | **Festive Lights** | Hanging string lights illuminate along the top border. |
| `2.5s – 4.3s` | **Sky Lanterns** | Warm floating lanterns begin drifting upward. |
| `3.4s – 5.2s` | **Floor Rangoli** | The centerpiece geometric mandala fades in on the ground. |
| `4.0s – 6.0s` | **Clay Diyas** | 7 flickering oil lamps ignite across the foreground. |
| `4.7s – 6.0s` | **Header Text** | `"T H E   F E S T I V A L   O F   L I G H T S"` appears. |
| `5.0s – 6.8s` | **Fireworks** | Automated firework rockets begin launching into the sky. |
| `5.4s – 7.1s` | **Main Title** | `"Happy Diwali"` title renders with a golden shimmer. |
| `6.2s – 7.
