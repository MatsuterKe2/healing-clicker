"""
アニメーション処理
"""

from __future__ import annotations

import math
import random
from typing import TypedDict

import pygame

from settings import ANIMATION, COLORS


class Particle(TypedDict):
    """パーティクルデータ"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: tuple[int, int, int]
    size: int


class PopupText:
    """ポップアップテキストアニメーション"""

    def __init__(
        self,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: tuple[int, int, int] | None = None,
        duration: float | None = None,
    ) -> None:
        """初期化"""
        self.text: str = text
        self.x: float = float(x)
        self.y: float = float(y)
        self.start_y: float = float(y)
        self.font: pygame.font.Font = font
        self.color: tuple[int, int, int] = color or COLORS["gold"]
        self.duration: float = duration or ANIMATION["popup_duration"]
        self.elapsed: float = 0.0
        self.alive: bool = True

    def update(self, dt: float) -> None:
        """更新"""
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.alive = False
            return

        # 上方に移動
        progress: float = self.elapsed / self.duration
        rise_distance: float = ANIMATION["popup_rise_distance"]
        self.y = self.start_y - (rise_distance * progress)

    def draw(self, surface: pygame.Surface) -> None:
        """描画"""
        if not self.alive:
            return

        # アルファ値計算 (フェードアウト)
        progress: float = self.elapsed / self.duration
        alpha: int = int(255 * (1 - progress))

        # テキストレンダリング
        text_surface: pygame.Surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)

        # 中央揃え
        rect: pygame.Rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surface, rect)


class ClickAnimation:
    """クリック時のスケールアニメーション"""

    def __init__(self) -> None:
        """初期化"""
        self.scale: float = 1.0
        self.target_scale: float = 1.0
        self.is_animating: bool = False
        self.shrink_phase: bool = True

    def trigger(self) -> None:
        """アニメーション開始"""
        self.scale = ANIMATION["click_scale_min"]
        self.target_scale = 1.0
        self.is_animating = True
        self.shrink_phase = False

    def update(self, dt: float) -> None:
        """更新"""
        if not self.is_animating:
            return

        # スケールを元に戻す
        speed: float = (1.0 - ANIMATION["click_scale_min"]) / ANIMATION["click_scale_duration"]
        self.scale += speed * dt

        if self.scale >= 1.0:
            self.scale = 1.0
            self.is_animating = False

    def get_scale(self) -> float:
        """現在のスケールを取得"""
        return self.scale


class ParticleEffect:
    """パーティクルエフェクト"""

    def __init__(self, x: int, y: int, count: int = 10) -> None:
        """初期化"""
        self.particles: list[Particle] = []
        for _ in range(count):
            angle: float = random.uniform(0, 360)
            speed: float = random.uniform(50, 150)
            vx: float = math.cos(math.radians(angle)) * speed
            vy: float = math.sin(math.radians(angle)) * speed
            color: tuple[int, int, int] = random.choice([
                COLORS["primary"],
                COLORS["secondary"],
                COLORS["accent"],
                COLORS["gold"],
            ])
            self.particles.append({
                "x": float(x),
                "y": float(y),
                "vx": vx,
                "vy": vy,
                "life": 1.0,
                "color": color,
                "size": random.randint(3, 8),
            })
        self.alive: bool = True

    def update(self, dt: float) -> None:
        """更新"""
        all_dead: bool = True
        for p in self.particles:
            if p["life"] <= 0:
                continue
            all_dead = False
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 200 * dt  # 重力
            p["life"] -= dt * 1.5

        if all_dead:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        """描画"""
        for p in self.particles:
            if p["life"] <= 0:
                continue
            size: int = int(p["size"] * p["life"])
            if size < 1:
                continue
            pygame.draw.circle(
                surface,
                p["color"],
                (int(p["x"]), int(p["y"])),
                size
            )


class AnimationManager:
    """アニメーション管理クラス"""

    def __init__(self) -> None:
        """初期化"""
        self.popups: list[PopupText] = []
        self.particles: list[ParticleEffect] = []
        self.click_animation: ClickAnimation = ClickAnimation()

    def add_popup(
        self,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        """ポップアップテキストを追加"""
        popup: PopupText = PopupText(text, x, y, font, color)
        self.popups.append(popup)

    def add_particles(self, x: int, y: int, count: int = 10) -> None:
        """パーティクルを追加"""
        effect: ParticleEffect = ParticleEffect(x, y, count)
        self.particles.append(effect)

    def trigger_click(self) -> None:
        """クリックアニメーション開始"""
        self.click_animation.trigger()

    def update(self, dt: float) -> None:
        """更新"""
        # ポップアップ更新
        for popup in self.popups:
            popup.update(dt)
        self.popups = [p for p in self.popups if p.alive]

        # パーティクル更新
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        # クリックアニメーション更新
        self.click_animation.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """描画"""
        # パーティクル描画
        for particle in self.particles:
            particle.draw(surface)

        # ポップアップ描画
        for popup in self.popups:
            popup.draw(surface)

    def get_click_scale(self) -> float:
        """クリックスケールを取得"""
        return self.click_animation.get_scale()
