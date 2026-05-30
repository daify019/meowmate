from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from src.meowmate.domain.cat_catalog import CAT_BREEDS
from src.meowmate.domain.models import AppSettings
from src.meowmate.services.behavior import BehaviorState
from src.meowmate.ui.cat_widget import CatWidget


class OnboardingDialog(QDialog):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self.setWindowTitle("选择你的桌面猫咪伙伴")
        self.setMinimumSize(620, 360)

        self.preview_state = BehaviorState()
        self.preview = CatWidget(CAT_BREEDS[settings.breed_id], self.preview_state)
        self.preview.set_scale(1.2)
        self.preview.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.breed_box = QComboBox()
        for breed in CAT_BREEDS.values():
            self.breed_box.addItem(breed.display_name, breed.id)
        self.breed_box.setCurrentIndex(max(0, self.breed_box.findData(settings.breed_id)))

        self.description = QTextEdit()
        self.description.setReadOnly(True)
        self.description.setMinimumHeight(120)

        start_button = QPushButton("带它回桌面")
        start_button.setDefault(True)

        title = QLabel("选择你的桌面猫咪伙伴")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")

        right = QVBoxLayout()
        right.addWidget(title)
        right.addWidget(QLabel("猫咪品种"))
        right.addWidget(self.breed_box)
        right.addWidget(self.description)
        right.addStretch()
        right.addWidget(start_button)

        root = QHBoxLayout()
        root.addWidget(self.preview, 1)
        root.addLayout(right, 1)
        self.setLayout(root)

        self.breed_box.currentIndexChanged.connect(self._changed)
        start_button.clicked.connect(self.accept)
        self._changed()

    def _changed(self) -> None:
        breed_id = self.breed_box.currentData()
        self.settings.breed_id = breed_id
        breed = CAT_BREEDS[breed_id]
        self.preview.set_breed(breed)
        self.description.setText(
            f"{breed.display_name}\n\n"
            f"性格：{breed.personality}\n"
            f"行为：{breed.behavior_style}\n"
            f"特殊动作：{breed.special_action}"
        )
