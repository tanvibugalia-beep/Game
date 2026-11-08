"""
auth_manager.py — Secure Account, Authentication & Profile Persistence for DAKSH BATTLE.

Features:
- Secure password hashing using PBKDF2-HMAC-SHA256 with cryptographically random 16-byte salts.
- Passwords are NEVER stored in plain text.
- Unique username validation (3-16 chars, alphanumeric and underscores).
- Fresh Profile Guarantee: Every newly created account begins with:
  • Level 1, 0 XP (1000 XP to Level 2)
  • Initial Rank: Bronze (0 RP)
  • Starter demo currency: 500 Coins, 0 Diamonds (no pre-baked level 15 or 12,650 coins!)
  • Starter weapon loadout (Crimson Blaze AK, Cobra MP5, SPAS-12, G18, Kar98k)
  • Zero match history (0 matches, 0 wins, 0 kills)
  • Default personalized settings
- Distinct Guest mode clearly marked as local/offline session.
- Google OAuth 2.0 configuration check and guidance.
"""
import os
import json
import hashlib
import secrets
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'accounts.json')
GOOGLE_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google_client_secrets.json')

def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """Hash password using PBKDF2-HMAC-SHA256 with a unique salt."""
    if salt is None:
        salt = secrets.token_bytes(16)
    salt_hex = salt.hex()
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 120000).hex()
    return pwd_hash, salt_hex

def verify_password(password: str, pwd_hash: str, salt_hex: str) -> bool:
    """Verify a password against stored PBKDF2 hash and salt."""
    salt = bytes.fromhex(salt_hex)
    check_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 120000).hex()
    return secrets.compare_digest(pwd_hash, check_hash)

def validate_username(username: str) -> tuple[bool, str]:
    """Validate username rules."""
    if not username:
        return False, "Username cannot be empty."
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 16:
        return False, "Username must be at most 16 characters."
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username may only contain letters, numbers, and underscores."
    return True, ""

def create_fresh_profile(username: str, is_guest: bool = False) -> dict:
    """Generate a clean, fresh Level 1 starter profile for a newly registered player."""
    return {
        "username": username,
        "is_guest": is_guest,
        "is_logged_in": True,
        "level": 1,
        "xp": 0,
        "xp_next": 1000,
        "rank_name": "Bronze",
        "rank_score": 0,
        "coins": 500,          # Fresh starter balance
        "diamonds": 0,         # Zero starting diamonds
        "selected_character": "Daksh",
        "selected_weapon": "Crimson Blaze",
        "equipped_weapons": {
            "AR": "Crimson Blaze",
            "SMG": "Cobra MP5",
            "Shotgun": "Thunder SPAS",
            "Pistol": "Tactical G18",
            "Sniper": "Shadow Kar98k"
        },
        "inventory": [
            "Crimson Blaze", "Cobra MP5", "Thunder SPAS", "Tactical G18", "Shadow Kar98k",
            "item_helmet", "item_vest", "item_backpack", "item_medkit"
        ],
        "equipped_emotes": ["Wave", "Thumbs Up", "Celebration", "Dance"],
        "matches_played": 0,
        "wins": 0,
        "kills": 0,
        "mail_claimed": False,
        "settings": {
            "mouse_sens": 0.20,
            "vol_master": 0.70,
            "vol_music": 0.50,
            "vol_sfx": 0.80,
            "graphics_preset": "Normal",
            "fps_cap": 60
        }
    }

