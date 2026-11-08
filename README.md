# ★ DAKSH BATTLE ★
**PLAY • FIGHT • SURVIVE**

A complete, high-octane 3D battle-royale game inspired by the overall gameplay atmosphere and lobby experience of **Free Fire**. Built with original artwork, characters, ballistics, audio, and branding.

Runs seamlessly on:
1. **Web & Mobile Browsers** (FastAPI / Uvicorn Backend + Three.js 3D WebGL Client + Touch Controls)
2. **Windows Desktop** (Python 3.15 + Pyglet + PyOpenGL)

---

## 🎮 Dual-Platform Architecture

| Platform | Engine / Framework | Key Features |
|---|---|---|
| **Mobile & Web Browser** | Python FastAPI / Uvicorn + Three.js WebGL | Realistic anatomical humanoid 3D character rigs, joint-based skeletal animations (idle, walk, run, jump, landing, crouch, reload, weapon holding, victory, defeat, emotes), 3D obstacle collision detection against watchtowers/bunkers/buildings/containers, virtual touch joystick, touch look swipe, touch buttons, Web Audio API sound synthesis, responsive landscape mobile layout. |
| **Windows Desktop** | Python 3.15, Pyglet 2.1, PyOpenGL 2.1 | Fullscreen/Windowed 3D battle arena, OpenGL 2.1 compatibility context, 32 art assets, mouse look, WASD, dynamic FPS scaling, full keyboard controls. |

---

## 🚀 How to Run Locally

### 1. Launch the Browser-Based Game (FastAPI + Three.js)

```powershell
# Navigate to the project directory:
cd "C:\Users\Admin\Desktop\study\vs code\lets try"

# Option A (Recommended): Launch with FastAPI & Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8080 --reload

# Option B: Launch with Unified Python Server
python server.py 8080
```

Open your browser:
- **Local PC:** `http://localhost:8080/`
- **Mobile Phone / Tablet on Local Wi-Fi:** `http://<your-computer-ip>:8080/`

---

### 2. Launch the Desktop Game (Pyglet + PyOpenGL)

```powershell
python main.py
```

---

### 3. Run the Automated Verification Test Suite

```powershell
python run_tests.py
```

---

## ☁️ Deployment Instructions

### Deploy to Render / Railway / Cloud VM

