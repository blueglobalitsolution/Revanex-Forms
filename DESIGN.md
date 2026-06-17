# Design System Inspired by Home

> Auto-extracted from `https://reevanax.com/` on 2026-06-17

## 1. Visual Theme & Atmosphere

Friendly, approachable design with rounded shapes and generous whitespace.

The hero section leads with "Ready for your luxurious & unique experience?".

**Key Characteristics:**
- Roboto as the heading font (custom web font loaded via @font-face)
- Roboto as the body font for all running text
- Heading weight 600, letter-spacing 0.5px
- Light/white background (#ffffff) as the primary canvas
- Primary accent `#864d26` used for CTAs and brand highlights
- 3 shadow level(s) detected — tinted shadows
- Rounded corners (10px+) creating a friendly, approachable feel
- Tags: light, rounded, monochrome, sans-serif

## 2. Color Palette & Roles

### Primary
- **Primary Accent** (`#864d26`) · `--color-primary`: Brand color, CTA backgrounds, link text, interactive highlights.
- **Secondary Accent** (`#834c24`) · `--color-secondary`: Secondary brand, hover states, complementary highlights.
- **Background** (`#ffffff`) · `--color-bg`: Page background, primary canvas.
- **Background Secondary** (`#fbfbf2`) · `--color-bg-secondary`: Cards, surfaces, alternating sections.

### Text
- **Text Primary** (`#89868d`) · `--color-text`: Headings and body text.
- **Text Secondary** (`#666666`) · `--color-text-secondary`: Muted text, captions, placeholders.

### Borders & Surfaces
- **Border** (`#fbfbf2`) · `--color-border`: Dividers, outlines, input borders.

### Full Extracted Palette

| # | Hex | CSS Variable | Role | Area | Contrast |
|---|---|---|---|---|---|
| 1 | `#864d26` | `--palette-1` | block | large | text-light |
| 2 | `#fbfbf2` | `--palette-2` | section | large | text-dark |
| 3 | `#ceae80` | `--palette-3` | text-accent | large | text-dark |
| 4 | `#ffffff` | `--palette-4` | badge | medium | text-dark |
| 5 | `#5a321b` | `--palette-5` | text-accent | small | text-light |
| 6 | `#112337` | `--palette-6` | text-accent | small | text-light |

## 3. Typography Rules

- **Heading Font:** `Roboto` (web font)
- **Body Font:** `Roboto` (web font)

### Type Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing |
|---|---|---|---|---|---|
| H1 | Roboto | 45px | 600 | 45px | 0.5px |
| H2 | Sora | 22px | 500 | 22px | normal |
| H4 | Roboto | 21.112px | 400 | 29.76px | normal |
| Body | Roboto | 16px | 400 | 20.8px | normal |

### Type Scale

| Token | Size | Suggested Usage |
|---|---|---|
| Display | `70px` | headings |
| H1 | `50px` | headings |
| H2 | `45px` | headings |
| H3 | `30px` | headings |
| H4 | `25px` | headings |
| Body L | `22px` | body / supporting text |
| Body | `21.112px` | body / supporting text |
| Small | `20px` | body / supporting text |
| XS | `18px` | body / supporting text |
| Caption | `17px` | body / supporting text |

## 4. Component Stylings

### Primary Button

```css
.btn-primary {
  background: transparent;
  color: #89868d;
  border-radius: 0px;
  padding: 0px 0px;
  font-size: 16px;
  font-weight: 400;
  border: none;
  cursor: pointer;
}
```

### Filled Button

```css
.btn-filled {
  background: #ceae80;
  color: #864d26;
  border-radius: 0px;
  padding: 0px 25px;
  font-size: 17px;
  font-weight: 500;
  border: none;
  cursor: pointer;
}
```

### Filled Button 2

```css
.btn-filled-2 {
  background: #ceae80;
  color: #864d26;
  border-radius: 50px;
  padding: 12px 24px;
  font-size: 25px;
  font-weight: 700;
  border: none;
  cursor: pointer;
}
```

### Filled Button 3

```css
.btn-filled-3 {
  background: #864d26;
  color: #69727d;
  border-radius: 50px;
  padding: 0px 0px;
  font-size: 20px;
  font-weight: 400;
  border: none;
  cursor: pointer;
}
```

### Filled Button 4

```css
.btn-filled-4 {
  background: #25d366;
  color: #ffffff;
  border-radius: 50px;
  padding: 0px 0px;
  font-size: 16px;
  font-weight: 400;
  border: none;
  cursor: pointer;
}
```

### Filled Button 5

```css
.btn-filled-5 {
  background: #ceae80;
  color: #ffffff;
  border-radius: 20px;
  padding: 0px 0px;
  font-size: 16px;
  font-weight: 400;
  border: none;
  cursor: pointer;
}
```

## 5. Layout Principles

- **Base spacing unit:** `8px` — use multiples (16px, 24px, 32px, etc.)

### Spacing Scale (extracted from real elements)

| Token | Value | Role |
|---|---|---|
| spacing-1 | `8px` | element |
| spacing-2 | `9.88875px` | element |
| spacing-3 | `10px` | element |
| spacing-4 | `15px` | element |
| spacing-5 | `30px` | card |
| spacing-6 | `20px` | element |
| spacing-7 | `25px` | card |
| spacing-8 | `80px` | section |

### Border Radius Scale

| Token | Value | Element |
|---|---|---|
| radius-button | `10px` | button |
| radius-subtle | `3px` | subtle |
| radius-card | `50px` | card |
| radius-subtle | `5px` | subtle |
| radius-subtle | `4px` | subtle |
| radius-button | `15px` | button |

## 6. Depth & Elevation

| Level | Shadow | Usage |
|---|---|---|
| Deep | `rgba(0, 0, 0, 0.07) 0px 0px 50px 0px` | Hero sections, deep layers |
| Low | `rgba(18, 25, 97, 0.08) 0px 1px 4px 0px` | Cards, subtle elevation |
| Low | `rgb(134, 77, 38) 0px 0px 3px 0px` | Cards, subtle elevation |

> **Note:** This site uses chromatic (color-tinted) shadows rather than pure black — this is a deliberate brand choice that adds warmth to elevation.

## 7. Do's and Don'ts

### Do
- Use `#ffffff` as the primary background color
- Use `Roboto` for all headings and `Roboto` for body text
- Use `#864d26` as the single dominant accent/CTA color
- Maintain `8px` as the base spacing unit — all gaps should be multiples
- Use rounded corners (`10px`+) consistently for all interactive elements
- Stick to grayscale + `#864d26` accent — avoid color overload
- Apply the shadow system for elevation — use the extracted shadow values
- Use weight 600 for headings to match the brand's typographic voice

### Don't
- Don't use colors outside the extracted palette without justification
- Don't substitute Roboto/Roboto with generic alternatives
- Don't use irregular spacing — stick to 8px grid
- Don't use dark/black backgrounds — this is a light-themed design
- Don't use sharp corners — they feel hostile in this rounded design language
- Don't add additional saturated colors beyond the primary accent
- Don't use pure black (#000000) for text — use `#89868d` instead
- Don't add decorative elements not present in the original design — no badges, ribbons, banners, or ornaments unless the source site uses them
- Don't invent UI patterns the source site doesn't have — if the original has no NEW badge, don't add one just because a red is in the palette

## 8. Responsive Behavior

| Breakpoint | Width | Notes |
|---|---|---|
| Mobile | < 640px | Single column, stack sections, reduce font sizes ~80% |
| Tablet | 640–1024px | 2-column where appropriate, maintain spacing ratios |
| Desktop | 1024–1440px | Full layout as designed |
| Wide | > 1440px | Max-width container, center content |

- Touch targets: minimum 44×44px on mobile
- Maintain 8px base unit across breakpoints — only scale multipliers

## 9. Agent Prompt Guide

### Quick Color Reference

```
Background:  #ffffff
Text:        #89868d
Accent:      #864d26
Secondary:   #834c24
Border:      #fbfbf2
```

### Example Prompts

1. "Build a hero section with a `#ffffff` background, `Roboto` heading in `#89868d`, and a `#864d26` CTA button with 0px radius."
2. "Create a pricing card using background `#fbfbf2`, border `#fbfbf2`, `Roboto` for text, and 24px padding."
3. "Design a navigation bar — `#ffffff` background, `#89868d` links, `#864d26` for active state."
4. "Build a feature grid with 3 columns, 24px gap, each card using the card component style."
5. "Create a footer with `#89868d` background, `#ffffff` text, and 16px padding."

### Iteration Guide

1. Start with layout structure (sections, grid, spacing)
2. Apply colors from the palette — background first, then text, then accents
3. Set typography — font families, sizes from the type scale, weights
4. Add components — buttons, cards, inputs using the specs above
5. Apply border-radius consistently across all elements
6. Add shadows for depth — use the extracted shadow values, not defaults
7. Check responsive behavior — test mobile and tablet layouts
8. Final pass — verify all colors match, spacing is consistent, fonts are correct

## 10. CSS Custom Properties

> 101 custom properties extracted from `:root` / `html` stylesheets.

### Color Variables

| Variable | Value |
|---|---|
| `--wp-admin-theme-color` | `#3858e9` |
| `--wp-admin-theme-color-darker-10` | `#2145e6` |
| `--wp-admin-theme-color-darker-20` | `#183ad6` |
| `--wp-block-synced-color` | `#7a00df` |
| `--wp--preset--color--black` | `#000000` |
| `--wp--preset--color--cyan-bluish-gray` | `#abb8c3` |
| `--wp--preset--color--white` | `#ffffff` |
| `--wp--preset--color--pale-pink` | `#f78da7` |
| `--wp--preset--color--vivid-red` | `#cf2e2e` |
| `--wp--preset--color--luminous-vivid-orange` | `#ff6900` |
| `--wp--preset--color--luminous-vivid-amber` | `#fcb900` |
| `--wp--preset--color--light-green-cyan` | `#7bdcb5` |
| `--wp--preset--color--vivid-green-cyan` | `#00d084` |
| `--wp--preset--color--pale-cyan-blue` | `#8ed1fc` |
| `--wp--preset--color--vivid-cyan-blue` | `#0693e3` |
| `--wp--preset--color--vivid-purple` | `#9b51e0` |
| `--wp--preset--gradient--vivid-cyan-blue-to-vivid-purple` | `linear-gradient(135deg,rgba(6,147,227,1) 0%,rgb(155,81,224) 100%)` |
| `--wp--preset--gradient--light-green-cyan-to-vivid-green-cyan` | `linear-gradient(135deg,rgb(122,220,180) 0%,rgb(0,208,130) 100%)` |
| `--wp--preset--gradient--luminous-vivid-amber-to-luminous-vivid-orange` | `linear-gradient(135deg,rgba(252,185,0,1) 0%,rgba(255,105,0,1) 100%)` |
| `--wp--preset--gradient--luminous-vivid-orange-to-vivid-red` | `linear-gradient(135deg,rgba(255,105,0,1) 0%,rgb(207,46,46) 100%)` |
| `--wp--preset--gradient--very-light-gray-to-cyan-bluish-gray` | `linear-gradient(135deg,rgb(238,238,238) 0%,rgb(169,184,195) 100%)` |
| `--wp--preset--gradient--cool-to-warm-spectrum` | `linear-gradient(135deg,rgb(74,234,220) 0%,rgb(151,120,209) 20%,rgb(207,42,186) 40%,rgb(238,44,130) 60%,rgb(251,105,98) 80%,rgb(254,248,76) 100%)` |
| `--wp--preset--gradient--blush-light-purple` | `linear-gradient(135deg,rgb(255,206,236) 0%,rgb(152,150,240) 100%)` |
| `--wp--preset--gradient--blush-bordeaux` | `linear-gradient(135deg,rgb(254,205,165) 0%,rgb(254,45,45) 50%,rgb(107,0,62) 100%)` |
| `--wp--preset--gradient--luminous-dusk` | `linear-gradient(135deg,rgb(255,203,112) 0%,rgb(199,81,192) 50%,rgb(65,88,208) 100%)` |
| `--wp--preset--gradient--pale-ocean` | `linear-gradient(135deg,rgb(255,245,203) 0%,rgb(182,227,212) 50%,rgb(51,167,181) 100%)` |
| `--wp--preset--gradient--electric-grass` | `linear-gradient(135deg,rgb(202,248,128) 0%,rgb(113,206,126) 100%)` |
| `--wp--preset--gradient--midnight` | `linear-gradient(135deg,rgb(2,3,129) 0%,rgb(40,116,252) 100%)` |
| `--wp--preset--shadow--natural` | `6px 6px 9px rgba(0, 0, 0, 0.2)` |
| `--wp--preset--shadow--deep` | `12px 12px 50px rgba(0, 0, 0, 0.4)` |
| ... | *(11 more)* |

### Spacing Variables

| Variable | Value |
|---|---|
| `--direction-multiplier` | `1` |
| `--wp-admin-border-width-focus` | `2px` |
| `--wp--preset--aspect-ratio--square` | `1` |
| `--wp--preset--spacing--20` | `0.44rem` |
| `--wp--preset--spacing--30` | `0.67rem` |
| `--wp--preset--spacing--40` | `1rem` |
| `--wp--preset--spacing--50` | `1.5rem` |
| `--wp--preset--spacing--60` | `2.25rem` |
| `--wp--preset--spacing--70` | `3.38rem` |
| `--wp--preset--spacing--80` | `5.06rem` |
| `--iti-spacer-horizontal` | `8px` |
| `--iti-flag-height` | `15px` |
| `--iti-flag-width` | `20px` |
| `--iti-border-width` | `1px` |
| `--iti-arrow-height` | `4px` |
| `--iti-arrow-width` | `6px` |
| `--iti-arrow-padding` | `6px` |
| `--iti-input-padding` | `6px` |
| `--iti-flag-sprite-width` | `5762px` |
| `--iti-flag-sprite-height` | `15px` |
| ... | *(5 more)* |

### Typography Variables

| Variable | Value |
|---|---|
| `--wp--preset--font-size--small` | `13px` |
| `--wp--preset--font-size--medium` | `20px` |
| `--wp--preset--font-size--large` | `36px` |
| `--wp--preset--font-size--x-large` | `42px` |
| `--primary-font` | `Roboto` |
| `--font-size` | `16px` |
| `--line-height` | `1.86em` |
| `--letter-spacing` | `0px` |
| `--secondary-font` | `Roboto` |

### Other Variables

| Variable | Value |
|---|---|
| `--page-title-display` | `block` |
| `--wp-admin-theme-color--rgb` | `56,88,233` |
| `--wp-admin-theme-color-darker-10--rgb` | `33,69,230` |
| `--wp-admin-theme-color-darker-20--rgb` | `24,58,214` |
| `--wp-block-synced-color--rgb` | `122,0,223` |
| `--wp-bound-block-color` | `var(--wp-block-synced-color)` |
| `--wp--preset--aspect-ratio--4-3` | `4/3` |
| `--wp--preset--aspect-ratio--3-4` | `3/4` |
| `--wp--preset--aspect-ratio--3-2` | `3/2` |
| `--wp--preset--aspect-ratio--2-3` | `2/3` |
| `--wp--preset--aspect-ratio--16-9` | `16/9` |
| `--wp--preset--aspect-ratio--9-16` | `9/16` |
| `--iti-border-color` | `var(--iti-border-gray)` |
| `--iti-dialcode-color` | `var(--iti-text-gray)` |
| `--iti-dropdown-bg` | `white` |
| ... | *(11 more)* |
