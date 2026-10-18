# Visual themes

The active theme is **Vermeer**. **Basquiat** is preserved as a complete named
stylesheet, byte-for-byte matching the previous theme, with its native iPhone
colours saved alongside the Vermeer values. Neither theme reproduces artwork;
these are interpreted palettes adapted for legible interfaces, not exact samples.

## Vermeer — active

Inspired by the blue-and-yellow pairing in
[Girl with a Pearl Earring](https://www.mauritshuis.nl/en/our-collection/artworks/670-girl-with-a-pearl-earring)
and the museum’s research into
[Vermeer’s ultramarine](https://www.mauritshuis.nl/en/our-collection/restoration-and-research/closer-to-vermeer-and-the-girl/girl-with-a-blog/blue-pigment-girl-with-a-pearl-earring-vermeer).

| Role | Colour |
| --- | --- |
| Header | Deep ultramarine `#233e68` |
| Primary actions and links | Blue `#28518a` |
| Active navigation and highlights | Ochre `#d6b35c` |
| Completed progress | Muted green `#466758` |
| Earth accents | Burnt earth `#8a4c34` |
| Page background | Warm ivory `#f6f0e3` |
| Reading surfaces | Pearl `#fffdf6` |
| Text | Warm charcoal `#302c24` |

Subtle borders and soft shadows replace the stronger graphic edges. Compact
layouts, typography, logo and labelled blue-to-purple difficulty scale remain.

## Basquiat — saved

Inspired by Basquiat’s
[Modena paintings](https://www.fondationbeyeler.ch/en/exhibitions/jean-michel-basquiat).
The complete stylesheet is `src/palettes/basquiat.css` inside the WordPress theme.
It retains the yellow `#ffd437` header, cobalt `#1743c5`, vermilion `#c73923`,
teal `#007b74`, warm cream `#fff6e4`, light reading surface `#fffcf5`,
near-black `#191714` outlines and offset shadows. The original implementation
is also preserved in commit `bf598ab`.

## Selecting a saved theme

1. In `wordpress/themes/flexagon/src/theme-palette.css`, import
   `./palettes/vermeer.css` or `./palettes/basquiat.css`.
2. Match the theme-colour metadata in the theme’s `index.php` to its header:
   Vermeer `#233e68`, Basquiat `#ffd437`.
3. Set `CommunityWebsitePalette.current` in
   `ios/Flexagon/App/CommunityWebsiteView.swift` to `.vermeer` or `.basquiat`.
4. Run `npm run build:web` and `npm run package:web`, then rebuild the Debug iPhone
   app when changing its native controls.

The connected Debug app loads the same website styles. The inherited Release
reader is not part of this theme change. This is a developer theme selection;
no preference control was added to the public interface.
