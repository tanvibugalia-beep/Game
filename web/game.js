/**
 * DAKSH BATTLE — Play • Fight • Survive
 * Complete 3D WebGL Battle Royale Game Engine (Three.js)
 * Dual-Platform: Desktop & Mobile Browser Optimized
 * Features:
 * - Realistic Humanoid Anatomical Rigs with Tactical Gear & Weapons
 * - Joint-Based Hierarchical Skeletal Animation State Machine
 * - Detailed Terrain, Roads, Military Watchtowers, Concrete Bunkers, Buildings, Containers
 * - 3D Obstacle & Wall Collision Detection
 * - 5 Full Weapon Classes with Ballistics, Recoil, Spread & Reload Animations
 * - FSM AI Bots with Navigation & Line-of-Sight
 * - Web Audio API Procedural Sound Synthesis
 * - Mobile Touch Joystick, Swipe Look, Touch Buttons & Desktop Keyboard/Mouse Controls
 * - Dedicated Loading Screen, Lobby & Results Screen with Backend API Sync
 */

// ── 1. Global Configurations & Weapon Catalog ─────────────────────────────────

const WEAPON_CATALOG = {
  // Assault Rifles
  "Crimson Blaze": {
    name: "Crimson Blaze", category: "AR", tier: "EPIC",
    damage: 34, fireRate: 0.11, range: 60, accuracy: 78, reloadTime: 2.1,
    magSize: 30, totalAmmo: 120, pellets: 1, spread: 0.02,
    color: 0xe62020, desc: "High-impact tactical rifle equipped with a crimson flame shroud."
  },
  "Golden Eagle": {
    name: "Golden Eagle", category: "AR", tier: "LEGENDARY",
    damage: 29, fireRate: 0.088, range: 55, accuracy: 82, reloadTime: 1.9,
    magSize: 35, totalAmmo: 140, pellets: 1, spread: 0.018,
    color: 0xf5b018, desc: "Rapid-fire precision carbine with golden titanium heat sink."
  },
  // Submachine Guns
  "Cobra MP5": {
    name: "Cobra MP5", category: "SMG", tier: "RARE",
    damage: 23, fireRate: 0.072, range: 35, accuracy: 70, reloadTime: 1.6,
    magSize: 32, totalAmmo: 160, pellets: 1, spread: 0.035,
    color: 0x2ecc71, desc: "Lightweight close-quarters submachine gun with high stability."
  },
  "Neon Vector": {
    name: "Neon Vector", category: "SMG", tier: "EPIC",
    damage: 20, fireRate: 0.054, range: 30, accuracy: 65, reloadTime: 1.5,
    magSize: 33, totalAmmo: 165, pellets: 1, spread: 0.042,
    color: 0x00d2ff, desc: "Hyper-velocity burst SMG shredding rivals at close range."
  },
  // Shotguns
  "Thunder SPAS": {
    name: "Thunder SPAS", category: "Shotgun", tier: "RARE",
    damage: 16, fireRate: 0.65, range: 20, accuracy: 45, reloadTime: 2.4,
    magSize: 8, totalAmmo: 40, pellets: 8, spread: 0.11,
    color: 0xff7700, desc: "Tactical pump-action shotgun delivering a lethal 8-pellet spread."
  },
  "Double Striker": {
    name: "Double Striker", category: "Shotgun", tier: "LEGENDARY",
    damage: 20, fireRate: 0.32, range: 16, accuracy: 40, reloadTime: 2.0,
    magSize: 2, totalAmmo: 30, pellets: 8, spread: 0.14,
    color: 0xe74c3c, desc: "Twin-barrel powerhouse delivering immense instantaneous burst."
  },
  // Pistols
  "Tactical G18": {
    name: "Tactical G18", category: "Pistol", tier: "COMMON",
    damage: 22, fireRate: 0.13, range: 30, accuracy: 72, reloadTime: 1.4,
    magSize: 17, totalAmmo: 85, pellets: 1, spread: 0.028,
    color: 0xbdc3c7, desc: "Reliable high-capacity sidearm with quick-draw response."
  },
  "Desert Hawk": {
    name: "Desert Hawk", category: "Pistol", tier: "EPIC",
    damage: 54, fireRate: 0.36, range: 45, accuracy: 80, reloadTime: 1.7,
    magSize: 7, totalAmmo: 35, pellets: 1, spread: 0.02,
    color: 0xf39c12, desc: "Heavy .50 caliber magnum pistol with bone-crushing impact."
  },
  // Sniper Rifles
  "Frostbite AWM": {
    name: "Frostbite AWM", category: "Sniper", tier: "MYTHIC",
    damage: 115, fireRate: 1.25, range: 120, accuracy: 96, reloadTime: 2.8,
    magSize: 5, totalAmmo: 25, pellets: 1, spread: 0.004,
    color: 0x3498db, desc: "Cryogenic bolt-action heavy sniper rifle with match-grade accuracy."
  },
  "Shadow Kar98k": {
    name: "Shadow Kar98k", category: "Sniper", tier: "EPIC",
    damage: 86, fireRate: 0.92, range: 95, accuracy: 92, reloadTime: 2.3,
    magSize: 5, totalAmmo: 30, pellets: 1, spread: 0.007,
    color: 0x9b59b6, desc: "Agile marksman rifle built for high mobility and swift target acquisition."
  }
};

const RANK_TIERS = [
  { name: "Bronze", minScore: 0, badge: "/assets/badge_bronze.png" },
  { name: "Silver", minScore: 500, badge: "/assets/badge_silver.png" },
  { name: "Gold", minScore: 1000, badge: "/assets/badge_gold.png" },
  { name: "Platinum", minScore: 1600, badge: "/assets/badge_platinum.png" },
  { name: "Diamond", minScore: 2300, badge: "/assets/badge_diamond.png" },
  { name: "Heroic", minScore: 3200, badge: "/assets/badge_heroic.png" },
  { name: "Master", minScore: 4500, badge: "/assets/badge_master.png" }
];

// Profile & Persistent State
let currentUser = {
  username: "Daksh_Battle",
  is_guest: true,
  level: 1,
  xp: 0,
  xp_next: 1000,
  rank_name: "Bronze",
  rank_score: 0,
  coins: 500,
  diamonds: 0,
  selected_character: "Daksh",
  selected_weapon: "Crimson Blaze",
  equipped_weapons: {
    AR: "Crimson Blaze",
    SMG: "Cobra MP5",
    Shotgun: "Thunder SPAS",
    Pistol: "Tactical G18",
    Sniper: "Shadow Kar98k"
  },
  equipped_emotes: ["wave", "dance", "celebration", "thumbs_up"],
  mail_claimed: false,
  settings: {
    graphics_preset: "Normal",
    fps_cap: 60,
    mouse_sens: 0.20,
    vol_master: 0.70,
    vol_sfx: 0.80,
    vol_music: 0.50
  }
};

// ── 2. Procedural Texture Factory ─────────────────────────────────────────────

const TextureFactory = {
  _cache: {},

  createDigitalCamo(baseColor = "#263238", spotColor1 = "#37474f", spotColor2 = "#102027") {
    const key = `camo_${baseColor}_${spotColor1}_${spotColor2}`;
    if (this._cache[key]) return this._cache[key];

    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = baseColor;
    ctx.fillRect(0, 0, 256, 256);

    const colors = [spotColor1, spotColor2, "#1a1a1a"];
    const blockSize = 16;
    for (let x = 0; x < 256; x += blockSize) {
      for (let y = 0; y < 256; y += blockSize) {
        if (Math.random() > 0.45) {
          ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
          ctx.fillRect(x, y, blockSize, blockSize);
        }
      }
    }

    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    this._cache[key] = tex;
    return tex;
  },

  createPlateCarrierTexture(color = "#1f2421") {
    const key = `plate_${color}`;
    if (this._cache[key]) return this._cache[key];

    const canvas = document.createElement("canvas");
    canvas.width = 128;
    canvas.height = 128;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = color;
    ctx.fillRect(0, 0, 128, 128);

    // MOLLE webbing lines
    ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
    for (let y = 16; y < 128; y += 24) {
      ctx.fillRect(0, y, 128, 6);
      // Stitch marks
      ctx.fillStyle = "rgba(255, 255, 255, 0.25)";
      for (let x = 8; x < 128; x += 18) {
        ctx.fillRect(x, y - 2, 2, 10);
      }
      ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
    }

    const tex = new THREE.CanvasTexture(canvas);
    this._cache[key] = tex;
    return tex;
  },

  createContainerTexture(color = "#b71c1c") {
    const key = `container_${color}`;
    if (this._cache[key]) return this._cache[key];

    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 128;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = color;
    ctx.fillRect(0, 0, 256, 128);

    // Corrugation ridges
    for (let x = 0; x < 256; x += 16) {
      ctx.fillStyle = "rgba(0, 0, 0, 0.35)";
      ctx.fillRect(x, 0, 6, 128);
      ctx.fillStyle = "rgba(255, 255, 255, 0.2)";
      ctx.fillRect(x + 6, 0, 3, 128);
    }

    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    this._cache[key] = tex;
    return tex;
  },

  createConcreteTexture() {
    if (this._cache["concrete"]) return this._cache["concrete"];
    const canvas = document.createElement("canvas");
    canvas.width = 128;
    canvas.height = 128;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "#616161";
    ctx.fillRect(0, 0, 128, 128);

    for (let i = 0; i < 400; i++) {
      const x = Math.random() * 128;
      const y = Math.random() * 128;
      ctx.fillStyle = Math.random() > 0.5 ? "rgba(0,0,0,0.15)" : "rgba(255,255,255,0.1)";
      ctx.fillRect(x, y, 2, 2);
    }

    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    this._cache["concrete"] = tex;
    return tex;
  }
};

// ── 3. Web Audio API Sound Synthesizer ────────────────────────────────────────

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.sfxGain = null;
  }

  init() {
    if (this.ctx) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.value = currentUser.settings.vol_master;
      this.masterGain.connect(this.ctx.destination);

      this.sfxGain = this.ctx.createGain();
      this.sfxGain.gain.value = currentUser.settings.vol_sfx;
      this.sfxGain.connect(this.masterGain);
    } catch (e) {
      console.warn("Web Audio API not supported:", e);
    }
  }

  updateVolumes() {
    if (!this.ctx) return;
    this.masterGain.gain.value = currentUser.settings.vol_master;
    this.sfxGain.gain.value = currentUser.settings.vol_sfx;
  }

  playShot(category = "AR") {
    if (!this.ctx) this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;

    const isSniper = category === "Sniper";
    const isShotgun = category === "Shotgun";
    const isPistol = category === "Pistol";

    const bufferSize = this.ctx.sampleRate * (isSniper ? 0.22 : 0.12);
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.22));
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = isSniper ? "bandpass" : "lowpass";
    filter.frequency.setValueAtTime(isShotgun ? 1200 : (isPistol ? 2800 : 2200), now);
    filter.frequency.exponentialRampToValueAtTime(120, now + 0.1);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(isSniper ? 0.95 : (isShotgun ? 0.85 : 0.65), now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + (isSniper ? 0.22 : 0.12));

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.sfxGain);
    noise.start(now);

    // Punch oscillator
    const osc = this.ctx.createOscillator();
    const oscGain = this.ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(isSniper ? 180 : (isShotgun ? 90 : 130), now);
    osc.frequency.exponentialRampToValueAtTime(25, now + 0.09);

    oscGain.gain.setValueAtTime(0.7, now);
    oscGain.gain.exponentialRampToValueAtTime(0.01, now + 0.09);

    osc.connect(oscGain);
    oscGain.connect(this.sfxGain);
    osc.start(now);
    osc.stop(now + 0.1);
  }

  playHit() {
    if (!this.ctx) this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(950, now);
    osc.frequency.setValueAtTime(1450, now + 0.04);

    gain.gain.setValueAtTime(0.5, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);

    osc.connect(gain);
    gain.connect(this.sfxGain);
    osc.start(now);
    osc.stop(now + 0.1);
  }

  playReload() {
    if (!this.ctx) this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    [0, 0.35, 0.7].forEach((t, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "square";
      osc.frequency.setValueAtTime(320 + i * 160, now + t);
      gain.gain.setValueAtTime(0.3, now + t);
      gain.gain.exponentialRampToValueAtTime(0.01, now + t + 0.07);
      osc.connect(gain);
      gain.connect(this.sfxGain);
      osc.start(now + t);
      osc.stop(now + t + 0.08);
    });
  }

  playFootstep() {
    if (!this.ctx) this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(80, now);
    osc.frequency.exponentialRampToValueAtTime(30, now + 0.05);
    gain.gain.setValueAtTime(0.18, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
    osc.connect(gain);
    gain.connect(this.sfxGain);
    osc.start(now);
    osc.stop(now + 0.06);
  }

  playBooyah() {
    if (!this.ctx) this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
    notes.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq, now + idx * 0.15);
      gain.gain.setValueAtTime(0.5, now + idx * 0.15);
      gain.gain.exponentialRampToValueAtTime(0.01, now + idx * 0.15 + 0.45);
      osc.connect(gain);
      gain.connect(this.sfxGain);
      osc.start(now + idx * 0.15);
      osc.stop(now + idx * 0.15 + 0.5);
    });
  }

  playClick() {
    if (!this.ctx) this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(600, now);
    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.03);
    osc.connect(gain);
    gain.connect(this.sfxGain);
    osc.start(now);
    osc.stop(now + 0.04);
  }
}

