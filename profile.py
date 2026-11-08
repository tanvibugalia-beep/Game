"""
profile.py — Compatibility Layer connecting to auth_manager for DAKSH BATTLE.
Ensures legacy code referencing profile.player_profile seamlessly gets the authenticated user.
"""
from auth_manager import auth_manager

class ProfileProxy:
    """Dynamic proxy delegating to the authenticated profile in auth_manager."""

    @property
    def data(self) -> dict:
        if auth_manager.current_user is None:
            auth_manager.login_as_guest()
        return auth_manager.current_user

    def save(self):
        auth_manager.save_current_profile()

    def login_as_guest(self):
        return auth_manager.login_as_guest()

    def logout(self):
        auth_manager.logout()

    def is_google_configured(self) -> bool:
        return auth_manager.is_google_configured()

    def get_google_auth_status(self) -> str:
        return auth_manager.get_google_auth_status()

    def record_match_result(self, won: bool, kills: int, score: int, duration_sec: int) -> dict:
        return auth_manager.record_match(won, kills, score, duration_sec)

    def claim_daily_mail(self) -> bool:
        if not self.data.get("mail_claimed"):
            self.data["coins"] += 2500
            self.data["diamonds"] += 50
            self.data["mail_claimed"] = True
            self.save()
            return True
        return False

# Global singleton proxy
player_profile = ProfileProxy()
