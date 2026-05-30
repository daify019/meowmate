# Assets

## Tiny Kitten Sprite

- Source: https://opengameart.org/content/tiny-kitten-game-sprite
- Author: Segel
- License: CC0
- Local path: `assets/cats/tiny_kitten_cc0/TINY CAT SPRITE`

The runtime maps MeowMate actions to this sprite pack:

- `idle`, `happy`: `01_Idle`
- `walk`: `02_Run`
- `clicked`, `dragged`, `annoyed`: `04_Hurt`
- `sleep`, ragdoll special: `05_Dead`
- other special actions: `03_Jump/01_Up`

Breed-specific looks are produced by recoloring the same transparent PNG frames at load time. Replacing this pack with a bespoke art set only requires adding equivalent action folders and updating `CatWidget._clip_for`.
