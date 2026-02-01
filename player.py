"""
プレイヤーデータ管理
"""

from __future__ import annotations

import random
from typing import Any

from settings import UPGRADES


class Player:
    """プレイヤーデータを管理するクラス"""

    def __init__(self) -> None:
        """初期化"""
        self.points: float = 0.0
        self.total_points_earned: float = 0.0
        self.total_clicks: int = 0
        self.upgrade_levels: dict[str, int] = {key: 0 for key in UPGRADES.keys()}

    def get_click_power(self) -> int:
        """クリックパワーを計算"""
        base_power: int = 1
        # 撫でる力
        base_power += self.upgrade_levels["click_power"] * UPGRADES["click_power"]["effect_per_level"]
        # 黄金の手
        base_power += self.upgrade_levels["golden_touch"] * UPGRADES["golden_touch"]["effect_per_level"]
        return base_power

    def get_auto_rate(self) -> float:
        """毎秒の自動獲得ポイントを計算"""
        rate: float = 0.0
        # お手伝い妖精
        rate += self.upgrade_levels["auto_click"] * UPGRADES["auto_click"]["effect_per_level"]
        # 妖精軍団
        rate += self.upgrade_levels["fairy_army"] * UPGRADES["fairy_army"]["effect_per_level"]
        return rate

    def get_lucky_chance(self) -> float:
        """ラッキーボーナスの確率を取得 (0.0 ~ 1.0)"""
        base_chance: float = 0.0
        level: int = self.upgrade_levels["lucky_bonus"]
        if level > 0:
            base_chance = 0.10  # 基本10%
            base_chance += (level - 1) * (UPGRADES["lucky_bonus"]["effect_per_level"] / 100.0)
        return min(base_chance, 0.5)  # 最大50%

    def get_upgrade_cost(self, upgrade_id: str) -> int:
        """アップグレードのコストを計算"""
        if upgrade_id not in UPGRADES:
            return 0
        upgrade: dict[str, Any] = UPGRADES[upgrade_id]
        level: int = self.upgrade_levels[upgrade_id]
        cost: float = upgrade["base_cost"] * (upgrade["cost_multiplier"] ** level)
        return int(cost)

    def can_afford_upgrade(self, upgrade_id: str) -> bool:
        """アップグレードを購入できるか確認"""
        if upgrade_id not in UPGRADES:
            return False
        # 最大レベルチェック
        upgrade: dict[str, Any] = UPGRADES[upgrade_id]
        if "max_level" in upgrade:
            if self.upgrade_levels[upgrade_id] >= upgrade["max_level"]:
                return False
        return self.points >= self.get_upgrade_cost(upgrade_id)

    def purchase_upgrade(self, upgrade_id: str) -> bool:
        """アップグレードを購入"""
        if not self.can_afford_upgrade(upgrade_id):
            return False
        cost: int = self.get_upgrade_cost(upgrade_id)
        self.points -= cost
        self.upgrade_levels[upgrade_id] += 1
        return True

    def add_points(self, amount: float) -> None:
        """ポイントを追加"""
        self.points += amount
        self.total_points_earned += amount

    def click(self) -> int:
        """クリック処理 - 獲得ポイントを返す"""
        base_points: int = self.get_click_power()

        # ラッキーボーナス判定
        if random.random() < self.get_lucky_chance():
            base_points *= 2

        self.add_points(base_points)
        self.total_clicks += 1
        return base_points

    def to_dict(self) -> dict[str, Any]:
        """セーブ用に辞書に変換"""
        return {
            "points": self.points,
            "total_points_earned": self.total_points_earned,
            "total_clicks": self.total_clicks,
            "upgrade_levels": self.upgrade_levels.copy(),
        }

    def from_dict(self, data: dict[str, Any]) -> None:
        """辞書からデータを復元"""
        self.points = data.get("points", 0.0)
        self.total_points_earned = data.get("total_points_earned", 0.0)
        self.total_clicks = data.get("total_clicks", 0)
        saved_levels: dict[str, int] = data.get("upgrade_levels", {})
        for key in self.upgrade_levels:
            if key in saved_levels:
                self.upgrade_levels[key] = saved_levels[key]
