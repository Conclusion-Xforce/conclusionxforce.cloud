# Homepage Redesign

**Date:** 2026-05-13
**Status:** Approved

## Problem

The current `layouts/hextra-home.html` override does not call `{{ .Content }}`, so the
hero headline, subtitle, CTA button, and welcome paragraph defined in `content/_index.md`
are never rendered. The homepage only shows three information sections (latest post, tag
cloud, author index) with no identity or context for first-time visitors.

The section labels are visually weak, and the site has no defined color identity, font
pairing, or visual motif.

## Goal

Restore the original hero experience while keeping the three content sections. Apply a
dark, technical-premium visual style site-wide, and add clear visual structure to the
homepage so visitors can scan it at a glance.

## Design

### Page structure (top to bottom)

1. **Hero** — rendered via `{{ .Content }}` from `content/_index.md`
   - Headline: "Conclusion Xforce Tech Playground" (`hextra/hero-headline`)
   - Subtitle: "A space to experiment and play, for enthusiasts by enthusiasts." (`hextra/hero-subtitle`)
   - CTA button: "Jump to latest blogs" → `/blog` (`hextra/hero-button`)
   - Welcome paragraph: plain markdown text below the button

2. `<hr>` divider

3. **Latest Post** — `<h2>` section heading, post card with thin left accent border

4. `<hr>` divider

5. **Browse by Tag** — `<h2>` section heading, tag chips

6. `<hr>` divider

7. **Authors** — `<h2>` section heading, avatar grid with thin left accent border per author card

### Color scheme

Dark, technical-premium palette applied site-wide via CSS custom properties in
`static/css/custom-styles.css`.

| Role | Value |
|------|-------|
| Background | `#040720` |
| Primary text | `#ffffff` |
| Primary accent | `#0097B2` (teal) |
| Secondary accent | `#5A3F8C` (purple) |
| Dividers / subtle borders | white at 10–15% opacity |

The primary accent (`#0097B2`) is used for: CTA button, read-more links, tag chip borders
and text, thin card accent lines.

The secondary accent (`#5A3F8C`) is used for: author card left border, hover states on
the tag chips.

### Typography

Fonts loaded via Google Fonts `@import` in `static/css/custom-styles.css`.

| Role | Font |
|------|------|
| Headings (`h1`–`h4`, `.hextra-hero-headline`) | Montserrat 700 |
| Body / UI text | Montserrat 300 (Light) |

Apply via CSS `font-family` on `body` (Montserrat Light) and heading selectors
(Montserrat 700).

### Visual motif — thin accent lines on content cards

Every discrete content card on the homepage gets a 3 px left border in an accent color:

- **Latest post card** — `border-left: 3px solid #0097B2`
- **Author cards** — `border-left: 3px solid #5A3F8C`
- **Tag chips** — instead of a left border (chips are inline), use `border: 1px solid #0097B2` with `color: #0097B2`; on hover, fill with `#0097B2` and flip text to `#040720`

The cards themselves get a subtle background (`rgba(255,255,255,0.04)`) and `border-radius`
to lift them off the page background.

### Section headings

Replace the current small uppercase labels with `<h2>` at a readable size, white text:

```html
<h2 class="homepage-section-heading">Latest Post</h2>
```

Styled in CSS:
```css
.homepage-section-heading {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 1.5rem;
  color: #ffffff;
  margin-bottom: 1rem;
}
```

### Dividers

```html
<hr class="homepage-divider" />
```

```css
.homepage-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  margin: 2.5rem 0;
}
```

## Changes required

| File | Change |
|------|--------|
| `layouts/hextra-home.html` | Add `{{ .Content }}` before the sections |
| `layouts/hextra-home.html` | Replace `<p class="text-xs uppercase …">` labels with `<h2 class="homepage-section-heading">` |
| `layouts/hextra-home.html` | Add `<hr class="homepage-divider">` between hero and each section |
| `layouts/hextra-home.html` | Wrap latest post content in a card `<div>` with accent left border |
| `layouts/hextra-home.html` | Wrap each author in a card `<div>` with secondary accent left border |
| `static/css/custom-styles.css` | `@import` Montserrat from Google Fonts |
| `static/css/custom-styles.css` | Override Hextra CSS variables for background, text, and accent colors |
| `static/css/custom-styles.css` | Add `body` font-family (Montserrat Light) and heading font-family (Montserrat 700) |
| `static/css/custom-styles.css` | Add `.homepage-section-heading`, `.homepage-divider`, card, and tag chip styles |

`content/_index.md` — **no changes needed.**

## Out of scope

- Changes to blog list, single post, or author page layouts
- Mobile-specific layout changes beyond what the styles naturally provide
- Custom icon set or iconography