class AuthManager:
    """Manages persistent player accounts and sessions."""

    def __init__(self):
        self.accounts: dict[str, dict] = {}
        self.current_user: dict | None = None
        self.load_accounts()
        # Initialize default session if none exists
        if not self.current_user:
            self.login_as_guest()

    def load_accounts(self):
        """Load stored accounts database."""
        if os.path.exists(ACCOUNTS_FILE):
            try:
                with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)
            except Exception as e:
                print(f"[Auth] Error reading accounts.json: {e}")
                self.accounts = {}
        else:
            self.accounts = {}

    def save_accounts(self):
        """Save accounts database to disk atomically."""
        try:
            temp_file = f"{ACCOUNTS_FILE}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=2)
            os.replace(temp_file, ACCOUNTS_FILE)
        except Exception as e:
            print(f"[Auth] Error saving accounts.json: {e}")

    def register(self, username: str, password: str) -> tuple[bool, str, dict | None]:
        """Register a new account with a unique username and password."""
        valid, err = validate_username(username)
        if not valid:
            return False, err, None

        username_clean = username.strip()
        username_key = username_clean.lower()

        if username_key in self.accounts:
            return False, f"Username '{username_clean}' is already taken. Please choose another.", None

        if len(password) < 4:
            return False, "Password must be at least 4 characters.", None

        # Securely hash password
        pwd_hash, salt_hex = hash_password(password)

        # Create fresh profile
        profile = create_fresh_profile(username_clean, is_guest=False)

        account_entry = {
            "username": username_clean,
            "pwd_hash": pwd_hash,
            "salt_hex": salt_hex,
            "created_at": secrets.token_hex(4),
            "profile": profile
        }

        self.accounts[username_key] = account_entry
        self.save_accounts()

        self.current_user = profile
        return True, "Account created successfully!", profile

    def login(self, username: str, password: str) -> tuple[bool, str, dict | None]:
        """Authenticate user with username and password."""
        if not username:
            return False, "Username required.", None
        username_key = username.strip().lower()

        if username_key not in self.accounts:
            return False, "Account not found. Please register first.", None

        acc = self.accounts[username_key]
        if not verify_password(password, acc["pwd_hash"], acc["salt_hex"]):
            return False, "Incorrect password. Please try again.", None

        self.current_user = acc["profile"]
        return True, "Login successful!", self.current_user

    def login_as_guest(self, guest_id: str | None = None) -> dict:
        """Create or resume an offline guest session."""
        if not guest_id:
            guest_id = "Daksh_Battle"
        
        # Check if guest entry exists
        guest_key = f"__guest_{guest_id.lower()}__"
        if guest_key in self.accounts:
            profile = self.accounts[guest_key]["profile"]
        else:
            profile = create_fresh_profile(guest_id, is_guest=True)
            self.accounts[guest_key] = {
                "username": guest_id,
                "pwd_hash": "",
                "salt_hex": "",
                "created_at": "guest",
                "profile": profile
            }
            self.save_accounts()

        self.current_user = profile
        return profile

    def logout(self):
        """Sign out current user and switch to a clean guest state."""
        self.current_user = None

    def save_current_profile(self):
        """Persist modifications to the active profile."""
        if not self.current_user:
            return
        user_key = self.current_user["username"].lower()
        if self.current_user.get("is_guest"):
            user_key = f"__guest_{user_key}__"

        if user_key in self.accounts:
            self.accounts[user_key]["profile"] = self.current_user
            self.save_accounts()

    def record_match(self, won: bool, kills: int, score: int, duration_sec: int) -> dict:
        """Record game match progress to active profile."""
        if not self.current_user:
            return {"won": won, "kills": kills, "xp_gain": 0, "coin_gain": 0, "rank_gain": 0}

        p = self.current_user
        p["matches_played"] += 1
        p["kills"] += kills
        if won:
            p["wins"] += 1

        xp_gain = 180 + kills * 40 + (250 if won else 80)
        coin_gain = 200 + kills * 30 + (350 if won else 100)
        rank_gain = 35 if won else max(-15, kills * 4 - 8)

        p["xp"] += xp_gain
        p["coins"] += coin_gain
        p["rank_score"] = max(0, p["rank_score"] + rank_gain)

        # Level up logic
        while p["xp"] >= p["xp_next"]:
            p["xp"] -= p["xp_next"]
            p["level"] += 1
            p["xp_next"] = int(p["xp_next"] * 1.25)
            p["diamonds"] += 15  # Level up diamond reward

        # Update rank tier
        score = p["rank_score"]
        if score >= 3500:
            p["rank_name"] = "Master"
        elif score >= 2800:
            p["rank_name"] = "Heroic"
        elif score >= 2200:
            p["rank_name"] = "Diamond I"
        elif score >= 1600:
            p["rank_name"] = "Platinum"
        elif score >= 1000:
            p["rank_name"] = "Gold"
        elif score >= 500:
            p["rank_name"] = "Silver"
        else:
            p["rank_name"] = "Bronze"

        self.save_current_profile()

        return {
            "won": won,
            "kills": kills,
            "xp_gain": xp_gain,
            "coin_gain": coin_gain,
            "rank_gain": rank_gain
        }

    def is_google_configured(self) -> bool:
        """Check whether Google OAuth client secrets file exists."""
        return os.path.exists(GOOGLE_CONFIG_FILE)

    def get_google_auth_status(self) -> str:
        if self.is_google_configured():
            return "Google OAuth 2.0 configuration detected."
        return (
            "Google Sign-In is not configured yet.\n\n"
            "Official Setup Instructions:\n"
            "1. Visit Google Cloud Console (console.cloud.google.com)\n"
            "2. Create an OAuth 2.0 Client ID for Web / Desktop Application\n"
            "3. Place downloaded credentials in 'google_client_secrets.json'\n\n"
            "Offline Guest mode and local accounts work 100% without external setup."
        )

# Global singleton
auth_manager = AuthManager()
