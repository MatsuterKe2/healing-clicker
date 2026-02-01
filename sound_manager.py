"""
サウンド管理
"""

from __future__ import annotations

import os

import pygame

from settings import DEFAULT_BGM_VOLUME, DEFAULT_SFX_VOLUME


class SoundManager:
    """サウンド管理クラス"""

    def __init__(self) -> None:
        """初期化"""
        self.bgm_volume: float = DEFAULT_BGM_VOLUME
        self.sfx_volume: float = DEFAULT_SFX_VOLUME
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.current_bgm: str | None = None
        self.is_initialized: bool = False

        # pygame.mixerが初期化されているか確認
        if pygame.mixer.get_init():
            self.is_initialized = True

    def load_sound(self, name: str, path: str) -> bool:
        """効果音をロード"""
        if not self.is_initialized:
            return False
        try:
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
                self.sounds[name].set_volume(self.sfx_volume)
                return True
            else:
                print(f"サウンドファイルが見つかりません: {path}")
                return False
        except Exception as e:
            print(f"サウンドロードエラー ({name}): {e}")
            return False

    def load_all_sounds(self, sound_dir: str = "assets/sounds") -> None:
        """全効果音をロード"""
        sound_files: dict[str, str] = {
            "click": "click.wav",
            "upgrade": "upgrade.wav",
            "bonus": "bonus.wav",
        }
        for name, filename in sound_files.items():
            path: str = os.path.join(sound_dir, filename)
            self.load_sound(name, path)

    def play_sound(self, name: str) -> None:
        """効果音を再生"""
        if not self.is_initialized:
            return
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"サウンド再生エラー ({name}): {e}")

    def load_bgm(self, path: str) -> bool:
        """BGMをロード"""
        if not self.is_initialized:
            return False
        try:
            if os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.bgm_volume)
                self.current_bgm = path
                return True
            else:
                print(f"BGMファイルが見つかりません: {path}")
                return False
        except Exception as e:
            print(f"BGMロードエラー: {e}")
            return False

    def play_bgm(self, loops: int = -1) -> None:
        """BGMを再生（デフォルトはループ）"""
        if not self.is_initialized:
            return
        try:
            pygame.mixer.music.play(loops)
        except Exception as e:
            print(f"BGM再生エラー: {e}")

    def stop_bgm(self) -> None:
        """BGMを停止"""
        if not self.is_initialized:
            return
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"BGM停止エラー: {e}")

    def pause_bgm(self) -> None:
        """BGMを一時停止"""
        if not self.is_initialized:
            return
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"BGM一時停止エラー: {e}")

    def unpause_bgm(self) -> None:
        """BGMを再開"""
        if not self.is_initialized:
            return
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"BGM再開エラー: {e}")

    def set_bgm_volume(self, volume: float) -> None:
        """BGM音量を設定"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        if self.is_initialized:
            try:
                pygame.mixer.music.set_volume(self.bgm_volume)
            except Exception:
                pass

    def set_sfx_volume(self, volume: float) -> None:
        """効果音音量を設定"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            try:
                sound.set_volume(self.sfx_volume)
            except Exception:
                pass

    def get_bgm_volume(self) -> float:
        """BGM音量を取得"""
        return self.bgm_volume

    def get_sfx_volume(self) -> float:
        """効果音音量を取得"""
        return self.sfx_volume

    def cleanup(self) -> None:
        """リソース解放"""
        self.stop_bgm()
        self.sounds.clear()