const sounds = new SoundEngine();

// ── 4. REST API & Data Client ─────────────────────────────────────────────────

const API = {
  async fetchProfile() {
    try {
      const res = await fetch("/api/profile");
      if (res.ok) {
        const json = await res.json();
        if (json.profile) {
          currentUser = json.profile;
          return true;
        }
      }
    } catch (e) {}
    const saved = localStorage.getItem("daksh_battle_user");
    if (saved) {
      try { currentUser = JSON.parse(saved); } catch (e) {}
    }
    return false;
  },

  async register(username, password) {
    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        currentUser = data.profile;
        localStorage.setItem("daksh_battle_user", JSON.stringify(currentUser));
        return { ok: true, msg: data.message };
      }
      return { ok: false, msg: data.detail || data.error || "Registration failed" };
    } catch (e) {
      if (!username || username.length < 3) return { ok: false, msg: "Username must be 3-16 characters." };
      currentUser.username = username;
      currentUser.is_guest = false;
      currentUser.level = 1;
      currentUser.xp = 0;
      currentUser.rank_score = 0;
      currentUser.rank_name = "Bronze";
      currentUser.coins = 500;
      currentUser.diamonds = 0;
      localStorage.setItem("daksh_battle_user", JSON.stringify(currentUser));
      return { ok: true, msg: "Account created (Local fallback mode)" };
    }
  },

  async login(username, password) {
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        currentUser = data.profile;
        localStorage.setItem("daksh_battle_user", JSON.stringify(currentUser));
        return { ok: true, msg: data.message };
      }
      return { ok: false, msg: data.detail || data.error || "Invalid credentials" };
    } catch (e) {
      return { ok: false, msg: "Backend offline. Use Guest mode." };
    }
  },

  async loginGuest(guestName = "Daksh_Battle") {
    try {
      const res = await fetch("/api/guest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ guest_id: guestName })
      });
      if (res.ok) {
        const data = await res.json();
        currentUser = data.profile;
      }
    } catch (e) {
      currentUser.username = guestName || "Daksh_Battle";
      currentUser.is_guest = true;
    }
    localStorage.setItem("daksh_battle_user", JSON.stringify(currentUser));
    return currentUser;
  },

  async saveProfile() {
    localStorage.setItem("daksh_battle_user", JSON.stringify(currentUser));
    try {
      await fetch("/api/profile/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(currentUser)
      });
    } catch (e) {}
  },

  async recordMatch(won, kills, score, duration) {
    try {
      const res = await fetch("/api/match/record", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ won, kills, score, duration })
      });
      if (res.ok) {
        const data = await res.json();
        currentUser = data.profile;
        localStorage.setItem("daksh_battle_user", JSON.stringify(currentUser));
        return data.result;
      }
    } catch (e) {}

    // Offline progression calculation
    const coinsEarned = kills * 80 + (won ? 400 : 80);
    const diamondsEarned = won ? 5 : 1;
    const xpEarned = kills * 50 + (won ? 250 : 50);
    const scoreEarned = kills * 25 + (won ? 80 : 15);

    currentUser.coins += coinsEarned;
    currentUser.diamonds += diamondsEarned;
    currentUser.xp += xpEarned;
    currentUser.rank_score += scoreEarned;

    for (let i = RANK_TIERS.length - 1; i >= 0; i--) {
      if (currentUser.rank_score >= RANK_TIERS[i].minScore) {
        currentUser.rank_name = RANK_TIERS[i].name;
        break;
      }
    }
    if (currentUser.xp >= currentUser.xp_next) {
      currentUser.level += 1;
      currentUser.xp -= currentUser.xp_next;
      currentUser.xp_next = Math.floor(currentUser.xp_next * 1.5);
    }
    localStorage.setItem("daksh_battle_user", JSON.stringify(currentUser));
    return { won, kills, coins_earned: coinsEarned, diamonds_earned: diamondsEarned, xp_earned: xpEarned, rank_points_earned: scoreEarned };
  }
};

// ── 5. Humanoid Character & Weapon Rigging System ──────────────────────────────

class CharacterFactory {
  /**
   * Constructs an anatomically proportioned humanoid combatant mesh with articulated skeletal joints.
   */
  static createHumanoid(options = {}) {
    const isPlayer = options.isPlayer || false;
    const charName = options.characterName || (isPlayer ? currentUser.selected_character : "Rival");
    const isMaya = charName === "Maya";
    const primaryColor = isMaya ? 0x00d2ff : (isPlayer ? 0xe62020 : (options.color || 0x3498db));

    const rootGroup = new THREE.Group();

    // Textures
    const camoTex = TextureFactory.createDigitalCamo(
      isMaya ? "#0d47a1" : (isPlayer ? "#b71c1c" : "#263238"),
      isMaya ? "#1976d2" : (isPlayer ? "#e53935" : "#455a64")
    );
    const vestTex = TextureFactory.createPlateCarrierTexture(isPlayer ? "#212121" : "#1a1a1a");

    const skinMat = new THREE.MeshLambertMaterial({ color: isMaya ? 0xf5cba7 : 0xd4a373 });
    const camoMat = new THREE.MeshLambertMaterial({ map: camoTex });
    const vestMat = new THREE.MeshLambertMaterial({ map: vestTex });
    const darkMat = new THREE.MeshLambertMaterial({ color: 0x181818 });
    const goldMat = new THREE.MeshLambertMaterial({ color: 0xf5b018 });
    const visorMat = new THREE.MeshBasicMaterial({ color: primaryColor });

    // ── Joint Structure ───────────────────────────────────────────────────────
    // Pelvis / Hips (Root pivot of humanoid)
    const pelvis = new THREE.Group();
    pelvis.position.y = 0.95; // 0.95m off ground
    rootGroup.add(pelvis);

    const pelvisMesh = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.22, 0.24), camoMat);
    pelvisMesh.castShadow = true;
    pelvis.add(pelvisMesh);

    // Tactical Utility Belt
    const belt = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.08, 0.26), darkMat);
    belt.position.y = 0.08;
    pelvis.add(belt);

    // Canteen & Ammo Pouches on Belt
    const canteen = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.12, 0.08), darkMat);
    canteen.position.set(-0.16, 0.02, -0.12);
    pelvis.add(canteen);

    // ── Spine & Torso (Plate Carrier) ─────────────────────────────────────────
    const spine = new THREE.Group();
    spine.position.y = 0.12;
    pelvis.add(spine);

    const torsoMesh = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.44, 0.26), vestMat);
    torsoMesh.position.y = 0.22;
    torsoMesh.castShadow = true;
    spine.add(torsoMesh);

    // Tactical Front Magazine Pouches
    const pouches = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.16, 0.08), darkMat);
    pouches.position.set(0, 0.18, 0.16);
    spine.add(pouches);

    // Tactical Backpack on Back
    const backpack = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.36, 0.16), darkMat);
    backpack.position.set(0, 0.24, -0.18);
    backpack.castShadow = true;
    spine.add(backpack);

    // ── Neck & Head ───────────────────────────────────────────────────────────
    const neck = new THREE.Group();
    neck.position.y = 0.44;
    spine.add(neck);

    const headGroup = new THREE.Group();
    headGroup.position.y = 0.12;
    neck.add(headGroup);

    // Face / Head
    const face = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.24, 0.22), skinMat);
    face.castShadow = true;
    headGroup.add(face);

    // Ballistic Combat Helmet
    const helmet = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.16, 0.26), darkMat);
    helmet.position.set(0, 0.08, -0.01);
    headGroup.add(helmet);

    // Glowing Tactical Visor / Goggles
    const visor = new THREE.Mesh(new THREE.BoxGeometry(0.20, 0.07, 0.06), visorMat);
    visor.position.set(0, 0.02, 0.12);
    headGroup.add(visor);

    // Comms Headset with Mic
    const headset = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.26, 6), darkMat);
    headset.rotation.z = Math.PI / 2;
    headset.position.set(0, 0.04, 0);
    headGroup.add(headset);

    const mic = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.02, 0.12), goldMat);
    mic.position.set(0.12, -0.04, 0.08);
    headGroup.add(mic);

    // ── Left Arm Hierarchy ────────────────────────────────────────────────────
    const leftShoulder = new THREE.Group();
    leftShoulder.position.set(-0.25, 0.38, 0.02);
    spine.add(leftShoulder);

    const leftUpperArm = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.055, 0.26, 6), camoMat);
    leftUpperArm.position.y = -0.13;
    leftUpperArm.castShadow = true;
    leftShoulder.add(leftUpperArm);

    const leftElbow = new THREE.Group();
    leftElbow.position.y = -0.26;
    leftShoulder.add(leftElbow);

    const leftElbowPad = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 0.06), darkMat);
    leftElbowPad.position.z = -0.04;
    leftElbow.add(leftElbowPad);

    const leftForearm = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.05, 0.24, 6), camoMat);
    leftForearm.position.y = -0.12;
    leftForearm.castShadow = true;
    leftElbow.add(leftForearm);

    const leftHand = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.10, 0.06), darkMat);
    leftHand.position.y = -0.26;
    leftElbow.add(leftHand);

    // ── Right Arm Hierarchy (Weapon Grip) ─────────────────────────────────────
    const rightShoulder = new THREE.Group();
    rightShoulder.position.set(0.25, 0.38, 0.02);
    spine.add(rightShoulder);

    const rightUpperArm = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.055, 0.26, 6), camoMat);
    rightUpperArm.position.y = -0.13;
    rightUpperArm.castShadow = true;
    rightShoulder.add(rightUpperArm);

    const rightElbow = new THREE.Group();
    rightElbow.position.y = -0.26;
    rightShoulder.add(rightElbow);

    const rightElbowPad = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 0.06), darkMat);
    rightElbowPad.position.z = -0.04;
    rightElbow.add(rightElbowPad);

    const rightForearm = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.05, 0.24, 6), camoMat);
    rightForearm.position.y = -0.12;
    rightForearm.castShadow = true;
    rightElbow.add(rightForearm);

    const rightHand = new THREE.Group();
    rightHand.position.y = -0.26;
    rightElbow.add(rightHand);

    const rightHandMesh = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.10, 0.06), darkMat);
    rightHand.add(rightHandMesh);

    // ── Left Leg Hierarchy ────────────────────────────────────────────────────
    const leftHip = new THREE.Group();
    leftHip.position.set(-0.11, -0.10, 0);
    pelvis.add(leftHip);

    const leftThigh = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.065, 0.40, 6), camoMat);
    leftThigh.position.y = -0.20;
    leftThigh.castShadow = true;
    leftHip.add(leftThigh);

    const leftKnee = new THREE.Group();
    leftKnee.position.y = -0.40;
    leftHip.add(leftKnee);

    const leftKneePad = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.10, 0.06), darkMat);
    leftKneePad.position.z = 0.06;
    leftKnee.add(leftKneePad);

    const leftShin = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.055, 0.38, 6), camoMat);
    leftShin.position.y = -0.19;
    leftShin.castShadow = true;
    leftKnee.add(leftShin);

    const leftFoot = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.12, 0.22), darkMat);
    leftFoot.position.set(0, -0.40, 0.05);
    leftFoot.castShadow = true;
    leftKnee.add(leftFoot);

    // ── Right Leg Hierarchy ───────────────────────────────────────────────────
    const rightHip = new THREE.Group();
    rightHip.position.set(0.11, -0.10, 0);
    pelvis.add(rightHip);

    const rightThigh = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.065, 0.40, 6), camoMat);
    rightThigh.position.y = -0.20;
    rightThigh.castShadow = true;
    rightHip.add(rightThigh);

    // Holster on Right Thigh
    const holster = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.14, 0.08), darkMat);
    holster.position.set(0.09, -0.18, 0.02);
    rightHip.add(holster);

    const rightKnee = new THREE.Group();
    rightKnee.position.y = -0.40;
    rightHip.add(rightKnee);

    const rightKneePad = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.10, 0.06), darkMat);
    rightKneePad.position.z = 0.06;
    rightKnee.add(rightKneePad);

    const rightShin = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.055, 0.38, 6), camoMat);
    rightShin.position.y = -0.19;
    rightShin.castShadow = true;
    rightKnee.add(rightShin);

    const rightFoot = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.12, 0.22), darkMat);
    rightFoot.position.set(0, -0.40, 0.05);
    rightFoot.castShadow = true;
    rightKnee.add(rightFoot);

    // ── Weapon Model Attachment ───────────────────────────────────────────────
    const weaponGroup = new THREE.Group();
    rightHand.add(weaponGroup);
    weaponGroup.position.set(0, -0.04, 0.16);
    weaponGroup.rotation.x = -Math.PI / 2;

    const currentWeaponName = isPlayer ? (currentUser.selected_weapon || "Crimson Blaze") : "Crimson Blaze";
    this.buildWeaponMesh(weaponGroup, currentWeaponName);

    return {
      group: rootGroup,
      bones: {
        pelvis, spine, neck, head: headGroup,
        leftShoulder, leftElbow, leftHand,
        rightShoulder, rightElbow, rightHand,
        leftHip, leftKnee,
        rightHip, rightKnee
      },
      weaponGroup
    };
  }

  /**
   * Constructs high-detail 3D models for all 5 weapon categories.
   */
  static buildWeaponMesh(parentGroup, weaponName) {
    while (parentGroup.children.length > 0) {
      parentGroup.remove(parentGroup.children[0]);
    }

    const spec = WEAPON_CATALOG[weaponName] || WEAPON_CATALOG["Crimson Blaze"];
    const cat = spec.category;
    const accentColor = spec.color || 0xe62020;

    const metalMat = new THREE.MeshLambertMaterial({ color: 0x212121 });
    const barrelMat = new THREE.MeshLambertMaterial({ color: 0x111111 });
    const accentMat = new THREE.MeshLambertMaterial({ color: accentColor });
    const opticGlassMat = new THREE.MeshBasicMaterial({ color: 0x00d2ff, transparent: true, opacity: 0.65 });

    if (cat === "Sniper") {
      // Extended match-grade barrel
      const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.025, 1.25, 8), barrelMat);
      barrel.position.set(0, 0.55, 0);
      parentGroup.add(barrel);

      // Heavy receiver
      const receiver = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.40, 0.12), accentMat);
      parentGroup.add(receiver);

      // Large Telescopic Sniper Scope
      const scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.38, 8), metalMat);
      scopeBody.position.set(0, 0.05, 0.10);
      parentGroup.add(scopeBody);

      const scopeLens = new THREE.Mesh(new THREE.CircleGeometry(0.032, 8), opticGlassMat);
      scopeLens.position.set(0, 0.24, 0.10);
      parentGroup.add(scopeLens);

      // Thumbhole target stock
      const stock = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.32, 0.10), metalMat);
      stock.position.set(0, -0.32, -0.02);
      parentGroup.add(stock);

    } else if (cat === "Shotgun") {
      // Twin-barrel or heavy pump shotgun
      const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.035, 0.85, 8), barrelMat);
      barrel.position.set(0, 0.35, 0.03);
      parentGroup.add(barrel);

      const magTube = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.70, 8), metalMat);
      magTube.position.set(0, 0.30, -0.03);
      parentGroup.add(magTube);

      // Ribbed pump slide
      const pump = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.22, 0.10), accentMat);
      pump.position.set(0, 0.30, 0);
      parentGroup.add(pump);

      const receiver = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.35, 0.14), metalMat);
      parentGroup.add(receiver);

      const stock = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.30, 0.12), accentMat);
      stock.position.set(0, -0.30, -0.02);
      parentGroup.add(stock);

    } else if (cat === "SMG") {
      // Compact receiver with vertical foregrip
      const receiver = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.32, 0.12), accentMat);
      parentGroup.add(receiver);

      const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.025, 0.35, 8), barrelMat);
      barrel.position.set(0, 0.28, 0.02);
      parentGroup.add(barrel);

      // Straight box magazine
      const mag = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.26, 0.05), metalMat);
      mag.position.set(0, 0.05, -0.14);
      parentGroup.add(mag);

      // Vertical foregrip
      const foregrip = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.12, 6), metalMat);
      foregrip.position.set(0, 0.20, -0.08);
      parentGroup.add(foregrip);

    } else if (cat === "Pistol") {
      // Tactical sidearm slide & frame
      const slide = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.24, 0.08), accentMat);
      slide.position.set(0, 0.08, 0.04);
      parentGroup.add(slide);

      const frame = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.16, 0.10), metalMat);
      frame.position.set(0, -0.06, -0.02);
      parentGroup.add(frame);

    } else {
      // Assault Rifle (Default)
      const receiver = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.42, 0.12), metalMat);
      parentGroup.add(receiver);

      const shroud = new THREE.Mesh(new THREE.BoxGeometry(0.065, 0.30, 0.08), accentMat);
      shroud.position.set(0, 0.32, 0.01);
      parentGroup.add(shroud);

      const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.022, 0.35, 8), barrelMat);
      barrel.position.set(0, 0.58, 0.01);
      parentGroup.add(barrel);

      // Curved banana magazine
      const mag = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.26, 0.08), accentMat);
      mag.position.set(0, 0.08, -0.14);
      mag.rotation.x = 0.25;
      parentGroup.add(mag);

      // Red-dot optic sight
      const optic = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.12, 0.08), metalMat);
      optic.position.set(0, 0.06, 0.09);
      parentGroup.add(optic);

      const lens = new THREE.Mesh(new THREE.CircleGeometry(0.025, 8), opticGlassMat);
      lens.position.set(0, 0.12, 0.09);
      parentGroup.add(lens);

      const stock = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.25, 0.10), metalMat);
      stock.position.set(0, -0.28, -0.01);
      parentGroup.add(stock);
    }
  }
}

