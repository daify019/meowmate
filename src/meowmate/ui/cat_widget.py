from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QPoint, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from src.meowmate.domain.models import CatAction, CatBreed
from src.meowmate.services.behavior import BehaviorState


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SPRITE_ROOT = PROJECT_ROOT / "assets" / "cats" / "tiny_kitten_cc0" / "TINY CAT SPRITE"


@dataclass(frozen=True)
class SpriteClip:
    frames: tuple[QPixmap, ...]
    frame_step: int = 2
    y_offset: int = 0
    scale: float = 1.0


class CatWidget(QWidget):
    clicked = Signal()
    drag_started = Signal()
    drag_finished = Signal()
    moved = Signal(QPoint)

    def __init__(self, breed: CatBreed, state: BehaviorState) -> None:
        super().__init__()
        self.breed = breed
        self.state = state
        self.setMouseTracking(True)
        self._drag_offset: QPoint | None = None
        self._press_global: QPoint | None = None
        self.setFixedSize(240, 220)

    def set_breed(self, breed: CatBreed) -> None:
        self.breed = breed
        self.update()

    def set_scale(self, scale: float) -> None:
        self.setFixedSize(round(240 * scale), round(220 * scale))
        self.update()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            global_pos = event.globalPosition().toPoint()
            self._press_global = global_pos
            self._drag_offset = global_pos - self.window().frameGeometry().topLeft()
            self.drag_started.emit()
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.moved.emit(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and self._drag_offset is not None:
            moved_far = self._press_global is not None and (
                event.globalPosition().toPoint() - self._press_global
            ).manhattanLength() > 4
            self._drag_offset = None
            self._press_global = None
            self.drag_finished.emit()
            if not moved_far:
                self.clicked.emit()
            event.accept()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        current = self._clip_for(self.state.action)
        previous = self._clip_for(self.state.previous_action)
        transition = self.state.transition_frame / max(1, self.state.transition_frames)
        transition = _ease_out(transition)

        self._draw_shadow(painter, current)
        if transition < 1 and self.state.previous_action != self.state.action:
            painter.setOpacity(1 - transition)
            self._draw_clip(painter, previous, self.state.frame, settle=1 - transition)
            painter.setOpacity(transition)
            self._draw_clip(painter, current, self.state.frame, settle=transition)
            painter.setOpacity(1)
        else:
            self._draw_clip(painter, current, self.state.frame, settle=1)

    def _clip_for(self, action: CatAction) -> SpriteClip:
        if action == CatAction.WALK:
            return _load_clip(self.breed.id, "02_Run", frame_step=1, y_offset=0, scale=1.02)
        if action == CatAction.SLEEP:
            return _load_clip(self.breed.id, "05_Dead", frame_step=5, y_offset=18, scale=1.06)
        if action in {CatAction.CLICKED, CatAction.DRAGGED, CatAction.ANNOYED}:
            return _load_clip(self.breed.id, "04_Hurt", frame_step=3, y_offset=0, scale=1.0)
        if action == CatAction.SPECIAL:
            if self.breed.id == "ragdoll":
                return _load_clip(self.breed.id, "05_Dead", frame_step=4, y_offset=18, scale=1.08)
            return _load_clip(self.breed.id, "03_Jump/01_Up", frame_step=2, y_offset=-12, scale=1.0)
        return _load_clip(self.breed.id, "01_Idle", frame_step=3, y_offset=0, scale=1.0)

    def _draw_clip(self, painter: QPainter, clip: SpriteClip, frame: int, settle: float) -> None:
        if not clip.frames:
            return
        pixmap = clip.frames[(frame // max(1, clip.frame_step)) % len(clip.frames)]
        target_height = self.height() * 0.82 * clip.scale
        target_width = target_height * pixmap.width() / max(1, pixmap.height())
        if self.state.facing > 0:
            painter.save()
            painter.translate(self.width(), 0)
            painter.scale(-1, 1)
            rect = self._target_rect(target_width, target_height, clip.y_offset, settle)
            painter.drawPixmap(rect, pixmap, QRectF(pixmap.rect()))
            painter.restore()
            return
        rect = self._target_rect(target_width, target_height, clip.y_offset, settle)
        painter.drawPixmap(rect, pixmap, QRectF(pixmap.rect()))

    def _target_rect(self, width: float, height: float, y_offset: int, settle: float) -> QRectF:
        lift = (1 - settle) * 7
        x = (self.width() - width) / 2
        y = self.height() - height - 18 + y_offset + lift
        return QRectF(x, y, width, height)

    def _draw_shadow(self, painter: QPainter, clip: SpriteClip) -> None:
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(28, 24, 22, 54))
        painter.drawEllipse(QRectF(self.width() * 0.27, self.height() - 30, self.width() * 0.46, 14))


@lru_cache(maxsize=64)
def _load_clip(breed_id: str, folder: str, frame_step: int, y_offset: int, scale: float) -> SpriteClip:
    directory = SPRITE_ROOT / folder
    frames = tuple(
        QPixmap.fromImage(_tint_and_crop(QImage(str(path)), breed_id))
        for path in sorted(directory.glob("*.png"))
    )
    return SpriteClip(frames=frames, frame_step=frame_step, y_offset=y_offset, scale=scale)


def _tint_and_crop(image: QImage, breed_id: str) -> QImage:
    image = image.convertToFormat(QImage.Format_ARGB32)
    body, belly, accent = _palette_for(breed_id)
    left, top, right, bottom = image.width(), image.height(), 0, 0
    for y in range(image.height()):
        for x in range(image.width()):
            color = image.pixelColor(x, y)
            if color.alpha() == 0:
                continue
            left = min(left, x)
            top = min(top, y)
            right = max(right, x)
            bottom = max(bottom, y)
            luminance = int(color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114)
            if luminance < 36:
                new_color = color
            elif luminance > 205:
                new_color = _shade(belly, luminance)
            elif luminance < 95:
                new_color = _shade(accent, luminance + 35)
            else:
                new_color = _shade(body, luminance)
            new_color.setAlpha(color.alpha())
            image.setPixelColor(x, y, new_color)
    if right <= left or bottom <= top:
        return image
    padding = 8
    return image.copy(
        max(0, left - padding),
        max(0, top - padding),
        min(image.width() - left + padding, right - left + padding * 2),
        min(image.height() - top + padding, bottom - top + padding * 2),
    )


def _palette_for(breed_id: str) -> tuple[QColor, QColor, QColor]:
    palettes = {
        "siamese": (QColor(222, 204, 171), QColor(248, 239, 215), QColor(72, 55, 50)),
        "american_shorthair": (QColor(162, 171, 176), QColor(231, 235, 236), QColor(83, 91, 98)),
        "ragdoll": (QColor(232, 222, 211), QColor(254, 248, 239), QColor(170, 134, 122)),
        "black": (QColor(28, 29, 34), QColor(54, 55, 62), QColor(8, 9, 13)),
        "lihua": (QColor(139, 116, 82), QColor(217, 198, 160), QColor(70, 54, 35)),
        "tortoiseshell": (QColor(86, 55, 40), QColor(210, 117, 58), QColor(32, 25, 21)),
    }
    return palettes.get(breed_id, palettes["american_shorthair"])


def _shade(base: QColor, luminance: int) -> QColor:
    factor = 0.72 + max(0, min(255, luminance)) / 255 * 0.55
    return QColor(
        max(0, min(255, round(base.red() * factor))),
        max(0, min(255, round(base.green() * factor))),
        max(0, min(255, round(base.blue() * factor))),
    )


def _ease_out(value: float) -> float:
    value = max(0, min(1, value))
    return 1 - (1 - value) * (1 - value)