#### Docker Deployment
A minimal `Dockerfile` for deploying DAKSH BATTLE:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn
COPY . .
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Render.com / Railway.app Web Service
- **Build Command:** `pip install -r requirements.txt fastapi uvicorn`
- **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/api/status`

---

## ⚔️ Key Features & Systems

### 1. Realistic 3D Humanoid Characters & Skeletal Animations
- **Realistic Human Proportions:** Anatomical joint hierarchy with pelvis, spine, ribcage plate carrier with MOLLE webbing and magazine pouches, tactical chinstrap helmet with visor and comms headset, articulated shoulders, biceps, elbow pads, forearms, hands with fingers, tactical belt with canteen and sidearm holster, thighs with cargo pockets, knee pads, and laced combat boots with tread soles.
- **Joint-Based Skeletal Animations:**
  - `idle`: Natural breathing cycle, weight shift, subtle weapon sway.
  - `walk`: Bipedal foot stride with pelvis sway, inverse leg swing, and weapon bounce.
  - `run`: Aggressive sprint cycle with 18° torso lean, high knee drive, and arm pump.
  - `sprint`: High-octane tactical sprint with weapon at high ready.
  - `jump`: 3-phase jump: Launch compression -> Airborne leg tuck -> Impact landing knee-bend recovery.
  - `crouch`: Realistic 90° knee bend, hunched center of gravity, weapon held level at eye height.
  - `reload`: Left hand drops from foregrip to belt pouch, ejects spent magazine (physical falling 3D magazine), inserts fresh magazine with mechanical click, racks the bolt, and re-grips!
  - `weapon holding`: Distinct stances for rifles, snipers, shotguns, pistols, and ADS (Aim Down Sights zoom).
  - `victory`: Celebratory Booyah victory dance / two-handed rifle pump with fists in the air.
  - `defeat`: Knockdown stagger, knee buckle, and collapse onto the terrain.
  - `emotes`: Wave, Dance, Celebration, and Thumbs Up.

### 2. Tactical Island Environment & 3D Collision Detection
- **Detailed Terrain:** Island terrain with heightmap elevations, rolling interior hills, coastal beaches, and connecting dirt roads.
- **Tactical Buildings & Compounds:**
  - 4 Military Watchtowers with elevated observation decks, ladders, and railings.
  - 3 Reinforced Concrete Pillbox Bunkers with blast doors and firing slits.
  - 8 Corrugated Shipping Containers (stacked to form tactical cover and alleyways).
  - Sandbag Barricades at road checkpoints.
  - Scots Pine Trees with multi-tier branch cones and Deciduous broadleaf trees.
- **3D Collision Detection:** Continuous swept-sphere/box collision prevents walking through building walls, bunker walls, container boxes, watchtower pillars, sandbag walls, and tree trunks. Raycasting ensures bullets impact obstacles with particle sparks and smoke puffs.

### 3. Complete Weapon Armory (All 5 Categories)
Every weapon features unique ballistic stats (damage, fire rate, accuracy, effective range, mag capacity, reserve ammo, reload time, spread bloom, and recoil):
- **Assault Rifles (AR):** *Crimson Blaze* (34 DMG, high impact), *Golden Eagle* (29 DMG, laser precision)
- **Submachine Guns (SMG):** *Cobra MP5* (23 DMG, high mobility), *Neon Vector* (20 DMG, hyper burst)
- **Shotguns:** *Thunder SPAS* (16 DMG x 8 pellets), *Double Striker* (20 DMG x 8 pellets)
- **Pistols:** *Tactical G18* (22 DMG, high capacity sidearm), *Desert Hawk* (54 DMG, heavy .50 caliber magnum)
- **Sniper Rifles:** *Frostbite AWM* (115 DMG, cryogenic bolt-action), *Shadow Kar98k* (86 DMG, agile marksman)

### 4. Account Creation & Secure Profiles
- **Register Account:** Usernames validated (3-16 chars, letters/numbers/underscores only), passwords hashed using salted **PBKDF2-HMAC-SHA256**.
- **Clean Starter Progression:** Every new account starts at **Level 1**, **0 XP**, **Bronze I rank**, **500 starter coins**, **0 diamonds**, and starter gear.
- **Offline Guest Mode:** Instant play with default display name `Daksh_Battle`.
- **Google OAuth 2.0 Security:** Validates server configuration; displays clear status without fake credentials.

### 5. In-Game Settings & Emotes
- **Settings Modal (ESC):** Graphics Quality presets (*Smooth*, *Normal*, *Ultra*), Target FPS (*30*, *60*, *120*, *Max*), Aim Sensitivity slider, and Volume sliders (*Master*, *SFX*, *Music*).
- **Emotes System:** Triggerable anytime via `B` key, Emote modal, or mobile touch button: *Wave*, *Victory Dance*, *Celebration*, *Thumbs Up*.

---

## 🕹️ Controls Guide

### Desktop Controls
| Key / Input | Action |
|---|---|
| `W`, `A`, `S`, `D` | Movement |
| `Mouse` | Aim / Rotate third-person camera |
| `Left Click` | Fire equipped weapon |
| `Right Click` / `Scope` | Aim down sights (ADS zoom) |
| `Space` | Jump |
| `Shift` (Hold) | Sprint |
| `C` | Crouch (toggle tactical stance) |
| `1`, `2`, `3` | Switch Weapon Slots (AR, SMG/Shotgun, Pistol) |
| `R` | Reload current magazine |
| `B` | Trigger Emote animation |
| `Escape` | Pause match / Settings / Return to Lobby |

### Mobile Touch Controls
- **Left Thumb:** Floating virtual joystick for 360-degree analog movement.
- **Right Thumb:** Swipe surface for camera orientation and aiming.
- **Weapon Slots (1, 2, 3):** Tap on-screen slot pills to switch weapons instantly.
- **Touch Action Buttons:** Dedicated on-screen buttons for **FIRE**, **SCOPE**, **JUMP**, **CROUCH**, **SPRINT**, **RELOAD**, and **EMOTE**.
- **Landscape Lock Prompt:** Automatically guides players to hold their device horizontally.

---

## 📂 Project Architecture

```
DAKSH_BATTLE/
├── assets/                     # 32 Extracted original artwork & UI assets
│   ├── game_logo.png           # Official DAKSH BATTLE crown emblem
│   ├── splash_background.png   # Island battlefield splash
│   ├── login_background.png    # Cinematic dual-character login
│   ├── lobby_background.png    # Futuristic city skyline lobby
│   ├── player_character.png    # Operator character showcase
│   ├── pet_panda.png           # Tactical pet panda companion
│   ├── badge_bronze.png ...    # 7 Rank badges (Bronze to Master)
│   └── weapon_*.png            # Weapon icons and portraits
├── web/                        # Dual-Platform Web & Mobile Browser Client
│   ├── libs/
│   │   └── three.min.js        # Offline Three.js library
│   ├── index.html              # HTML5 Web client layout & mobile HUD
│   ├── style.css               # Free Fire inspired dark futuristic CSS
│   └── game.js                 # Three.js 3D WebGL engine & skeletal animations
├── data/
│   └── accounts.json           # Secure user accounts & PBKDF2 hashes
├── app.py                      # FastAPI modern REST API backend & static server
├── server.py                   # High-performance server with Uvicorn / HTTP fallback
├── main.py                     # Desktop game entry point (Pyglet + OpenGL)
├── auth_manager.py             # User registration, authentication & profiles
├── weapons.py                  # Weapon catalog across all 5 classes
├── arena.py                    # Desktop 3D procedural arena, towers & airship
├── player.py                   # Desktop Player physics, ballistics & emotes
├── bot_ai.py                   # AI rival bots with state machines
├── projectiles.py              # Ballistic projectiles & hit detection
├── camera_controller.py        # Third-person orbit camera
├── renderer.py                 # PyOpenGL 2.1 fixed-function pipeline
├── ui.py                       # Desktop 2D UI system & modals
├── settings.py                 # Global constants & runtime configs
├── run_tests.py                # Automated 9-point verification suite
└── requirements.txt            # Python dependencies
```
