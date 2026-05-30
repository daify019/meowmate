from __future__ import annotations

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import QMainWindow, QMenu

from src.meowmate.domain.cat_catalog import get_breed
from src.meowmate.domain.models import AppSettings, CatAction
from src.meowmate.services.behavior import BehaviorEngine
from src.meowmate.services.storage import SettingsStore
from src.meowmate.ui.cat_widget import CatWidget
from src.meowmate.ui.settings_dialog import SettingsDialog


class CatWindow(QMainWindow):
    def __init__(self, settings: AppSettings, store: SettingsStore) -> None:
        super().__init__()
        self.settings = settings
        self.store = store
        self.engine = BehaviorEngine(settings, get_breed(settings.breed_id))
        self.cat = CatWidget(self.engine.breed, self.engine.state)
        self.setCentralWidget(self.cat)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.Tool, True)
        self._apply_top_flag()
        self.cat.set_scale(settings.scale)
        self.setFixedSize(self.cat.size())

        self.cat.clicked.connect(self._clicked)
        self.cat.drag_started.connect(self.engine.drag_started)
        self.cat.drag_finished.connect(self._drag_finished)
        self.cat.moved.connect(self._move_to)

        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(83)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start()

        self.behavior_timer = QTimer(self)
        self.behavior_timer.setInterval(3600)
        self.behavior_timer.timeout.connect(self._next_behavior)
        self.behavior_timer.start()

        self.save_timer = QTimer(self)
        self.save_timer.setInterval(5000)
        self.save_timer.timeout.connect(self._save_position)
        self.save_timer.start()

        self._restore_position()

    def contextMenuEvent(self, event) -> None:  # type: ignore[override]
        menu = QMenu(self)
        tease_action = QAction("逗逗它", self)
        feed_action = QAction("喂小鱼干", self)
        sleep_action = QAction("让它睡一会儿", self)
        special_action = QAction("特殊动作", self)
        settings_action = QAction("设置", self)
        quit_action = QAction("退出", self)

        tease_action.triggered.connect(self._tease)
        feed_action.triggered.connect(self._feed)
        sleep_action.triggered.connect(self._sleep)
        special_action.triggered.connect(self._special)
        settings_action.triggered.connect(self._open_settings)
        quit_action.triggered.connect(self._quit)

        for action in [tease_action, feed_action, sleep_action, special_action]:
            menu.addAction(action)
        menu.addSeparator()
        menu.addAction(settings_action)
        menu.addAction(quit_action)
        menu.exec(event.globalPos())

    def _animate(self) -> None:
        self.engine.tick_animation()
        self._maybe_move()
        self.cat.update()

    def _maybe_move(self) -> None:
        if self.engine.state.action != CatAction.WALK:
            return
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return
        bounds = screen.availableGeometry()
        step = round(2 * self.settings.move_speed * self.engine.breed.speed_bias)
        next_x = self.x() + step * self.engine.state.facing
        if next_x < bounds.left() or next_x + self.width() > bounds.right():
            self.engine.state.facing *= -1
            next_x = self.x() + step * self.engine.state.facing
        self.move(next_x, self.y())

    def _next_behavior(self) -> None:
        self.engine.choose_next_action()
        self._save_position()

    def _clicked(self) -> None:
        self.engine.click()
        self._save_position()

    def _drag_finished(self) -> None:
        self.engine.drag_finished()
        self._save_position()

    def _move_to(self, point: QPoint) -> None:
        self.move(point)

    def _tease(self) -> None:
        self.engine.tease()
        self._save_position()

    def _feed(self) -> None:
        self.engine.feed()
        self._save_position()

    def _sleep(self) -> None:
        self.engine.sleep()
        self._save_position()

    def _special(self) -> None:
        self.engine.special()
        self._save_position()

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.reset_requested.connect(self._save_position)
        dialog.exec()
        self._apply_settings()

    def _apply_settings(self) -> None:
        self.settings.clamp()
        breed = get_breed(self.settings.breed_id)
        self.engine.update_breed(breed)
        self.cat.set_breed(breed)
        self.cat.set_scale(self.settings.scale)
        self.setFixedSize(self.cat.size())
        self._apply_top_flag()
        self.store.save(self.settings)

    def _apply_top_flag(self) -> None:
        was_visible = self.isVisible()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.settings.always_on_top)
        if was_visible:
            self.show()

    def _restore_position(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            self.move(100, 100)
            return
        bounds = screen.availableGeometry()
        if self.settings.x is None or self.settings.y is None:
            self.move(bounds.right() - self.width() - 40, bounds.bottom() - self.height() - 24)
        else:
            self.move(self.settings.x, self.settings.y)

    def _save_position(self) -> None:
        self.settings.x = self.x()
        self.settings.y = self.y()
        self.store.save(self.settings)

    def _quit(self) -> None:
        self._save_position()
        QGuiApplication.quit()
