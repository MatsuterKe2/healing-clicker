"""
実績判定・報酬付与・通知
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from settings import ACHIEVEMENTS, UPGRADES

if TYPE_CHECKING:
    from character_manager import CharacterManager
    from player import Player


class AchievementManager:
    """実績管理クラス"""

    def __init__(self) -> None:
        self.unlocked: list[str] = []
        self.notified: list[str] = []
        # 特殊フラグ
        self.first_lucky: bool = False
        self.first_offline: bool = False
        self.first_event: bool = False

    def check_all(
        self, player: Player, char_mgr: CharacterManager
    ) -> list[dict[str, Any]]:
        """全実績をチェックし、新たに達成された実績情報のリストを返す"""
        newly: list[dict[str, Any]] = []
        for aid, info in ACHIEVEMENTS.items():
            if aid in self.unlocked:
                continue
            if self._evaluate(aid, info["condition"], player, char_mgr):
                self.unlocked.append(aid)
                newly.append({"id": aid, **info})
        return newly

    def _evaluate(
        self,
        aid: str,
        cond: dict[str, Any],
        player: Player,
        char_mgr: CharacterManager,
    ) -> bool:
        t = cond["type"]
        v = cond["value"]
        if t == "total_clicks":
            return player.total_clicks >= v
        if t == "total_points":
            return player.total_points_earned >= v
        if t == "total_upgrades":
            return sum(player.upgrade_levels.values()) >= v
        if t == "all_upgrades_lv":
            return all(lv >= v for lv in player.upgrade_levels.values())
        if t == "max_affection":
            return char_mgr.get_max_affection() >= v
        if t == "all_affection":
            return char_mgr.all_affection_above(v)
        if t == "first_lucky":
            return self.first_lucky
        if t == "first_offline":
            return self.first_offline
        if t == "first_event":
            return self.first_event
        return False

    def mark_lucky(self) -> None:
        self.first_lucky = True

    def mark_offline(self) -> None:
        self.first_offline = True

    def mark_event(self) -> None:
        self.first_event = True

    def count(self) -> int:
        return len(self.unlocked)

    # ------------------------------------------------------------------
    # セーブ / ロード
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "unlocked": self.unlocked.copy(),
            "notified": self.notified.copy(),
            "first_lucky": self.first_lucky,
            "first_offline": self.first_offline,
            "first_event": self.first_event,
        }

    def from_dict(self, data: dict[str, Any]) -> None:
        self.unlocked = data.get("unlocked", [])
        self.notified = data.get("notified", [])
        self.first_lucky = data.get("first_lucky", False)
        self.first_offline = data.get("first_offline", False)
        self.first_event = data.get("first_event", False)