// ── 6. Skeletal Animation State Machine ────────────────────────────────────────

class CharacterAnimator {
  static update(entity, dt) {
    const bones = entity.mesh.bones;
    if (!bones) return;

    const state = entity.animState || "idle";
    const speed = entity.currentSpeed || 0;
    const t = entity.animTime = (entity.animTime || 0) + dt;

    // Reset base rotations
    bones.pelvis.rotation.set(0, 0, 0);
    bones.spine.rotation.set(0, 0, 0);
    bones.neck.rotation.set(0, 0, 0);
    bones.leftShoulder.rotation.set(0, 0, 0);
    bones.leftElbow.rotation.set(0, 0, 0);
    bones.rightShoulder.rotation.set(0, 0, 0);
    bones.rightElbow.rotation.set(0, 0, 0);
    bones.leftHip.rotation.set(0, 0, 0);
    bones.leftKnee.rotation.set(0, 0, 0);
    bones.rightHip.rotation.set(0, 0, 0);
    bones.rightKnee.rotation.set(0, 0, 0);

    // ── 1. Idle Breathing ─────────────────────────────────────────────────────
    if (state === "idle") {
      const breath = Math.sin(t * 2.4);
      bones.spine.rotation.x = breath * 0.025;
      bones.spine.scale.set(1 + breath * 0.015, 1, 1 + breath * 0.015);
      bones.neck.rotation.y = Math.sin(t * 0.8) * 0.06;

      // Two-handed ready pose
      bones.rightShoulder.rotation.x = 0.95 + breath * 0.02;
      bones.rightShoulder.rotation.y = -0.32;
      bones.rightElbow.rotation.x = -0.85;

      bones.leftShoulder.rotation.x = 0.90 + breath * 0.02;
      bones.leftShoulder.rotation.y = 0.42;
      bones.leftElbow.rotation.x = -1.15;

      bones.pelvis.position.y = 0.95 + Math.abs(breath) * 0.015;
    }

    // ── 2. Walk Cycle ─────────────────────────────────────────────────────────
    else if (state === "walk") {
      const stride = t * 7.5;
      const legSwing = Math.sin(stride) * 0.55;
      const armSwing = Math.cos(stride) * 0.35;

      bones.leftHip.rotation.x = legSwing;
      bones.leftKnee.rotation.x = Math.max(0, -legSwing * 0.9);

      bones.rightHip.rotation.x = -legSwing;
      bones.rightKnee.rotation.x = Math.max(0, legSwing * 0.9);

      bones.pelvis.position.y = 0.95 + Math.abs(Math.sin(stride)) * 0.04;
      bones.pelvis.rotation.y = Math.sin(stride) * 0.08;

      // Weapon held during walk
      bones.rightShoulder.rotation.x = 0.90 + armSwing * 0.15;
      bones.rightShoulder.rotation.y = -0.30;
      bones.rightElbow.rotation.x = -0.80;

      bones.leftShoulder.rotation.x = 0.85 - armSwing * 0.15;
      bones.leftShoulder.rotation.y = 0.40;
      bones.leftElbow.rotation.x = -1.10;
    }

    // ── 3. Run & Sprint Cycle ─────────────────────────────────────────────────
    else if (state === "run" || state === "sprint") {
      const isSprint = state === "sprint";
      const stride = t * (isSprint ? 14.0 : 10.5);
      const legSwing = Math.sin(stride) * (isSprint ? 0.95 : 0.75);

      // Torso lean
      bones.spine.rotation.x = isSprint ? 0.32 : 0.20;
      bones.pelvis.position.y = 0.92 + Math.abs(Math.sin(stride)) * 0.08;
      bones.pelvis.rotation.y = Math.sin(stride) * 0.12;

      bones.leftHip.rotation.x = legSwing;
      bones.leftKnee.rotation.x = Math.max(0, -legSwing * 1.3);

      bones.rightHip.rotation.x = -legSwing;
      bones.rightKnee.rotation.x = Math.max(0, legSwing * 1.3);

      // Vigorous arms pumping with rifle
      bones.rightShoulder.rotation.x = 1.15 + Math.sin(stride) * 0.30;
      bones.rightShoulder.rotation.y = -0.28;
      bones.rightElbow.rotation.x = -1.0;

      bones.leftShoulder.rotation.x = 1.05 - Math.sin(stride) * 0.30;
      bones.leftShoulder.rotation.y = 0.45;
      bones.leftElbow.rotation.x = -1.25;
    }

    // ── 4. Jump & Airborne ────────────────────────────────────────────────────
    else if (state === "jump") {
      bones.pelvis.position.y = 1.05;
      // Legs tucked upward in mid-air
      bones.leftHip.rotation.x = -0.45;
      bones.leftKnee.rotation.x = 0.85;
      bones.rightHip.rotation.x = -0.35;
      bones.rightKnee.rotation.x = 0.75;

      bones.spine.rotation.x = -0.15;
      bones.rightShoulder.rotation.x = 1.25;
      bones.leftShoulder.rotation.x = 1.15;
    }

    // ── 5. Landing Impact ─────────────────────────────────────────────────────
    else if (state === "landing") {
      bones.pelvis.position.y = 0.80; // Deep knee compression
      bones.leftHip.rotation.x = 0.35;
      bones.leftKnee.rotation.x = 0.65;
      bones.rightHip.rotation.x = 0.35;
      bones.rightKnee.rotation.x = 0.65;
      bones.spine.rotation.x = 0.25;
    }

    // ── 6. Crouch Tactical Stance ─────────────────────────────────────────────
    else if (state === "crouch") {
      bones.pelvis.position.y = 0.68;
      bones.leftHip.rotation.x = 0.55;
      bones.leftKnee.rotation.x = 0.95;
      bones.rightHip.rotation.x = 0.55;
      bones.rightKnee.rotation.x = 0.95;
      bones.spine.rotation.x = 0.30;

      bones.rightShoulder.rotation.x = 1.05;
      bones.leftShoulder.rotation.x = 0.95;
    }

    // ── 7. Reload Animation ───────────────────────────────────────────────────
    if (entity.isReloading) {
      const relProg = entity.reloadTimer / (entity.weapon?.spec?.reloadTime || 2.0);
      // Left arm drops to ammo pouch then comes back up
      if (relProg > 0.5) {
        bones.leftShoulder.rotation.x = 0.20;
        bones.leftShoulder.rotation.y = 0.15;
        bones.leftElbow.rotation.x = -0.40;
      } else {
        bones.leftShoulder.rotation.x = 1.10;
        bones.leftShoulder.rotation.y = 0.30;
        bones.leftElbow.rotation.x = -1.45;
      }
    }

    // ── 8. Emotes & Celebrations ──────────────────────────────────────────────
    if (entity.activeEmote) {
      const emoteT = (2.5 - entity.emoteTimer) * 6.0;

      if (entity.activeEmote === "wave") {
        bones.rightShoulder.rotation.x = 1.85;
        bones.rightShoulder.rotation.z = -0.35;
        bones.rightElbow.rotation.z = Math.sin(emoteT * 2.0) * 0.45;
      } else if (entity.activeEmote === "dance") {
        bones.pelvis.rotation.y = Math.sin(emoteT) * 0.45;
        bones.pelvis.position.y = 0.95 + Math.abs(Math.sin(emoteT * 2)) * 0.08;
        bones.leftShoulder.rotation.x = 1.4 + Math.sin(emoteT) * 0.5;
        bones.rightShoulder.rotation.x = 1.4 - Math.sin(emoteT) * 0.5;
      } else if (entity.activeEmote === "celebration") {
        bones.rightShoulder.rotation.x = 2.1;
        bones.leftShoulder.rotation.x = 2.1;
        bones.pelvis.position.y = 0.95 + Math.abs(Math.sin(emoteT * 1.5)) * 0.15;
      } else if (entity.activeEmote === "thumbs_up") {
        bones.leftShoulder.rotation.x = 1.35;
        bones.leftShoulder.rotation.y = 0.25;
        bones.neck.rotation.x = Math.sin(emoteT * 2.0) * 0.12;
      }
    }

    // ── 9. Defeat Collapse ────────────────────────────────────────────────────
    if (state === "defeat") {
      bones.pelvis.position.y = 0.20;
      bones.pelvis.rotation.x = -Math.PI / 2 + 0.2;
      bones.spine.rotation.x = 0.3;
      bones.leftHip.rotation.x = 0.4;
      bones.rightHip.rotation.x = -0.3;
    }
  }
}

