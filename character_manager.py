"""
キャラクター管理（解放判定・好感度・表情切替）
"""

from __future__ import annotations

import math
import os
from typing import TYPE_CHECKING, Any

import pygame

from settings import AFFECTION, CHARACTERS, COLORS

if TYPE_CHECKING:
    from player import Player


class CharacterManager:
    """キャラクター管理クラス"""

    def __init__(self) -> None:
        self.current_id: str = "hana"
        self.unlocked: list[str] = ["hana"]
        self.affection: dict[str, float] = {cid: 0.0 for cid in CHARACTERS}
        # アイドルアニメーション用
        self._idle_timer: float = 0.0
        self._blink_timer: float = 0.0
        self._blink_duration: float = 0.15
        self._is_blinking: bool = False
        self._next_blink: float = 3.0

    # ------------------------------------------------------------------
    # 解放判定
    # ------------------------------------------------------------------
    def check_unlocks(self, player: Player, achievement_count: int = 0) -> list[str]:
        """解放条件をチェックし、新たに解放されたキャラIDリストを返す"""
        newly: list[str] = []
        for cid, info in CHARACTERS.items():
            if cid in self.unlocked:
                continue
            cond = info["unlock_condition"]
            if cond is None:
                if cid not in self.unlocked:
                    self.unlocked.append(cid)
                    newly.append(cid)
                continue
            unlocked = False
            if cond["type"] == "total_points":
                unlocked = player.total_points_earned >= cond["value"]
            elif cond["type"] == "total_clicks":
                unlocked = player.total_clicks >= cond["value"]
            elif cond["type"] == "achievements":
                unlocked = achievement_count >= cond["value"]
            if unlocked:
                self.unlocked.append(cid)
                newly.append(cid)
        return newly

    # ------------------------------------------------------------------
    # 好感度
    # ------------------------------------------------------------------
    def add_affection(self, amount: float, character_id: str | None = None) -> None:
        cid = character_id or self.current_id
        if cid in self.affection:
            self.affection[cid] = min(
                AFFECTION["max"], self.affection[cid] + amount
            )

    def get_affection(self, character_id: str | None = None) -> float:
        cid = character_id or self.current_id
        return self.affection.get(cid, 0.0)

    def get_affection_level(self, character_id: str | None = None) -> int:
        """好感度レベル (0-indexed) を返す"""
        val = self.get_affection(character_id)
        level = 0
        for i, lv in enumerate(AFFECTION["levels"]):
            if val >= lv["min"]:
                level = i
        return level

    def get_affection_level_info(self, character_id: str | None = None) -> dict[str, Any]:
        idx = self.get_affection_level(character_id)
        return AFFECTION["levels"][idx]

    def get_max_affection(self) -> float:
        """全キャラの最大好感度を返す"""
        return max(self.affection.values()) if self.affection else 0.0

    def all_affection_above(self, threshold: float) -> bool:
        return all(v >= threshold for v in self.affection.values())

    # ------------------------------------------------------------------
    # キャラ切替
    # ------------------------------------------------------------------
    def switch_character(self, character_id: str) -> bool:
        if character_id in self.unlocked:
            self.current_id = character_id
            return True
        return False

    # ------------------------------------------------------------------
    # 描画
    # ------------------------------------------------------------------
    def create_character_surface(
        self, size: tuple[int, int], character_id: str | None = None
    ) -> pygame.Surface:
        """キャラクター画像を生成"""
        cid = character_id or self.current_id
        info = CHARACTERS.get(cid, CHARACTERS["hana"])

        # 画像ファイルがあれば使う
        image_path = f"assets/images/{cid}.png"
        if os.path.exists(image_path):
            try:
                img = pygame.image.load(image_path)
                return pygame.transform.scale(img, size)
            except Exception:
                pass

        colors = info["colors"]
        aff_level = self.get_affection_level(cid)
        expression = AFFECTION["levels"][aff_level]["expression"]
        return self._draw_character(size, colors, expression)

    def _draw_character(
        self,
        size: tuple[int, int],
        colors: dict[str, tuple[int, int, int]],
        expression: str,
    ) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        cx, cy = size[0] // 2, size[1] // 2
        skin = (255, 228, 225)
        hair = colors["hair"]
        hair_shadow = colors["hair_shadow"]
        ribbon = colors["ribbon"]

        # 背景円
        pygame.draw.circle(surface, colors["accent"], (cx, cy), size[0] // 2 - 6)
        # 髪シルエット
        pygame.draw.ellipse(surface, hair, (cx - 70, cy - 90, 140, 150))
        pygame.draw.ellipse(surface, hair_shadow, (cx - 75, cy - 85, 150, 155), 6)
        # 前髪
        pygame.draw.polygon(surface, hair, [
            (cx - 55, cy - 40), (cx, cy - 70), (cx + 55, cy - 40),
            (cx + 40, cy - 15), (cx - 40, cy - 15),
        ])
        # 顔
        pygame.draw.ellipse(surface, skin, (cx - 52, cy - 40, 104, 110))

        eye_y = cy - 10
        eye_off = 28
        self._draw_eyes(surface, cx, eye_y, eye_off, expression)
        self._draw_eyebrows(surface, cx, eye_y)

        # 頬
        cheek_color = (255, 190, 200)
        if expression in ("blush", "sparkle", "rainbow"):
            cheek_color = (255, 160, 170)
        cheek_size = 10 if expression not in ("blush", "sparkle", "rainbow") else 13
        pygame.draw.circle(surface, cheek_color, (cx - 38, eye_y + 22), cheek_size)
        pygame.draw.circle(surface, cheek_color, (cx + 38, eye_y + 22), cheek_size)

        # 口
        self._draw_mouth(surface, cx, eye_y, expression)

        # リボン
        pygame.draw.polygon(surface, ribbon, [
            (cx - 70, cy - 60), (cx - 90, cy - 70),
            (cx - 72, cy - 82), (cx - 55, cy - 72),
        ])
        ribbon_center = (
            max(0, min(size[0], ribbon[0])),
            max(0, min(size[1], ribbon[1])),
        )
        pygame.draw.circle(
            surface,
            (min(255, ribbon[0] - 30), min(255, max(0, ribbon[1] - 30)), min(255, max(0, ribbon[2] - 20))),
            (cx - 70, cy - 72), 6,
        )

        # 好感度演出
        if expression == "sparkle":
            self._draw_sparkles(surface, cx, cy, size)
        elif expression == "rainbow":
            self._draw_sparkles(surface, cx, cy, size, rainbow=True)

        return surface

    def _draw_eyes(
        self, surface: pygame.Surface, cx: int, eye_y: int, offset: int, expression: str
    ) -> None:
        is_blink = self._is_blinking and expression not in ("sparkle", "rainbow")
        for d in (-1, 1):
            ex = cx + d * offset
            if is_blink:
                pygame.draw.line(surface, COLORS["text"], (ex - 12, eye_y), (ex + 12, eye_y), 3)
                continue
            # 白目
            pygame.draw.ellipse(surface, COLORS["white"], (ex - 16, eye_y - 10, 32, 24))
            if expression == "sparkle":
                iris = (255, 200, 100)
            elif expression == "rainbow":
                iris = (200, 150, 255)
            else:
                iris = (120, 80, 200)
            pygame.draw.ellipse(surface, iris, (ex - 10, eye_y - 6, 20, 20))
            pygame.draw.circle(surface, COLORS["black"], (ex, eye_y + 2), 6)
            pygame.draw.circle(surface, COLORS["white"], (ex - 5, eye_y - 4), 4)
            # キラキラ瞳 (sparkle / rainbow)
            if expression in ("sparkle", "rainbow"):
                pygame.draw.circle(surface, COLORS["white"], (ex + 4, eye_y - 2), 2)
                pygame.draw.circle(surface, (255, 255, 200), (ex - 3, eye_y + 5), 2)

    def _draw_eyebrows(self, surface: pygame.Surface, cx: int, eye_y: int) -> None:
        pygame.draw.arc(surface, COLORS["text"], (cx - 45, eye_y - 30, 35, 20), 3.4, 5.0, 3)
        pygame.draw.arc(surface, COLORS["text"], (cx + 10, eye_y - 30, 35, 20), 4.4, 6.0, 3)

    def _draw_mouth(self, surface: pygame.Surface, cx: int, eye_y: int, expression: str) -> None:
        if expression == "normal":
            pygame.draw.arc(surface, COLORS["text"], (cx - 18, eye_y + 20, 36, 24), 3.14, 0, 3)
        elif expression == "smile":
            pygame.draw.arc(surface, COLORS["text"], (cx - 22, eye_y + 16, 44, 30), 3.14, 0, 3)
        elif expression == "blush":
            pygame.draw.arc(surface, COLORS["text"], (cx - 15, eye_y + 18, 30, 22), 3.14, 0, 3)
            pygame.draw.ellipse(surface, (255, 200, 200), (cx - 6, eye_y + 24, 12, 6))
        elif expression in ("sparkle", "rainbow"):
            pygame.draw.arc(surface, COLORS["text"], (cx - 24, eye_y + 14, 48, 34), 3.14, 0, 3)
            pygame.draw.ellipse(surface, (255, 200, 200), (cx - 8, eye_y + 26, 16, 8))

    def _draw_sparkles(
        self, surface: pygame.Surface, cx: int, cy: int,
        size: tuple[int, int], rainbow: bool = False,
    ) -> None:
        import random as _rng
        _rng.seed(42)
        sparkle_colors = [
            (255, 255, 150), (255, 200, 255), (200, 255, 255), (255, 220, 180),
        ]
        if rainbow:
            sparkle_colors = [
                (255, 100, 100), (255, 200, 100), (100, 255, 100),
                (100, 200, 255), (200, 100, 255),
            ]
        for _ in range(8):
            sx = _rng.randint(10, size[0] - 10)
            sy = _rng.randint(10, size[1] - 10)
            c = _rng.choice(sparkle_colors)
            pygame.draw.circle(surface, c, (sx, sy), _rng.randint(2, 4))

    # ------------------------------------------------------------------
    # アイドルアニメーション
    # ------------------------------------------------------------------
    def update_idle(self, dt: float) -> None:
        self._idle_timer += dt
        self._blink_timer += dt
        if not self._is_blinking and self._blink_timer >= self._next_blink:
            self._is_blinking = True
            self._blink_timer = 0.0
        if self._is_blinking and self._blink_timer >= self._blink_duration:
            self._is_blinking = False
            self._blink_timer = 0.0
            import random
            self._next_blink = random.uniform(2.0, 5.0)

    def get_idle_offset_y(self) -> float:
        return math.sin(self._idle_timer * 1.5) * 3.0

    # ------------------------------------------------------------------
    # セーブ / ロード
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "current_character": self.current_id,
            "unlocked": self.unlocked.copy(),
            "affection": self.affection.copy(),
        }

    def from_dict(self, data: dict[str, Any]) -> None:
        self.current_id = data.get("current_character", "hana")
        self.unlocked = data.get("unlocked", ["hana"])
        saved_aff = data.get("affection", {})
        for cid in self.affection:
            if cid in saved_aff:
                self.affection[cid] = saved_aff[cid]
