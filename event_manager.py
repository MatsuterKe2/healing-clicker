"""
ランダムイベント管理・イベント実行
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

import pygame

from settings import COLORS, EVENT_CONFIG

if TYPE_CHECKING:
    from player import Player


class RandomEvent:
    """個別イベントデータ"""

    def __init__(
        self,
        event_type: str,
        name: str,
        duration: float,
        description: str,
    ) -> None:
        self.event_type: str = event_type
        self.name: str = name
        self.duration: float = duration
        self.description: str = description
        self.elapsed: float = 0.0
        self.active: bool = True
        self.success: bool = False
        # イベント固有データ
        self.targets: list[dict[str, Any]] = []
        self.collected: int = 0
        self.required: int = 0

    @property
    def time_remaining(self) -> float:
        return max(0.0, self.duration - self.elapsed)

    @property
    def progress(self) -> float:
        if self.required <= 0:
            return 0.0
        return min(1.0, self.collected / self.required)


EVENT_TEMPLATES: list[dict[str, Any]] = [
    {
        "type": "gold_rush",
        "name": "ゴールドラッシュ",
        "duration": 10.0,
        "description": "10秒間クリックポイント5倍！",
        "required": 0,
    },
    {
        "type": "shooting_star",
        "name": "流れ星",
        "duration": 15.0,
        "description": "流れ星をクリックしよう！",
        "required": 3,
    },
    {
        "type": "flower_field",
        "name": "お花畑",
        "duration": 20.0,
        "description": "お花を収穫しよう！",
        "required": 5,
    },
    {
        "type": "rainbow_visitor",
        "name": "虹の訪問者",
        "duration": 10.0,
        "description": "不思議な訪問者が現れた！",
        "required": 1,
    },
]


class EventManager:
    """ランダムイベント管理"""

    def __init__(self) -> None:
        self.current_event: RandomEvent | None = None
        self._timer: float = 0.0
        self._next_interval: float = self._random_interval()
        self.total_completed: int = 0
        self.showing_alert: bool = False
        self._alert_timer: float = 0.0

    def _random_interval(self) -> float:
        return random.uniform(
            EVENT_CONFIG["min_interval"], EVENT_CONFIG["max_interval"]
        )

    # ------------------------------------------------------------------
    # 更新
    # ------------------------------------------------------------------
    def update(self, dt: float) -> dict[str, Any] | None:
        """更新。イベント完了/失敗時に結果dictを返す"""
        # イベント中
        if self.current_event is not None:
            ev = self.current_event
            ev.elapsed += dt
            if ev.elapsed >= ev.duration:
                return self._finish_event()
            # gold_rush は時間経過で自動成功
            if ev.event_type == "gold_rush" and ev.elapsed >= ev.duration:
                ev.success = True
                return self._finish_event()
            return None

        # アラート表示中
        if self.showing_alert:
            self._alert_timer += dt
            if self._alert_timer > 5.0:
                self.showing_alert = False
                self._start_event()
            return None

        # 次のイベントまでカウントダウン
        self._timer += dt
        if self._timer >= self._next_interval:
            self._timer = 0.0
            self.showing_alert = True
            self._alert_timer = 0.0
        return None

    def _start_event(self) -> None:
        template = random.choice(EVENT_TEMPLATES)
        ev = RandomEvent(
            template["type"], template["name"],
            template["duration"], template["description"],
        )
        ev.required = template["required"]

        if ev.event_type in ("shooting_star", "flower_field", "rainbow_visitor"):
            for _ in range(ev.required):
                ev.targets.append({
                    "x": random.randint(100, 800),
                    "y": random.randint(150, 550),
                    "alive": True,
                })
        self.current_event = ev

    def _finish_event(self) -> dict[str, Any]:
        ev = self.current_event
        assert ev is not None
        result: dict[str, Any] = {"type": ev.event_type, "success": False}
        if ev.event_type == "gold_rush":
            ev.success = True
        elif ev.collected >= ev.required:
            ev.success = True
        result["success"] = ev.success
        if ev.success:
            self.total_completed += 1
        self.current_event = None
        self._next_interval = self._random_interval()
        self._timer = 0.0
        return result

    # ------------------------------------------------------------------
    # イベント操作
    # ------------------------------------------------------------------
    def handle_click(self, pos: tuple[int, int]) -> bool:
        """イベント中のクリック処理。ターゲットを消費したらTrue"""
        if self.current_event is None:
            return False
        ev = self.current_event
        if ev.event_type == "gold_rush":
            return False  # クリックは通常クリック側で倍率処理
        for t in ev.targets:
            if not t["alive"]:
                continue
            dx = pos[0] - t["x"]
            dy = pos[1] - t["y"]
            if dx * dx + dy * dy < 30 * 30:
                t["alive"] = False
                ev.collected += 1
                if ev.collected >= ev.required:
                    ev.success = True
                return True
        return False

    def dismiss_alert(self) -> None:
        """アラートをクリックで即開始"""
        if self.showing_alert:
            self.showing_alert = False
            self._start_event()

    def is_gold_rush(self) -> bool:
        return (
            self.current_event is not None
            and self.current_event.event_type == "gold_rush"
        )

    def get_click_multiplier(self) -> int:
        if self.is_gold_rush():
            return 5
        return 1

    # ------------------------------------------------------------------
    # 描画
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font]) -> None:
        if self.showing_alert:
            self._draw_alert(surface, fonts)
        elif self.current_event is not None:
            self._draw_event(surface, fonts)

    def _draw_alert(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font]) -> None:
        # 画面上部にバナー
        banner = pygame.Rect(340, 80, 600, 50)
        pygame.draw.rect(surface, (*COLORS["gold"], 220), banner, border_radius=12)
        pygame.draw.rect(surface, COLORS["text"], banner, 2, border_radius=12)
        text = fonts["medium"].render("！イベント発生！ クリックで開始", True, COLORS["text"])
        tr = text.get_rect(center=banner.center)
        surface.blit(text, tr)

    def _draw_event(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font]) -> None:
        ev = self.current_event
        if ev is None:
            return

        # イベント名 + 残り時間
        info_text = f"{ev.name}  残り {ev.time_remaining:.1f}秒"
        info_surf = fonts["medium"].render(info_text, True, COLORS["gold"])
        surface.blit(info_surf, (340, 85))

        # 説明
        desc_surf = fonts["small"].render(ev.description, True, COLORS["text"])
        surface.blit(desc_surf, (340, 115))

        # 進捗バー (収集系)
        if ev.required > 0:
            bar_bg = pygame.Rect(340, 138, 200, 12)
            pygame.draw.rect(surface, COLORS["text_light"], bar_bg, border_radius=6)
            filled_w = int(200 * ev.progress)
            if filled_w > 0:
                bar_fill = pygame.Rect(340, 138, filled_w, 12)
                pygame.draw.rect(surface, COLORS["gold"], bar_fill, border_radius=6)
            prog_text = fonts["small"].render(f"{ev.collected}/{ev.required}", True, COLORS["text"])
            surface.blit(prog_text, (548, 134))

        # ターゲット描画
        if ev.event_type == "shooting_star":
            for t in ev.targets:
                if t["alive"]:
                    pygame.draw.circle(surface, (255, 255, 150), (t["x"], t["y"]), 15)
                    pygame.draw.circle(surface, COLORS["gold"], (t["x"], t["y"]), 10)
                    pygame.draw.circle(surface, COLORS["white"], (t["x"] - 3, t["y"] - 3), 4)
        elif ev.event_type == "flower_field":
            for t in ev.targets:
                if t["alive"]:
                    # 花びら
                    for angle_offset in range(5):
                        import math
                        a = math.radians(angle_offset * 72)
                        px = t["x"] + int(math.cos(a) * 10)
                        py = t["y"] + int(math.sin(a) * 10)
                        pygame.draw.circle(surface, (255, 180, 200), (px, py), 8)
                    pygame.draw.circle(surface, (255, 230, 100), (t["x"], t["y"]), 6)
        elif ev.event_type == "rainbow_visitor":
            for t in ev.targets:
                if t["alive"]:
                    # シルエット (丸い影)
                    silhouette = pygame.Surface((60, 60), pygame.SRCALPHA)
                    pygame.draw.circle(silhouette, (100, 80, 150, 180), (30, 30), 28)
                    pygame.draw.circle(silhouette, (150, 130, 200, 200), (30, 25), 16)
                    text = fonts["small"].render("？", True, COLORS["white"])
                    tr = text.get_rect(center=(30, 30))
                    silhouette.blit(text, tr)
                    surface.blit(silhouette, (t["x"] - 30, t["y"] - 30))

    # ------------------------------------------------------------------
    # セーブ / ロード
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "total_events_completed": self.total_completed,
        }

    def from_dict(self, data: dict[str, Any]) -> None:
        self.total_completed = data.get("total_events_completed", 0)
