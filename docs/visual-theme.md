# Visual theme

The website uses an interpreted palette inspired by Jean-Michel Basquiat’s
[Modena paintings](https://www.fondationbeyeler.ch/en/exhibitions/jean-michel-basquiat),
with colours adjusted for clear text and controls. These are design choices, not
exact samples from the paintings; no artwork is reproduced in the application.

| Role | Colour |
| --- | --- |
| Header and highlights | Yellow `#ffd437` |
| Primary actions and links | Cobalt `#1743c5` |
| Active navigation and accents | Vermilion `#c73923` |
| Completed progress | Teal `#007b74` |
| Page background | Warm cream `#fff6e4` |
| Reading surfaces | Light cream `#fffcf5` |
| Text and outlines | Near-black `#191714` |

Black outlines and small offset shadows distinguish controls. Reading panels
remain light. Difficulty retains a labelled blue-to-purple progression from 1
to 5, independent of the accent palette.

Shared overrides live in `wordpress/themes/le-probleme-du-jour/src/theme-palette.css`.
The connected Debug iPhone client loads these same website styles; its native
navigation bar uses matching cream and cobalt. The inherited Release reader is
not part of this theme change.
