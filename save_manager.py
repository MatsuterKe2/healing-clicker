"""
セーブ・ロード・オフライン収益計算
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any

from settings import DEFAULT_BGM_VOLUME, DEFAULT_SFX_VOLUME, SAVE_FILE

if TYPE_CHECKING:
    from player import Player


class SaveManager:
    """セーブデータ管理クラス"""

    def __init__(self, save_path: str = SAVE_FILE) -> None:
        """初期化"""
        self.save_path: str = save_path

    def save(
        self,
        player: Player,
        settings: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> bool:
        """ゲームデータをセーブ"""
        try:
            data: dict[str, Any] = {
                "player": player.to_dict(),
                "last_played": datetime.now().isoformat(),
                "daily_login": datetime.now().strftime("%Y-%m-%d"),
                "settings": settings or {
                    "bgm_volume": DEFAULT_BGM_VOLUME,
                    "sfx_volume": DEFAULT_SFX_VOLUME,
                },
            }
            if extra:
                data.update(extra)
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"セーブエラー: {e}")
            return False

    def load(self) -> dict[str, Any] | None:
        """セーブデータをロード"""
        if not os.path.exists(self.save_path):
            return None
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
            return data
        except Exception as e:
            print(f"ロードエラー: {e}")
            return None

    def calculate_offline_earnings(self, player: Player, last_played_str: str) -> float:
        """オフライン収益を計算"""
        try:
            last_played: datetime = datetime.fromisoformat(last_played_str)
            now: datetime = datetime.now()
            offline_seconds: float = (now - last_played).total_seconds()

            # 最大24時間分まで
            max_offline_seconds: int = 24 * 60 * 60
            offline_seconds = min(offline_seconds, max_offline_seconds)

            # オフライン効率は50%
            efficiency: float = 0.5
            auto_rate: float = player.get_auto_rate()
            earnings: float = auto_rate * offline_seconds * efficiency

            return earnings
        except Exception as e:
            print(f"オフライン収益計算エラー: {e}")
            return 0.0

    def delete_save(self) -> bool:
        """セーブデータを削除"""
        try:
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
            return True
        except Exception as e:
            print(f"セーブ削除エラー: {e}")
            return False

    def has_save(self) -> bool:
        """セーブデータが存在するか確認"""
        return os.path.exists(self.save_path)
