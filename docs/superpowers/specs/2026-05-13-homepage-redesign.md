# Homepage Redesign

**Date:** 2026-05-13
**Status:** Approved

## Problem

The current `layouts/hextra-home.html` override does not call `{{ .Content }}`, so the
hero headline, subtitle, CTA button, and welcome paragraph defined in `content/_index.md`
are never rendered. The homepage only shows three information sections (latest post, tag
cloud, author index) with no identity or context for first-time visitors.

The section labels are also visually weak — small, uppercase, low-contrast text that does
not clearly delineate the page structure.

## Goal

Restore the original hero experience while keeping the three content sections, and add
clear visual structure so visitors can scan the page at a glance.

## Design

### Page structure (top to bottom)

1. **Hero** — rendered via `{{ .Content }}` from `content/_index.md`
   - Headline: "Conclusion Xforce Tech Playground" (`hextra/hero-headline`)
   - Subtitle: "A space to experiment and play, for enthusiasts by enthusiasts." (`hextra/hero-subtitle`)
   - CTA button: "Jump to latest blogs" → `/blog` (`hextra/hero-button`)
   - Welcome paragraph: plain markdown text below the button

2. `<hr>` divider

3. **Latest Post** — `<h2>` section heading, then title / date / author / summary / read-more link

4. `<hr>` divider

5. **Browse by Tag** — `<h2>` section heading, then tag chips (unchanged content)

6. `<hr>` divider

7. **Authors** — `<h2>` section heading, then avatar grid (unchanged content)

### Changes required

| File | Change |
|------|--------|
| `layouts/hextra-home.html` | Add `{{ .Content }}` before the sections |
| `layouts/hextra-home.html` | Replace the three `<p class="text-xs uppercase …">` labels with `<h2>` tags |
| `layouts/hextra-home.html` | Add `<hr>` dividers between hero and each section |

`content/_index.md` — **no changes needed.**

### Section heading style

Replace the existing label pattern:
```html
<p class="hx:text-xs hx:font-semibold hx:uppercase hx:tracking-wide hx:text-slate-500 …">
```
With a proper heading:
```html
<h2 class="hx:text-2xl hx:font-bold hx:tracking-tight hx:text-slate-900 hx:dark:text-slate-100">
```

### Divider style

```html
<hr class="hx:my-10 hx:border-slate-200 hx:dark:border-slate-700" />
```

## Out of scope

- Changes to tag chip or author avatar styles
- Mobile-specific layout changes
- Any changes to blog list, single post, or author pages