// ── 7. 3D Collision Detection System ──────────────────────────────────────────

class CollisionSystem {
  constructor() {
    this.colliders = []; // Array of AABBs or Cylinders
  }

  addBoxCollider(x, y, z, width, height, depth) {
    this.colliders.push({
      type: "box",
      min: new THREE.Vector3(x - width / 2, y, z - depth / 2),
      max: new THREE.Vector3(x + width / 2, y + height, z + depth / 2)
    });
  }

  addCylinderCollider(x, y, z, radius, height) {
    this.colliders.push({
      type: "cylinder",
      center: new THREE.Vector3(x, y, z),
      radius,
      height
    });
  }

  /**
   * Resolves collision for a moving entity with cylinder radius and height.
   * Returns corrected position.
   */
  resolveEntity(pos, radius = 0.45) {
    for (const c of this.colliders) {
      if (c.type === "box") {
        // Find closest point on AABB to circle center (XZ plane)
        const closestX = Math.max(c.min.x, Math.min(pos.x, c.max.x));
        const closestZ = Math.max(c.min.z, Math.min(pos.z, c.max.z));

        const dx = pos.x - closestX;
        const dz = pos.z - closestZ;
        const distSq = dx * dx + dz * dz;

        if (distSq < radius * radius && pos.y >= c.min.y - 0.2 && pos.y <= c.max.y) {
          const dist = Math.sqrt(distSq);
          if (dist > 0.0001) {
            const overlap = radius - dist;
            pos.x += (dx / dist) * overlap;
            pos.z += (dz / dist) * overlap;
          } else {
            pos.x += radius;
          }
        }
      } else if (c.type === "cylinder") {
        const dx = pos.x - c.center.x;
        const dz = pos.z - c.center.z;
        const distSq = dx * dx + dz * dz;
        const minDist = radius + c.radius;

        if (distSq < minDist * minDist && pos.y >= c.center.y && pos.y <= c.center.y + c.height) {
          const dist = Math.sqrt(distSq);
          if (dist > 0.0001) {
            const overlap = minDist - dist;
            pos.x += (dx / dist) * overlap;
            pos.z += (dz / dist) * overlap;
          }
        }
      }
    }
    return pos;
  }

  /**
   * Raycast check against solid obstacles for bullet ballistics.
   */
  raycast(origin, dir, maxDist) {
    const ray = new THREE.Ray(origin, dir);
    let closestHit = null;
    let minDist = maxDist;

    for (const c of this.colliders) {
      if (c.type === "box") {
        const box = new THREE.Box3(c.min, c.max);
        const hitPoint = ray.intersectBox(box, new THREE.Vector3());
        if (hitPoint) {
          const d = origin.distanceTo(hitPoint);
          if (d < minDist) {
            minDist = d;
            closestHit = hitPoint;
          }
        }
      }
    }
    return closestHit;
  }
}

// ── 8. Environment & Tactical Compound Builder ────────────────────────────────

class EnvironmentBuilder {
  static build(scene, collision) {
    // 1. Terrain Heightmap Ground
    const size = 320;
    const segs = 64;
    const geo = new THREE.PlaneGeometry(size, size, segs, segs);
    geo.rotateX(-Math.PI / 2);

    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      const h = this.getGroundHeight(x, z);
      pos.setY(i, h);
    }
    geo.computeVertexNormals();

    const terrainMat = new THREE.MeshLambertMaterial({ color: 0x4d8c36 });
    const terrain = new THREE.Mesh(geo, terrainMat);
    terrain.receiveShadow = true;
    scene.add(terrain);

    // 2. Concrete Bunkers (3 Military Pillboxes)
    const bunkerCoords = [[-35, -25], [30, 25], [0, 45]];
    const concreteTex = TextureFactory.createConcreteTexture();
    const concreteMat = new THREE.MeshLambertMaterial({ map: concreteTex });

    bunkerCoords.forEach(([bx, bz]) => {
      const by = this.getGroundHeight(bx, bz);
      const bunker = new THREE.Group();

      const bunkerWalls = new THREE.Mesh(new THREE.BoxGeometry(7, 3.2, 5), concreteMat);
      bunkerWalls.position.y = 1.6;
      bunkerWalls.castShadow = true;
      bunkerWalls.receiveShadow = true;
      bunker.add(bunkerWalls);

      // Firing Slit cutout detail
      const slit = new THREE.Mesh(new THREE.BoxGeometry(4.5, 0.45, 5.2), new THREE.MeshBasicMaterial({ color: 0x111111 }));
      slit.position.y = 1.9;
      bunker.add(slit);

      bunker.position.set(bx, by, bz);
      scene.add(bunker);

      collision.addBoxCollider(bx, by, bz, 7, 3.5, 5);
    });

    // 3. Elevated Military Watchtowers (4 Corner Towers)
    const towerCoords = [[-60, -60], [60, -60], [-60, 60], [60, 60]];
    const woodMat = new THREE.MeshLambertMaterial({ color: 0x5d4037 });
    const metalMat = new THREE.MeshLambertMaterial({ color: 0x37474f });

    towerCoords.forEach(([tx, tz]) => {
      const ty = this.getGroundHeight(tx, tz);
      const tower = new THREE.Group();

      // 4 Pillars
      const pillarGeo = new THREE.CylinderGeometry(0.18, 0.22, 9, 6);
      [[-2, -2], [2, -2], [-2, 2], [2, 2]].forEach(([px, pz]) => {
        const pillar = new THREE.Mesh(pillarGeo, woodMat);
        pillar.position.set(px, 4.5, pz);
        pillar.castShadow = true;
        tower.add(pillar);
        collision.addCylinderCollider(tx + px, ty, tz + pz, 0.35, 9);
      });

      // Platform Deck
      const deck = new THREE.Mesh(new THREE.BoxGeometry(5.2, 0.3, 5.2), woodMat);
      deck.position.y = 9.0;
      deck.castShadow = true;
      tower.add(deck);

      // Guard Railings
      const railing = new THREE.Mesh(new THREE.BoxGeometry(5.4, 0.9, 0.15), metalMat);
      railing.position.set(0, 9.55, 2.5);
      tower.add(railing);

      // Roof
      const roof = new THREE.Mesh(new THREE.ConeGeometry(4.2, 1.8, 4), metalMat);
      roof.position.y = 11.5;
      roof.rotation.y = Math.PI / 4;
      roof.castShadow = true;
      tower.add(roof);

      tower.position.set(tx, ty, tz);
      scene.add(tower);
    });

    // 4. Shipping Containers (Tactical maze cover)
    const containerColors = ["#b71c1c", "#0d47a1", "#1b5e20", "#f57f17"];
    const containerCoords = [
      [-15, -10, 0], [-15, 0, 0], [18, -12, Math.PI / 2], [18, 5, Math.PI / 2],
      [-2, -25, 0.4], [10, -28, -0.3], [-25, 20, Math.PI / 4], [25, -35, 0]
    ];

    containerCoords.forEach(([cx, cz, rot], idx) => {
      const cy = this.getGroundHeight(cx, cz);
      const cColor = containerColors[idx % containerColors.length];
      const cTex = TextureFactory.createContainerTexture(cColor);
      const cMat = new THREE.MeshLambertMaterial({ map: cTex });

      const container = new THREE.Mesh(new THREE.BoxGeometry(6.2, 2.6, 2.6), cMat);
      container.position.set(cx, cy + 1.3, cz);
      container.rotation.y = rot;
      container.castShadow = true;
      container.receiveShadow = true;
      scene.add(container);

      collision.addBoxCollider(cx, cy, cz, 6.2, 2.8, 2.6);
    });

    // 5. Sandbag Barricades
    const sandbagMat = new THREE.MeshLambertMaterial({ color: 0xc2a649 });
    const sandbagCoords = [[-6, -12], [6, -12], [0, 20], [-18, 15], [15, 20]];
    sandbagCoords.forEach(([sx, sz]) => {
      const sy = this.getGroundHeight(sx, sz);
      const bag = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.85, 0.6), sandbagMat);
      bag.position.set(sx, sy + 0.42, sz);
      bag.castShadow = true;
      scene.add(bag);
      collision.addBoxCollider(sx, sy, sz, 3.6, 0.9, 0.8);
    });

    // 6. Pine Trees & Broadleaf Foliage
    const trunkGeo = new THREE.CylinderGeometry(0.28, 0.45, 4.0, 6);
    const pineGeo = new THREE.ConeGeometry(2.6, 5.5, 7);
    const trunkMat = new THREE.MeshLambertMaterial({ color: 0x4e342e });
    const leafMat = new THREE.MeshLambertMaterial({ color: 0x2e7d32 });

    for (let i = 0; i < 70; i++) {
      const ang = Math.random() * Math.PI * 2;
      const rad = 14 + Math.random() * 95;
      const tx = Math.cos(ang) * rad;
      const tz = Math.sin(ang) * rad;
      const ty = this.getGroundHeight(tx, tz);

      // Avoid placing trees directly inside buildings or containers
      if (Math.abs(tx) < 20 && Math.abs(tz) < 15) continue;

      const tree = new THREE.Group();
      const trunk = new THREE.Mesh(trunkGeo, trunkMat);
      trunk.position.y = 2.0;
      trunk.castShadow = true;
      tree.add(trunk);

      const leaves = new THREE.Mesh(pineGeo, leafMat);
      leaves.position.y = 5.2;
      leaves.castShadow = true;
      tree.add(leaves);

      tree.position.set(tx, ty, tz);
      scene.add(tree);

      collision.addCylinderCollider(tx, ty, tz, 0.45, 4.5);
    }
  }

  static getGroundHeight(x, z) {
    const dist = Math.sqrt(x * x + z * z);
    let h = Math.sin(x * 0.04) * Math.cos(z * 0.04) * 3.8 +
            Math.sin(x * 0.08 + z * 0.06) * 1.6;
    if (dist > 115) {
      h -= Math.pow((dist - 115) * 0.16, 1.65);
    }
    return Math.max(-5, h);
  }
}

// ── 9. Main 3D Battle Arena Engine ────────────────────────────────────────────

class BattleEngine {
  constructor() {
    this.container = document.getElementById("webgl-container");
    this.scene = null;
    this.camera = null;
    this.renderer = null;

    this.player = null;
    this.bots = [];
    this.projectiles = [];
    this.pickups = [];
    this.towers = [];
    this.airship = null;
    this.collision = new CollisionSystem();

    // Safe Zone State
    this.zoneCenter = new THREE.Vector2(0, 0);
    this.zoneRadius = 140;
    this.zoneTargetRadius = 140;
    this.zoneTimer = 35.0;
    this.zoneStage = 0;
    this.zoneMesh = null;

    // Match Metrics
    this.isPlaying = false;
    this.isPaused = false;
    this.matchDuration = 0;
    this.playerKills = 0;
    this.remainingAlive = 10;

    // Inputs
    this.keys = {};
    this.mouse = { x: 0, y: 0, isLocked: false, isFiring: false };
    this.touch = { moveX: 0, moveY: 0, lookDx: 0, lookDy: 0 };
    this.isCrouched = false;
    this.isADS = false;

    this.clock = new THREE.Clock();
    this.minimapCanvas = document.getElementById("minimap-canvas");
    this.minimapCtx = this.minimapCanvas.getContext("2d");
  }

  init() {
    // 1. Scene & Fog
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x7ec0ee);
    this.scene.fog = new THREE.FogExp2(0x87ceeb, 0.0050);

    // 2. Camera
    const aspect = window.innerWidth / window.innerHeight;
    this.camera = new THREE.PerspectiveCamera(65, aspect, 0.1, 400);

