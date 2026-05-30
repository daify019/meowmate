from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QDialog

from src.meowmate.services.storage import SettingsStore
from src.meowmate.ui.main_window import CatWindow
from src.meowmate.ui.onboarding import OnboardingDialog


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("MeowMate")
    app.setQuitOnLastWindowClosed(False)

    store = SettingsStore()
    first_run = not store.path.exists()
    settings = store.load()

    if first_run:
        onboarding = OnboardingDialog(settings)
        if onboarding.exec() != QDialog.Accepted:
            return 0
        store.save(settings)

    window = CatWindow(settings, store)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
