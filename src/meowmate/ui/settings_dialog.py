from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from src.meowmate.domain.cat_catalog import CAT_BREEDS
from src.meowmate.domain.models import AppSettings, CatStats


class SettingsDialog(QDialog):
    settings_changed = Signal()
    reset_requested = Signal()

    def __init__(self, settings: AppSettings, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("MeowMate 设置")
        self.setMinimumWidth(380)

        self.breed_box = QComboBox()
        for breed in CAT_BREEDS.values():
            self.breed_box.addItem(breed.display_name, breed.id)
        self.breed_box.setCurrentIndex(max(0, self.breed_box.findData(settings.breed_id)))

        self.top_check = QCheckBox("始终置顶")
        self.top_check.setChecked(settings.always_on_top)
        self.muted_check = QCheckBox("静音")
        self.muted_check.setChecked(settings.muted)

        self.scale_slider = self._slider(settings.scale, 0.7, 1.8)
        self.speed_slider = self._slider(settings.move_speed, 0.4, 2.0)
        self.intensity_slider = self._slider(settings.interaction_intensity, 0.3, 2.0)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignLeft)

        reset_button = QPushButton("重置宠物数据")
        close_button = QPushButton("完成")

        form = QFormLayout()
        form.addRow("猫咪", self.breed_box)
        form.addRow("大小", self.scale_slider)
        form.addRow("移动速度", self.speed_slider)
        form.addRow("互动强度", self.intensity_slider)
        form.addRow("", self.top_check)
        form.addRow("", self.muted_check)

        behavior_group = QGroupBox("偏好")
        behavior_group.setLayout(form)

        status_group = QGroupBox("当前状态")
        status_layout = QVBoxLayout()
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        root = QVBoxLayout()
        root.addWidget(behavior_group)
        root.addWidget(status_group)
        root.addLayout(button_layout)
        self.setLayout(root)

        self.breed_box.currentIndexChanged.connect(self._apply)
        self.top_check.toggled.connect(self._apply)
        self.muted_check.toggled.connect(self._apply)
        self.scale_slider.valueChanged.connect(self._apply)
        self.speed_slider.valueChanged.connect(self._apply)
        self.intensity_slider.valueChanged.connect(self._apply)
        reset_button.clicked.connect(self._reset)
        close_button.clicked.connect(self.accept)
        self.refresh_status()

    def refresh_status(self) -> None:
        stats = self.settings.stats
        breed = CAT_BREEDS[self.settings.breed_id]
        self.status_label.setText(
            f"品种：{breed.display_name}\n"
            f"性格：{breed.personality}\n"
            f"能量：{stats.energy} / 100\n"
            f"心情：{stats.mood} / 100\n"
            f"亲密度：{stats.affection} / 100\n"
            f"等级：Lv.{stats.level}"
        )

    def _apply(self) -> None:
        self.settings.breed_id = self.breed_box.currentData()
        self.settings.always_on_top = self.top_check.isChecked()
        self.settings.muted = self.muted_check.isChecked()
        self.settings.scale = self.scale_slider.value() / 100
        self.settings.move_speed = self.speed_slider.value() / 100
        self.settings.interaction_intensity = self.intensity_slider.value() / 100
        self.settings.clamp()
        self.refresh_status()
        self.settings_changed.emit()

    def _reset(self) -> None:
        self.settings.stats = CatStats()
        self.refresh_status()
        self.reset_requested.emit()

    @staticmethod
    def _slider(value: float, minimum: float, maximum: float) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(round(minimum * 100))
        slider.setMaximum(round(maximum * 100))
        slider.setValue(round(value * 100))
        return slider