    // 3. Renderer with Mobile Optimization
    const isMobile = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    this.renderer = new THREE.WebGLRenderer({ antialias: !isMobile, powerPreference: "high-performance" });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2.0));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.container.appendChild(this.renderer.domElement);

    // 4. Lighting
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x445533, 0.85);
    this.scene.add(hemiLight);

    const sun = new THREE.DirectionalLight(0xfff5e6, 1.25);
    sun.position.set(65, 110, 45);
    sun.castShadow = true;
    sun.shadow.mapSize.width = isMobile ? 1024 : 2048;
    sun.shadow.mapSize.height = isMobile ? 1024 : 2048;
    sun.shadow.camera.near = 10;
    sun.shadow.camera.far = 260;
    const d = 85;
    sun.shadow.camera.left = -d;
    sun.shadow.camera.right = d;
    sun.shadow.camera.top = d;
    sun.shadow.camera.bottom = -d;
    sun.shadow.bias = -0.0008;
    this.scene.add(sun);

    // 5. Build Environment & Obstacles
    EnvironmentBuilder.build(this.scene, this.collision);
    this.buildSafeZoneCylinder();
    this.buildAirship();

    // 6. Setup Inputs
    this.setupDesktopInputs();
    this.setupMobileInputs();

    window.addEventListener("resize", () => this.onWindowResize());

    // 7. Render Loop
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  buildSafeZoneCylinder() {
    const geo = new THREE.CylinderGeometry(1, 1, 65, 32, 1, true);
    const mat = new THREE.MeshBasicMaterial({
      color: 0x00d2ff,
      transparent: true,
      opacity: 0.26,
      side: THREE.DoubleSide
    });
    this.zoneMesh = new THREE.Mesh(geo, mat);
    this.zoneMesh.position.y = 25;
    this.scene.add(this.zoneMesh);
  }

  buildAirship() {
    const ship = new THREE.Group();
    const hull = new THREE.Mesh(new THREE.SphereGeometry(6, 16, 12), new THREE.MeshLambertMaterial({ color: 0x1a237e }));
    hull.scale.set(2.4, 1.0, 1.0);
    hull.castShadow = true;
    ship.add(hull);

    const cabin = new THREE.Mesh(new THREE.BoxGeometry(5.2, 1.6, 2.2), new THREE.MeshLambertMaterial({ color: 0xf5b018 }));
    cabin.position.y = -6.2;
    ship.add(cabin);

    ship.position.set(0, 48, 0);
    this.scene.add(ship);
    this.airship = ship;
  }

  startMatch() {
    this.isPlaying = true;
    this.isPaused = false;
    this.matchDuration = 0;
    this.playerKills = 0;
    this.remainingAlive = 10;
    this.zoneRadius = 140;
    this.zoneTargetRadius = 140;
    this.zoneTimer = 35.0;
    this.zoneStage = 0;

    // Clean prior entities
    if (this.player && this.player.mesh) this.scene.remove(this.player.mesh.group);
    this.bots.forEach(b => this.scene.remove(b.mesh.group));
    this.bots = [];
    this.projectiles.forEach(p => this.scene.remove(p.mesh));
    this.projectiles = [];
    this.pickups.forEach(pk => this.scene.remove(pk.mesh));
    this.pickups = [];

    // Construct Player Rig
    const pMesh = CharacterFactory.createHumanoid({ isPlayer: true });
    this.scene.add(pMesh.group);

    const activeWName = currentUser.equipped_weapons.AR || "Crimson Blaze";
    const wSpec = WEAPON_CATALOG[activeWName] || WEAPON_CATALOG["Crimson Blaze"];

    this.player = {
      mesh: pMesh,
      pos: new THREE.Vector3(0, 0, 0),
      vel: new THREE.Vector3(0, 0, 0),
      yaw: 0,
      pitch: 0.15,
      hp: 200,
      maxHp: 200,
      shield: 100,
      maxShield: 100,
      isGrounded: true,
      animState: "idle",
      animTime: 0,
      currentSpeed: 0,
      isReloading: false,
      reloadTimer: 0,
      activeEmote: null,
      emoteTimer: 0,
      weapon: {
        spec: wSpec,
        ammoInMag: wSpec.magSize,
        ammoReserve: wSpec.totalAmmo,
        cooldown: 0
      },
      playEmote: (name) => {
        this.player.activeEmote = name;
        this.player.emoteTimer = 2.5;
      }
    };
    this.player.pos.y = EnvironmentBuilder.getGroundHeight(0, 0);

    // Spawn 9 AI Bots
    const botColors = [0x3498db, 0x9b59b6, 0xe67e22, 0x1abc9c, 0xf1c40f, 0x34495e, 0x00d2ff, 0xe74c3c, 0x2ecc71];
    for (let i = 0; i < 9; i++) {
      const bMesh = CharacterFactory.createHumanoid({ isPlayer: false, color: botColors[i] });
      this.scene.add(bMesh.group);

      const ang = (i / 9) * Math.PI * 2 + (Math.random() - 0.5) * 0.4;
      const dist = 38 + Math.random() * 45;
      const bx = Math.cos(ang) * dist;
      const bz = Math.sin(ang) * dist;
      const by = EnvironmentBuilder.getGroundHeight(bx, bz);

      this.bots.push({
        id: i + 1,
        mesh: bMesh,
        pos: new THREE.Vector3(bx, by, bz),
        hp: 120,
        maxHp: 120,
        isAlive: true,
        shootCooldown: 1.0 + Math.random() * 1.5,
        targetPos: new THREE.Vector3(bx, by, bz),
        state: "patrol",
        animState: "walk",
        changeDirTimer: 2.5,
        animTime: Math.random() * 5
      });
    }

    this.spawnPickups();
    this.updateHUD();
  }

  spawnPickups() {
    const medMat = new THREE.MeshLambertMaterial({ color: 0x2ecc71 });
    const vestMat = new THREE.MeshLambertMaterial({ color: 0x3498db });
    const boxGeo = new THREE.BoxGeometry(0.75, 0.75, 0.75);

    for (let i = 0; i < 14; i++) {
      const isMed = i % 2 === 0;
      const mesh = new THREE.Mesh(boxGeo, isMed ? medMat : vestMat);
      const ang = Math.random() * Math.PI * 2;
      const dist = 16 + Math.random() * 80;
      const px = Math.cos(ang) * dist;
      const pz = Math.sin(ang) * dist;
      const py = EnvironmentBuilder.getGroundHeight(px, pz) + 0.5;

      mesh.position.set(px, py, pz);
      this.scene.add(mesh);
      this.pickups.push({ mesh, type: isMed ? "medkit" : "armor", x: px, z: pz });
    }
  }

  // ── Input Setup ─────────────────────────────────────────────────────────────

  setupDesktopInputs() {
    window.addEventListener("keydown", (e) => {
      if (!this.isPlaying) return;
      this.keys[e.code] = true;

      if (e.code === "KeyR") this.reloadPlayerWeapon();
      if (e.code === "Digit1") this.switchSlot(0);
      if (e.code === "Digit2") this.switchSlot(1);
      if (e.code === "Digit3") this.switchSlot(2);
      if (e.code === "KeyC") this.isCrouched = !this.isCrouched;
      if (e.code === "KeyB") this.player.playEmote("dance");
      if (e.code === "Escape") {
        if (!this.isPaused) {
          this.pauseMatch();
          UI.openModal("modal-pause");
        }
      }
    });

    window.addEventListener("keyup", (e) => {
      this.keys[e.code] = false;
    });

    const canvas = this.renderer.domElement;
    canvas.addEventListener("click", () => {
      if (this.isPlaying && !this.isPaused && !this.mouse.isLocked) {
        canvas.requestPointerLock?.();
      }
    });

    document.addEventListener("pointerlockchange", () => {
      this.mouse.isLocked = document.pointerLockElement === canvas;
    });

    window.addEventListener("mousemove", (e) => {
      if (this.mouse.isLocked && this.isPlaying && !this.isPaused) {
        const sens = currentUser.settings.mouse_sens * 0.007;
        this.player.yaw -= e.movementX * sens;
        this.player.pitch = Math.max(-0.65, Math.min(0.70, this.player.pitch + e.movementY * sens));
      }
    });

    window.addEventListener("mousedown", (e) => {
      if (this.isPlaying && !this.isPaused) {
        if (e.button === 0) this.mouse.isFiring = true;
        if (e.button === 2) {
          e.preventDefault();
          this.toggleADS();
        }
      }
    });

    window.addEventListener("mouseup", (e) => {
      if (e.button === 0) this.mouse.isFiring = false;
    });

    window.addEventListener("contextmenu", (e) => {
      if (this.isPlaying) e.preventDefault();
    });
  }

  setupMobileInputs() {
    const joyZone = document.getElementById("joystick-zone");
    const joyStick = document.getElementById("joystick-stick");
    let joyTouchId = null;
    let joyOrigin = { x: 0, y: 0 };

    joyZone.addEventListener("touchstart", (e) => {
      e.preventDefault();
      const t = e.changedTouches[0];
      joyTouchId = t.identifier;
      const rect = joyZone.getBoundingClientRect();
      joyOrigin = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    }, { passive: false });

    joyZone.addEventListener("touchmove", (e) => {
      e.preventDefault();
      for (let i = 0; i < e.changedTouches.length; i++) {
        const t = e.changedTouches[i];
        if (t.identifier === joyTouchId) {
          const dx = t.clientX - joyOrigin.x;
          const dy = t.clientY - joyOrigin.y;
          const dist = Math.min(45, Math.hypot(dx, dy));
          const angle = Math.atan2(dy, dx);

          this.touch.moveX = (Math.cos(angle) * dist) / 45;
          this.touch.moveY = (Math.sin(angle) * dist) / 45;

          joyStick.style.transform = `translate(${Math.cos(angle) * dist}px, ${Math.sin(angle) * dist}px)`;
        }
      }
    }, { passive: false });

    const resetJoy = (e) => {
      for (let i = 0; i < e.changedTouches.length; i++) {
        if (e.changedTouches[i].identifier === joyTouchId) {
          joyTouchId = null;
          this.touch.moveX = 0;
          this.touch.moveY = 0;
          joyStick.style.transform = "translate(0px, 0px)";
        }
      }
    };
    joyZone.addEventListener("touchend", resetJoy);
    joyZone.addEventListener("touchcancel", resetJoy);

    // Touch Swipe Camera Look Zone
    const lookZone = document.getElementById("touch-look-zone");
    let lookTouchId = null;
    let lastLook = { x: 0, y: 0 };

    lookZone.addEventListener("touchstart", (e) => {
      e.preventDefault();
      const t = e.changedTouches[0];
      lookTouchId = t.identifier;
      lastLook = { x: t.clientX, y: t.clientY };
    }, { passive: false });

    lookZone.addEventListener("touchmove", (e) => {
      e.preventDefault();
      for (let i = 0; i < e.changedTouches.length; i++) {
        const t = e.changedTouches[i];
        if (t.identifier === lookTouchId) {
          const dx = t.clientX - lastLook.x;
          const dy = t.clientY - lastLook.y;
          lastLook = { x: t.clientX, y: t.clientY };

          const sens = currentUser.settings.mouse_sens * 0.009;
          this.player.yaw -= dx * sens;
          this.player.pitch = Math.max(-0.65, Math.min(0.70, this.player.pitch + dy * sens));
        }
      }
    }, { passive: false });

    lookZone.addEventListener("touchend", (e) => {
      for (let i = 0; i < e.changedTouches.length; i++) {
        if (e.changedTouches[i].identifier === lookTouchId) lookTouchId = null;
      }
    });

    // Mobile Action Buttons
    const btnFire = document.getElementById("btn-touch-fire");
    btnFire.addEventListener("touchstart", (e) => { e.preventDefault(); this.mouse.isFiring = true; });
    btnFire.addEventListener("touchend", (e) => { e.preventDefault(); this.mouse.isFiring = false; });

    document.getElementById("btn-touch-jump").onclick = () => this.playerJump();
    document.getElementById("btn-touch-crouch").onclick = () => { this.isCrouched = !this.isCrouched; };
    document.getElementById("btn-touch-reload").onclick = () => this.reloadPlayerWeapon();
    document.getElementById("btn-touch-emote").onclick = () => this.player.playEmote("dance");
    document.getElementById("btn-touch-scope").onclick = () => this.toggleADS();

    // Mobile Weapon Slot Buttons
    document.getElementById("btn-touch-slot-0").onclick = () => this.switchSlot(0);
    document.getElementById("btn-touch-slot-1").onclick = () => this.switchSlot(1);
    document.getElementById("btn-touch-slot-2").onclick = () => this.switchSlot(2);

    document.getElementById("slot-0").onclick = () => this.switchSlot(0);
    document.getElementById("slot-1").onclick = () => this.switchSlot(1);
    document.getElementById("slot-2").onclick = () => this.switchSlot(2);
  }

  toggleADS() {
    this.isADS = !this.isADS;
    this.camera.fov = this.isADS ? 32 : 65;
    this.camera.updateProjectionMatrix();
  }

  switchSlot(slotIdx) {
    document.querySelectorAll(".slot-tab").forEach((t, i) => t.classList.toggle("active", i === slotIdx));
    document.querySelectorAll(".touch-slot-btn").forEach((t, i) => t.classList.toggle("active", i === slotIdx));

    sounds.playClick();
    let cat = "AR";
    if (slotIdx === 1) cat = "SMG";
    if (slotIdx === 2) cat = "Pistol";

    const wName = currentUser.equipped_weapons[cat] || (slotIdx === 1 ? "Cobra MP5" : "Tactical G18");
    const spec = WEAPON_CATALOG[wName] || WEAPON_CATALOG["Crimson Blaze"];

    this.player.weapon = {
      spec,
      ammoInMag: spec.magSize,
      ammoReserve: spec.totalAmmo,
      cooldown: 0
    };
    this.player.isReloading = false;

    // Update 3D weapon model in hand
    CharacterFactory.buildWeaponMesh(this.player.mesh.weaponGroup, wName);
    this.updateHUD();
  }

  playerJump() {
    if (this.player && this.player.isGrounded) {
      this.player.vel.y = 8.8;
      this.player.isGrounded = false;
      this.player.animState = "jump";
    }
  }

  reloadPlayerWeapon() {
    const p = this.player;
    const w = p.weapon;
    if (p.isReloading || w.ammoInMag >= w.spec.magSize || w.ammoReserve <= 0) return;
    p.isReloading = true;
    p.reloadTimer = w.spec.reloadTime;
    sounds.playReload();
    document.getElementById("hud-reload-bar").classList.remove("hidden");
  }

  // ── Physics, Combat & AI Updates ──────────────────────────────────────────

  update(dt) {
    if (!this.isPlaying || this.isPaused) return;
    this.matchDuration += dt;

    this.updateSafeZone(dt);
    this.updatePlayerMovement(dt);
    this.updateCombat(dt);
    this.updateBots(dt);
    this.updateAtmosphere(dt);
    this.updateCamera();
    this.updateHUD();
    this.drawMinimap();
  }

  updateSafeZone(dt) {
    this.zoneTimer -= dt;
    if (this.zoneTimer <= 0) {
      this.zoneStage += 1;
      this.zoneTimer = 35.0;
      this.zoneTargetRadius = Math.max(16, this.zoneRadius * 0.65);
    }

    if (this.zoneRadius > this.zoneTargetRadius) {
      this.zoneRadius = Math.max(this.zoneTargetRadius, this.zoneRadius - dt * 3.8);
    }

    this.zoneMesh.scale.set(this.zoneRadius, 1, this.zoneRadius);
    this.zoneMesh.position.set(this.zoneCenter.x, 25, this.zoneCenter.y);

    const pDist = Math.hypot(this.player.pos.x - this.zoneCenter.x, this.player.pos.z - this.zoneCenter.y);
    if (pDist > this.zoneRadius) {
      this.damagePlayer(dt * 7.5);
      document.getElementById("hud-zone-timer").innerText = "⚠️ DANGER: OUTSIDE SAFE ZONE!";
    } else {
      document.getElementById("hud-zone-timer").innerText = `⚠️ SAFE ZONE: ${Math.ceil(this.zoneTimer)}s`;
    }
  }

  updatePlayerMovement(dt) {
    const p = this.player;

    let moveForward = 0;
    let moveRight = 0;

    if (this.keys["KeyW"]) moveForward += 1;
    if (this.keys["KeyS"]) moveForward -= 1;
    if (this.keys["KeyA"]) moveRight -= 1;
    if (this.keys["KeyD"]) moveRight += 1;

    moveForward -= this.touch.moveY;
    moveRight += this.touch.moveX;

    const isSprinting = (this.keys["ShiftLeft"] || this.keys["ShiftRight"]) && !this.isCrouched;
    const baseSpeed = this.isCrouched ? 4.0 : (isSprinting ? 12.0 : 7.5);

    const cosY = Math.cos(p.yaw);
    const sinY = Math.sin(p.yaw);
    const fwd = new THREE.Vector3(-sinY, 0, -cosY);
    const rgt = new THREE.Vector3(cosY, 0, -sinY);

    const moveDir = new THREE.Vector3();
    moveDir.addScaledVector(fwd, moveForward);
    moveDir.addScaledVector(rgt, moveRight);

    const isMoving = moveDir.lengthSq() > 0.001;
    if (isMoving) {
      moveDir.normalize();
      p.pos.x += moveDir.x * baseSpeed * dt;
      p.pos.z += moveDir.z * baseSpeed * dt;
      p.activeEmote = null;

      // 3D Obstacle & Wall Collision Resolution
      this.collision.resolveEntity(p.pos, 0.45);
    }

    // Vertical Jump & Gravity
    if (this.keys["Space"]) this.playerJump();

    p.vel.y -= 22.0 * dt;
    p.pos.y += p.vel.y * dt;

    const groundY = EnvironmentBuilder.getGroundHeight(p.pos.x, p.pos.z);
    if (p.pos.y <= groundY) {
      if (!p.isGrounded && p.vel.y < -5.0) {
        p.animState = "landing";
        setTimeout(() => { if (p.isGrounded) p.animState = isMoving ? (isSprinting ? "run" : "walk") : "idle"; }, 180);
      }
      p.pos.y = groundY;
      p.vel.y = 0;
      p.isGrounded = true;
    }

    // Update Animation State
    if (p.isGrounded && p.animState !== "landing") {
      if (this.isCrouched) {
        p.animState = "crouch";
      } else if (isMoving) {
        p.animState = isSprinting ? "sprint" : "walk";
      } else {
        p.animState = "idle";
      }
    }

    p.mesh.group.position.copy(p.pos);
    p.mesh.group.rotation.y = p.yaw;

    // Emote Timer
    if (p.activeEmote) {
      p.emoteTimer -= dt;
      if (p.emoteTimer <= 0) p.activeEmote = null;
    }

    // Update Skeletal Animations
    CharacterAnimator.update(p, dt);
  }

  updateCombat(dt) {
    const p = this.player;
    const w = p.weapon;

    if (w.cooldown > 0) w.cooldown -= dt;

    if (p.isReloading) {
      p.reloadTimer -= dt;
      const fillEl = document.getElementById("hud-reload-fill");
      const prog = Math.min(100, Math.floor((1 - p.reloadTimer / w.spec.reloadTime) * 100));
      if (fillEl) fillEl.style.width = `${prog}%`;

      if (p.reloadTimer <= 0) {
        p.isReloading = false;
        const needed = w.spec.magSize - w.ammoInMag;
        const transfer = Math.min(needed, w.ammoReserve);
        w.ammoInMag += transfer;
        w.ammoReserve -= transfer;
        document.getElementById("hud-reload-bar").classList.add("hidden");
      }
    }

    if (this.mouse.isFiring && w.cooldown <= 0 && !p.isReloading) {
      if (w.ammoInMag > 0) {
        this.firePlayerWeapon();
      } else {
        this.reloadPlayerWeapon();
      }
    }

    // Update Projectiles & Ray Collision
    for (let i = this.projectiles.length - 1; i >= 0; i--) {
      const prj = this.projectiles[i];
      const prevPos = prj.pos.clone();
      prj.pos.addScaledVector(prj.vel, dt);
      prj.mesh.position.copy(prj.pos);
      prj.life -= dt;

      // Obstacle Ray Collision
      const rayDir = prj.vel.clone().normalize();
      const stepDist = prevPos.distanceTo(prj.pos);
      const hitWall = this.collision.raycast(prevPos, rayDir, stepDist);

      if (hitWall || prj.pos.y <= EnvironmentBuilder.getGroundHeight(prj.pos.x, prj.pos.z)) {
        this.scene.remove(prj.mesh);
        this.projectiles.splice(i, 1);
        continue;
      }

      // Check Hits
      if (prj.isPlayer) {
        let hit = false;
        for (const b of this.bots) {
          if (!b.isAlive) continue;
          const botChest = b.pos.clone().add(new THREE.Vector3(0, 1.3, 0));
          if (prj.pos.distanceTo(botChest) < 1.35) {
            // Check Headshot
            const isHeadshot = prj.pos.y > b.pos.y + 1.8;
            const finalDmg = Math.round(prj.damage * (isHeadshot ? 1.5 : 1.0));
            b.hp -= finalDmg;

            sounds.playHit();
            this.showHitmarker(finalDmg, isHeadshot);

            if (b.hp <= 0) {
              b.isAlive = false;
              b.animState = "defeat";
              this.playerKills += 1;
              this.remainingAlive -= 1;
              this.addKillfeed(`🎯 [${currentUser.username}] 💥 ${w.spec.name} ➔ Rival_Bot_${b.id}`, true);
              UI.showToast(`🎯 ELIMINATED RIVAL BOT! (${this.remainingAlive} ALIVE)`);
              if (this.remainingAlive <= 1) {
                this.endMatch(true, this.playerKills, Math.floor(this.matchDuration));
              }
            }
            hit = true;
            break;
          }
        }
        if (hit) {
          this.scene.remove(prj.mesh);
          this.projectiles.splice(i, 1);
          continue;
        }
      } else {
        // Bot tag hit player
        const playerChest = p.pos.clone().add(new THREE.Vector3(0, 1.3, 0));
        if (prj.pos.distanceTo(playerChest) < 1.25) {
          this.damagePlayer(prj.damage);
          sounds.playHit();
          this.scene.remove(prj.mesh);
          this.projectiles.splice(i, 1);
          continue;
        }
      }

      if (prj.life <= 0) {
        this.scene.remove(prj.mesh);
        this.projectiles.splice(i, 1);
      }
    }
  }

  firePlayerWeapon() {
    const p = this.player;
    const w = p.weapon;
    w.ammoInMag -= 1;
    w.cooldown = w.spec.fireRate;

    sounds.playShot(w.spec.category);

    const cosY = Math.cos(p.yaw);
    const sinY = Math.sin(p.yaw);
    const cosP = Math.cos(p.pitch);
    const sinP = Math.sin(p.pitch);

    const baseDir = new THREE.Vector3(-sinY * cosP, -sinP, -cosY * cosP).normalize();
    const spawnPos = p.pos.clone().add(new THREE.Vector3(0, 1.45, 0)).addScaledVector(baseDir, 1.1);

    for (let pellet = 0; pellet < w.spec.pellets; pellet++) {
      const spread = w.spec.spread * (this.isADS ? 0.45 : 1.0);
      const spreadDir = baseDir.clone().add(new THREE.Vector3(
        (Math.random() - 0.5) * spread,
        (Math.random() - 0.5) * spread,
        (Math.random() - 0.5) * spread
      )).normalize();

      const pGeo = new THREE.SphereGeometry(w.spec.category === "Sniper" ? 0.14 : 0.09, 6, 6);
      const pMat = new THREE.MeshBasicMaterial({ color: w.spec.color });
      const pMesh = new THREE.Mesh(pGeo, pMat);
      pMesh.position.copy(spawnPos);
      this.scene.add(pMesh);

      this.projectiles.push({
        mesh: pMesh,
        pos: spawnPos.clone(),
        vel: spreadDir.multiplyScalar(w.spec.category === "Sniper" ? 140 : 85),
        damage: w.spec.damage,
        life: 1.8,
        isPlayer: true
      });
    }

    // Dynamic crosshair recoil
    const ch = document.getElementById("crosshair");
    if (ch) {
      ch.style.transform = "scale(1.4)";
      setTimeout(() => { ch.style.transform = "scale(1.0)"; }, 90);
    }

    if (w.ammoInMag <= 0 && w.ammoReserve > 0) {
      this.reloadPlayerWeapon();
    }
  }

  damagePlayer(dmg) {
    const p = this.player;
    if (p.shield > 0) {
      const absorb = Math.min(p.shield, dmg);
      p.shield -= absorb;
      dmg -= absorb;
    }
    p.hp -= dmg;

    // Low HP pulsing vignette alert
    const vig = document.getElementById("low-hp-vignette");
    if (vig) {
      if (p.hp < 60 && p.hp > 0) vig.classList.remove("hidden");
      else vig.classList.add("hidden");
    }

    if (p.hp <= 0) {
      p.hp = 0;
      p.animState = "defeat";
      if (vig) vig.classList.add("hidden");
      this.addKillfeed(`💀 ${currentUser.username} was eliminated!`, false);
      this.endMatch(false, this.playerKills, Math.floor(this.matchDuration));
    }
  }

  addKillfeed(text, isPlayerKill = false) {
    const container = document.getElementById("killfeed-container");
    if (!container) return;
    const entry = document.createElement("div");
    entry.className = `killfeed-entry ${isPlayerKill ? "player-kill" : ""}`;
    entry.innerText = text;
    container.appendChild(entry);
    if (container.children.length > 5) {
      container.removeChild(container.children[0]);
    }
    setTimeout(() => {
      if (entry.parentNode) entry.parentNode.removeChild(entry);
    }, 4500);
  }

  showHitmarker(dmg, isHeadshot) {
    const hm = document.getElementById("hitmarker");
    if (hm) {
      hm.classList.remove("hidden");
      setTimeout(() => hm.classList.add("hidden"), 180);
    }
    const pop = document.createElement("div");
    pop.className = "damage-num";
    pop.innerText = `${isHeadshot ? "CRIT! " : ""}-${dmg}`;
    pop.style.color = isHeadshot ? "#e62020" : "#f5b018";
    pop.style.left = `${window.innerWidth / 2 + (Math.random() - 0.5) * 60}px`;
    pop.style.top = `${window.innerHeight / 2 - 30 + (Math.random() - 0.5) * 30}px`;
    document.getElementById("damage-popup-container").appendChild(pop);
    setTimeout(() => pop.remove(), 700);
  }

  updateBots(dt) {
    const p = this.player;
    this.bots.forEach(b => {
      if (!b.isAlive) {
        CharacterAnimator.update(b, dt);
        return;
      }

      const toPlayer = p.pos.clone().sub(b.pos);
      const dist = toPlayer.length();

      if (dist < 45) {
        b.state = dist < 12 ? "strafe" : "chase";
        b.animState = "run";
      } else {
        b.state = "patrol";
        b.animState = "walk";
      }

      if (b.state === "patrol") {
        b.changeDirTimer -= dt;
        if (b.changeDirTimer <= 0) {
          b.changeDirTimer = 3.0 + Math.random() * 2;
          const ang = Math.random() * Math.PI * 2;
          b.targetPos.set(b.pos.x + Math.cos(ang) * 16, 0, b.pos.z + Math.sin(ang) * 16);
        }
        const moveDir = b.targetPos.clone().sub(b.pos).setY(0).normalize();
        b.pos.addScaledVector(moveDir, 4.0 * dt);
      } else if (b.state === "chase") {
        const moveDir = toPlayer.clone().setY(0).normalize();
        b.pos.addScaledVector(moveDir, 5.8 * dt);
        b.mesh.group.rotation.y = Math.atan2(-moveDir.x, -moveDir.z);
      } else if (b.state === "strafe") {
        const perp = new THREE.Vector3(-toPlayer.z, 0, toPlayer.x).normalize();
        b.pos.addScaledVector(perp, 4.8 * dt);
        b.mesh.group.rotation.y = Math.atan2(-toPlayer.x, -toPlayer.z);
      }

      // Obstacle collision resolution for bots
      this.collision.resolveEntity(b.pos, 0.45);
      b.pos.y = EnvironmentBuilder.getGroundHeight(b.pos.x, b.pos.z);
      b.mesh.group.position.copy(b.pos);

      // Skeletal Animation Update
      CharacterAnimator.update(b, dt);

      // Firing Paint/Energy tags
      b.shootCooldown -= dt;
      if (dist < 42 && b.shootCooldown <= 0) {
        b.shootCooldown = 1.2 + Math.random() * 1.0;
        const shotDir = toPlayer.clone().add(new THREE.Vector3(
          (Math.random() - 0.5) * 2.5,
          0.8 + (Math.random() - 0.5) * 1.5,
          (Math.random() - 0.5) * 2.5
        )).normalize();

        const pGeo = new THREE.SphereGeometry(0.12, 6, 6);
        const pMat = new THREE.MeshBasicMaterial({ color: 0x00d2ff });
        const pMesh = new THREE.Mesh(pGeo, pMat);
        pMesh.position.copy(b.pos.clone().add(new THREE.Vector3(0, 1.45, 0)));
        this.scene.add(pMesh);

        this.projectiles.push({
          mesh: pMesh,
          pos: pMesh.position.clone(),
          vel: shotDir.multiplyScalar(55),
          damage: 15,
          life: 1.5,
          isPlayer: false
        });
      }
    });
  }

  updateAtmosphere(dt) {
    if (this.airship) {
      const t = this.matchDuration * 0.08;
      this.airship.position.x = Math.cos(t) * 75;
      this.airship.position.z = Math.sin(t) * 75;
      this.airship.rotation.y = -t + Math.PI / 2;
    }

    this.pickups.forEach((pk, i) => {
      pk.mesh.rotation.y += dt * 1.5;
      pk.mesh.position.y = EnvironmentBuilder.getGroundHeight(pk.x, pk.z) + 0.6 + Math.sin(this.matchDuration * 3.0 + i) * 0.15;

      if (Math.hypot(this.player.pos.x - pk.x, this.player.pos.z - pk.z) < 2.2) {
        if (pk.type === "medkit") {
          this.player.hp = Math.min(this.player.maxHp, this.player.hp + 75);
          UI.showToast("+75 HP Recovered!");
        } else {
          this.player.shield = Math.min(this.player.maxShield, this.player.shield + 50);
          UI.showToast("+50 Tactical Armor Restored!");
        }
        sounds.playClick();
        this.scene.remove(pk.mesh);
        this.pickups.splice(i, 1);
      }
    });
  }

  updateCamera() {
    const p = this.player;
    const dist = this.isADS ? 2.8 : 5.2;
    const height = this.isCrouched ? 1.7 : 2.4;

    const cosY = Math.cos(p.yaw);
    const sinY = Math.sin(p.yaw);
    const cosP = Math.cos(p.pitch);
    const sinP = Math.sin(p.pitch);

    const camOffset = new THREE.Vector3(
      sinY * cosP * dist,
      sinP * dist + height,
      cosY * cosP * dist
    );

    this.camera.position.copy(p.pos).add(camOffset);
    const lookTarget = p.pos.clone().add(new THREE.Vector3(0, this.isCrouched ? 1.1 : 1.5, 0));
    this.camera.lookAt(lookTarget);
  }

  updateHUD() {
    const p = this.player;
    if (!p) return;

    const hpPct = Math.max(0, Math.min(100, (p.hp / p.maxHp) * 100));
    const shPct = Math.max(0, Math.min(100, (p.shield / p.maxShield) * 100));
    document.getElementById("hud-hp-fill").style.width = `${hpPct}%`;
    document.getElementById("hud-hp-text").innerText = `${Math.ceil(p.hp)}/${p.maxHp}`;
    document.getElementById("hud-shield-fill").style.width = `${shPct}%`;
    document.getElementById("hud-shield-text").innerText = `${Math.ceil(p.shield)}/${p.maxShield}`;

    document.getElementById("hud-alive-count").innerText = `${this.remainingAlive}`;
    document.getElementById("hud-kill-count").innerText = `${this.playerKills}`;

    const w = p.weapon;
    document.getElementById("hud-weapon-name").innerText = w.spec.name;
    document.getElementById("hud-weapon-cat").innerText = w.spec.category.toUpperCase();
    document.getElementById("hud-ammo-cur").innerText = `${w.ammoInMag}`;
    document.getElementById("hud-ammo-res").innerText = `${w.ammoReserve}`;

    const deg = Math.round(((-p.yaw * 180 / Math.PI) % 360 + 360) % 360);
    const tape = document.getElementById("compass-tape");
    if (tape) tape.style.transform = `translateX(-${(deg / 360) * 200}px)`;
  }

  drawMinimap() {
    const ctx = this.minimapCtx;
    const w = this.minimapCanvas.width;
    const h = this.minimapCanvas.height;
    ctx.clearRect(0, 0, w, h);

    const cx = w / 2;
    const cy = h / 2;
    const scale = 0.55;

    // Safe zone circle
    const szDx = (this.zoneCenter.x - this.player.pos.x) * scale;
    const szDz = (this.zoneCenter.y - this.player.pos.z) * scale;
    ctx.strokeStyle = "#00d2ff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx + szDx, cy + szDz, this.zoneRadius * scale, 0, Math.PI * 2);
    ctx.stroke();

    // Enemy Bots
    this.bots.forEach(b => {
      if (!b.isAlive) return;
      const bx = (b.pos.x - this.player.pos.x) * scale;
      const bz = (b.pos.z - this.player.pos.z) * scale;
      if (Math.hypot(bx, bz) < w / 2 - 4) {
        ctx.fillStyle = "#e62020";
        ctx.beginPath();
        ctx.arc(cx + bx, cy + bz, 3.5, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    // Player Direction Arrow
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(-this.player.yaw);
    ctx.fillStyle = "#f5b018";
    ctx.beginPath();
    ctx.moveTo(0, -6);
    ctx.lineTo(4, 5);
    ctx.lineTo(-4, 5);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  pauseMatch() {
    this.isPaused = true;
    if (document.exitPointerLock) document.exitPointerLock();
  }

  resumeMatch() {
    this.isPaused = false;
  }

  async endMatch(won, kills, duration) {
    this.isPlaying = false;
    if (document.exitPointerLock) document.exitPointerLock();

    if (won) sounds.playBooyah();

    document.getElementById("results-title").innerText = won ? "BOOYAH!" : "ELIMINATED";
    document.getElementById("results-subtitle").innerText = won ? "#1 VICTORY ROYALE" : "BATTLE SURVIVED";
    document.getElementById("res-kills").innerText = `${kills}`;

    const mins = Math.floor(duration / 60);
    const secs = duration % 60;
    document.getElementById("res-time").innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    document.getElementById("res-score").innerText = `+${kills * 25 + (won ? 80 : 20)}`;

    const matchRes = await API.recordMatch(won, kills, kills * 25 + (won ? 80 : 20), duration);

    document.getElementById("res-coins").innerText = `${matchRes.coins_earned || 250}`;
    document.getElementById("res-xp").innerText = `${matchRes.xp_earned || 150}`;
    document.getElementById("res-diamonds").innerText = `${matchRes.diamonds_earned || (won ? 5 : 1)}`;
    document.getElementById("res-rank-name").innerText = currentUser.rank_name;
    document.getElementById("res-rank-points").innerText = `+${matchRes.rank_points_earned || 35} RP`;

    UI.showScreen("screen-results");
  }

  onWindowResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  animate() {
    requestAnimationFrame(this.animate);
    const dt = Math.min(0.05, this.clock.getDelta());
    this.update(dt);
    this.renderer.render(this.scene, this.camera);
  }
}

// ── 10. UI & Screen Transition Controller ─────────────────────────────────────

const UI = {
  currentScreen: "screen-splash",
  activeModal: null,
  activeArmoryCategory: "AR",
  selectedArmoryWeapon: "Crimson Blaze",

  showScreen(screenId) {
    document.querySelectorAll(".screen").forEach(s => {
      s.classList.remove("active");
      s.classList.add("hidden");
    });
    const el = document.getElementById(screenId);
    if (el) {
      el.classList.remove("hidden");
      el.classList.add("active");
      this.currentScreen = screenId;
    }
  },

  openModal(modalId) {
    sounds.playClick();
    const cont = document.getElementById("modal-container");
    cont.classList.remove("hidden");
    document.querySelectorAll(".modal-dialog").forEach(m => m.classList.add("hidden"));
    const el = document.getElementById(modalId);
    if (el) el.classList.remove("hidden");
    this.activeModal = modalId;
  },

  closeModal() {
    sounds.playClick();
    const cont = document.getElementById("modal-container");
    cont.classList.add("hidden");
    document.querySelectorAll(".modal-dialog").forEach(m => m.classList.add("hidden"));
    this.activeModal = null;
  },

  showToast(msg) {
    const t = document.getElementById("toast");
    t.innerText = msg;
    t.classList.remove("hidden");
    setTimeout(() => t.classList.add("hidden"), 2500);
  },

  updateLobbyUI() {
    document.getElementById("lobby-player-name").innerText = currentUser.username;
    document.getElementById("lobby-level").innerText = `Lv.${currentUser.level}`;
    document.getElementById("lobby-coins").innerText = currentUser.coins.toLocaleString();
    document.getElementById("lobby-diamonds").innerText = currentUser.diamonds.toLocaleString();
    document.getElementById("lobby-rank-name").innerText = currentUser.rank_name;
    document.getElementById("lobby-rank-score").innerText = `★ ${currentUser.rank_score}`;

    const pill = document.getElementById("lobby-guest-pill");
    if (currentUser.is_guest) {
      pill.style.display = "inline-block";
      pill.innerText = "GUEST";
    } else {
      pill.style.display = "none";
    }

    const tier = RANK_TIERS.find(t => t.name === currentUser.rank_name) || RANK_TIERS[0];
    document.getElementById("lobby-rank-badge").src = tier.badge;

    const xpPercent = Math.min(100, Math.floor((currentUser.xp / currentUser.xp_next) * 100));
    document.getElementById("lobby-xp-fill").style.width = `${xpPercent}%`;

    const dot = document.getElementById("mail-dot");
    if (dot) dot.style.display = currentUser.mail_claimed ? "none" : "block";

    const avatar = document.getElementById("lobby-avatar");
    if (avatar) {
      avatar.src = currentUser.selected_character === "Maya" ? "/assets/char_female.png" : "/assets/char_male.png";
    }
  },

  renderArmory(category = "AR") {
    this.activeArmoryCategory = category;
    const listEl = document.getElementById("armory-weapon-list");
    listEl.innerHTML = "";

    const weaponsInCat = Object.values(WEAPON_CATALOG).filter(w => w.category === category);
    weaponsInCat.forEach(w => {
      const isEquipped = currentUser.equipped_weapons[category] === w.name;
      const isSelected = this.selectedArmoryWeapon === w.name;

      const card = document.createElement("div");
      card.className = `weapon-card-item ${isSelected ? "selected" : ""}`;
      card.innerHTML = `
        <span class="w-name" style="color:#${w.color.toString(16).padStart(6, '0')}">${w.name}</span>
        ${isEquipped ? '<span class="w-equipped-tag">EQUIPPED</span>' : ''}
      `;
      card.onclick = () => {
        this.selectedArmoryWeapon = w.name;
        sounds.playClick();
        this.renderArmory(category);
      };
      listEl.appendChild(card);
    });

    const sel = WEAPON_CATALOG[this.selectedArmoryWeapon] || weaponsInCat[0];
    if (sel) {
      document.getElementById("arm-detail-name").innerText = sel.name;
      document.getElementById("arm-detail-tier").innerText = `${sel.tier} ${sel.category.toUpperCase()}`;
      document.getElementById("arm-detail-desc").innerText = sel.desc;

      document.getElementById("stat-bar-damage").style.width = `${Math.min(100, sel.damage * 0.9)}%`;
      document.getElementById("stat-bar-rate").style.width = `${Math.min(100, (1.0 / sel.fireRate) * 7)}%`;
      document.getElementById("stat-bar-range").style.width = `${Math.min(100, sel.range * 0.8)}%`;
      document.getElementById("stat-bar-acc").style.width = `${sel.accuracy}%`;

      const btnEquip = document.getElementById("btn-equip-weapon");
      const already = currentUser.equipped_weapons[sel.category] === sel.name;
      btnEquip.innerText = already ? "ALREADY EQUIPPED" : "EQUIP TO LOADOUT";
      btnEquip.style.opacity = already ? "0.6" : "1.0";
    }
  },

  startMatchWithLoading(engine) {
    this.showScreen("screen-loading");
    sounds.playClick();

    const tips = [
      "Headshots inflict 1.5x critical tag damage! Aim carefully when engaging distant rivals.",
      "Stay inside the blue safe zone boundary to avoid toxic storm damage.",
      "Collect medkits and tactical vests scattered in compounds to restore armor.",
      "Use shipping containers and watchtower ladders for tactical high ground."
    ];
    document.getElementById("loading-tip-text").innerText = tips[Math.floor(Math.random() * tips.length)];

    let prog = 10;
    const bar = document.getElementById("loading-bar-fill");
    const pct = document.getElementById("loading-pct-text");
    const status = document.getElementById("loading-status-text");

    const timer = setInterval(() => {
      prog += Math.floor(Math.random() * 22) + 12;
      if (prog >= 100) {
        prog = 100;
        clearInterval(timer);
        bar.style.width = "100%";
        pct.innerText = "100%";
        status.innerText = "WARM UP COMPLETE! DEPLOYING NOW...";

        setTimeout(() => {
          this.showScreen("screen-game");
          engine.startMatch();
        }, 350);
      } else {
        bar.style.width = `${prog}%`;
        pct.innerText = `${prog}%`;
        if (prog > 60) status.innerText = "CONFIGURING 3D COMBATANTS & SAFE ZONE...";
        else if (prog > 30) status.innerText = "LOADING TACTICAL WEAPON ARMORY...";
      }
    }, 120);
  },

  initEventListeners(engine) {
    // Quick Bar Utilities (Guide, Audio, Fullscreen)
    const btnGuide = document.getElementById("btn-quick-guide");
    if (btnGuide) btnGuide.onclick = () => this.openModal("modal-guide");

    const btnAudio = document.getElementById("btn-quick-audio");
    if (btnAudio) {
      btnAudio.onclick = () => {
        sounds.init();
        const icon = document.getElementById("audio-btn-icon");
        if (currentUser.settings.vol_master > 0) {
          currentUser.settings.vol_master = 0;
          if (icon) icon.innerText = "🔇 SOUND: OFF";
          this.showToast("Sound Muted");
        } else {
          currentUser.settings.vol_master = 0.7;
          if (icon) icon.innerText = "🔊 SOUND: ON";
          sounds.playClick();
          this.showToast("Sound Enabled");
        }
        sounds.updateVolumes();
      };
    }

    const btnFs = document.getElementById("btn-quick-fullscreen");
    if (btnFs) {
      btnFs.onclick = () => {
        sounds.playClick();
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen?.().catch(() => {});
        } else {
          document.exitFullscreen?.().catch(() => {});
        }
      };
    }

    document.getElementById("btn-tap-continue").onclick = () => {
      sounds.init();
      sounds.playClick();
      this.showScreen("screen-login");
    };

    const tabGuest = document.getElementById("tab-guest");
    const tabLogin = document.getElementById("tab-login");
    const tabReg = document.getElementById("tab-register");

    const viewGuest = document.getElementById("view-guest");
    const viewSignin = document.getElementById("view-signin");
    const viewReg = document.getElementById("view-register");

    tabGuest.onclick = () => {
      sounds.playClick();
      [tabGuest, tabLogin, tabReg].forEach(t => t.classList.remove("active"));
      tabGuest.classList.add("active");
      viewGuest.classList.remove("hidden");
      viewSignin.classList.add("hidden");
      viewReg.classList.add("hidden");
    };

    tabLogin.onclick = () => {
      sounds.playClick();
      [tabGuest, tabLogin, tabReg].forEach(t => t.classList.remove("active"));
      tabLogin.classList.add("active");
      viewSignin.classList.remove("hidden");
      viewGuest.classList.add("hidden");
      viewReg.classList.add("hidden");
    };

    tabReg.onclick = () => {
      sounds.playClick();
      [tabGuest, tabLogin, tabReg].forEach(t => t.classList.remove("active"));
      tabReg.classList.add("active");
      viewReg.classList.remove("hidden");
      viewGuest.classList.add("hidden");
      viewSignin.classList.add("hidden");
    };

    document.getElementById("btn-guest-play").onclick = async () => {
      sounds.playClick();
      const val = document.getElementById("guest-username").value.trim() || "Daksh_Battle";
      await API.loginGuest(val);
      this.updateLobbyUI();
      this.showScreen("screen-lobby");
      this.showToast(`Welcome Guest Warrior: ${currentUser.username}!`);
    };

    document.getElementById("btn-signin-submit").onclick = async () => {
      sounds.playClick();
      const u = document.getElementById("signin-username").value.trim();
      const p = document.getElementById("signin-password").value.trim();
      const errEl = document.getElementById("signin-error");

      const res = await API.login(u, p);
      if (res.ok) {
        errEl.classList.add("hidden");
        this.updateLobbyUI();
        this.showScreen("screen-lobby");
        this.showToast(`Welcome back, ${currentUser.username}!`);
      } else {
        errEl.innerText = res.msg;
        errEl.classList.remove("hidden");
      }
    };

    document.getElementById("btn-register-submit").onclick = async () => {
      sounds.playClick();
      const u = document.getElementById("register-username").value.trim();
      const p = document.getElementById("register-password").value.trim();
      const errEl = document.getElementById("register-error");

      const res = await API.register(u, p);
      if (res.ok) {
        errEl.classList.add("hidden");
        this.updateLobbyUI();
        this.showScreen("screen-lobby");
        this.showToast(`Account Created! Welcome ${currentUser.username}!`);
      } else {
        errEl.innerText = res.msg;
        errEl.classList.remove("hidden");
      }
    };

    document.getElementById("btn-google-login").onclick = () => this.openModal("modal-google-info");
    document.getElementById("btn-back-splash").onclick = () => {
      sounds.playClick();
      this.showScreen("screen-splash");
    };

    document.querySelectorAll(".btn-close-modal, [data-close]").forEach(btn => {
      btn.onclick = () => this.closeModal();
    });
    document.getElementById("modal-backdrop").onclick = () => this.closeModal();

    document.getElementById("nav-armory").onclick = () => {
      this.openModal("modal-armory");
      this.renderArmory(this.activeArmoryCategory);
    };

    document.querySelectorAll(".arm-tab").forEach(tab => {
      tab.onclick = () => {
        sounds.playClick();
        document.querySelectorAll(".arm-tab").forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        this.renderArmory(tab.dataset.cat);
      };
    });

    document.getElementById("btn-equip-weapon").onclick = () => {
      sounds.playClick();
      const sel = WEAPON_CATALOG[this.selectedArmoryWeapon];
      if (sel) {
        currentUser.equipped_weapons[sel.category] = sel.name;
        currentUser.selected_weapon = sel.name;
        API.saveProfile();
        this.renderArmory(sel.category);
        this.showToast(`Equipped ${sel.name} as active ${sel.category}!`);
      }
    };

    document.getElementById("nav-emotes").onclick = () => this.openModal("modal-emotes");
    document.querySelectorAll(".emote-card").forEach(c => {
      c.onclick = () => {
        sounds.playClick();
        const emote = c.dataset.emote;
        this.closeModal();
        this.showToast(`Emote activated: ${emote.toUpperCase()}!`);
        if (engine && engine.player) engine.player.playEmote(emote);
      };
    });

    document.getElementById("nav-character").onclick = () => this.openModal("modal-character");
    document.querySelectorAll(".char-card").forEach(c => {
      c.onclick = () => {
        sounds.playClick();
        document.querySelectorAll(".char-card").forEach(card => card.classList.remove("active"));
        c.classList.add("active");
        const charName = c.dataset.char;
        currentUser.selected_character = charName;
        API.saveProfile();
        this.updateLobbyUI();
        this.showToast(`Selected Survivor: ${charName}`);
      };
    });

    document.getElementById("btn-lobby-settings").onclick = () => this.openModal("modal-settings");
    document.getElementById("btn-lobby-mail").onclick = () => this.openModal("modal-mail");
    document.getElementById("btn-claim-mail").onclick = () => {
      sounds.playClick();
      if (!currentUser.mail_claimed) {
        currentUser.coins += 2500;
        currentUser.diamonds += 50;
        currentUser.mail_claimed = true;
        API.saveProfile();
        this.updateLobbyUI();
        this.closeModal();
        this.showToast("Claimed HQ Supply Drop: +2,500 Coins, +50 Diamonds!");
      } else {
        this.showToast("Already claimed today's supply crate!");
      }
    };

    document.getElementById("btn-lobby-logout").onclick = () => {
      sounds.playClick();
      API.loginGuest("Daksh_Battle");
      this.showScreen("screen-login");
      this.showToast("Signed out. Ready for new combatant.");
    };

    // Play Battle Royale with Loading Screen
    document.getElementById("btn-lobby-play").onclick = () => {
      this.startMatchWithLoading(engine);
    };

    document.getElementById("btn-hud-pause").onclick = () => {
      engine.pauseMatch();
      this.openModal("modal-pause");
    };
    document.getElementById("btn-pause-resume").onclick = () => {
      this.closeModal();
      engine.resumeMatch();
    };
    document.getElementById("btn-pause-settings").onclick = () => this.openModal("modal-settings");
    document.getElementById("btn-pause-lobby").onclick = () => {
      this.closeModal();
      engine.endMatch(false, 0, 0);
      this.showScreen("screen-lobby");
    };

    document.getElementById("btn-res-lobby").onclick = () => {
      sounds.playClick();
      this.updateLobbyUI();
      this.showScreen("screen-lobby");
    };
    document.getElementById("btn-res-replay").onclick = () => {
      this.startMatchWithLoading(engine);
    };

    // Settings Sliders
    const sSens = document.getElementById("slider-sens");
    sSens.oninput = () => {
      currentUser.settings.mouse_sens = parseFloat(sSens.value);
      document.getElementById("val-sens").innerText = currentUser.settings.mouse_sens.toFixed(2);
    };

    const sVolM = document.getElementById("slider-vol-master");
    sVolM.oninput = () => {
      currentUser.settings.vol_master = parseFloat(sVolM.value);
      document.getElementById("val-vol-master").innerText = `${Math.round(currentUser.settings.vol_master * 100)}%`;
      sounds.updateVolumes();
    };

    const sVolS = document.getElementById("slider-vol-sfx");
    sVolS.oninput = () => {
      currentUser.settings.vol_sfx = parseFloat(sVolS.value);
      document.getElementById("val-vol-sfx").innerText = `${Math.round(currentUser.settings.vol_sfx * 100)}%`;
      sounds.updateVolumes();
    };

    document.getElementById("btn-settings-save").onclick = () => {
      sounds.playClick();
      API.saveProfile();
      this.closeModal();
      this.showToast("Settings saved successfully!");
    };
  }
};

// ── 11. Dual-Platform App Startup ─────────────────────────────────────────────

let gameEngine = null;

window.addEventListener("DOMContentLoaded", async () => {
  gameEngine = new BattleEngine();
  UI.initEventListeners(gameEngine);
  await API.fetchProfile();
  UI.updateLobbyUI();
  gameEngine.init();

  console.log("=================================================");
  console.log("  ★  DAKSH BATTLE  ★  — PLAY • FIGHT • SURVIVE");
  console.log("  3D WebGL Battle Royale Engine Online!");
  console.log("=================================================");
});
