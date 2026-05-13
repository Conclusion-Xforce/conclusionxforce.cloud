# Homepage Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the hero section on the homepage, apply a dark technical-premium visual style site-wide, and add clear structural hierarchy with accent-bordered content cards.

**Architecture:** Three-file change — `hugo.yaml` locks the theme to dark mode, `assets/custom.css` provides all custom styles (fonts, colors, components), and `layouts/hextra-home.html` is updated to render the hero content and use new CSS classes for headings, dividers, and cards.

**Tech Stack:** Hugo 0.145.0, Hextra theme, Tailwind CSS (via Hextra), Google Fonts (Montserrat)

---

### Task 1: Force dark theme

**Files:**
- Modify: `hugo.yaml` lines 108–111

- [ ] **Step 1: Update theme params**

In `hugo.yaml`, replace:
```yaml
  theme:
    # light | dark | system
    default: system
    displayToggle: true
```
With:
```yaml
  theme:
    # light | dark | system
    default: dark
    displayToggle: false
```

- [ ] **Step 2: Verify**

Run `hugo server` and open `http://localhost:1313/`. Confirm the page renders in dark mode and the light/dark toggle is gone from the navbar.

- [ ] **Step 3: Commit**

```bash
git add hugo.yaml
git commit -m "feat: force dark theme site-wide"
```

---

### Task 2: Apply custom styles (fonts, colors, homepage components)

**Files:**
- Modify: `assets/custom.css`

- [ ] **Step 1: Write the full custom.css**

Replace the entire contents of `assets/custom.css` with:

```css
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,700;1,300&display=swap');

/* ── Typography ─────────────────────────────────────────────── */

body {
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
}

/* ── Dark color scheme ──────────────────────────────────────── */

/* Background: override Hextra's dark neutral */
html, body {
  background-color: #040720 !important;
  color: #ffffff;
}

/* Navbar */
header nav,
.nav-container {
  background-color: rgba(4, 7, 32, 0.92) !important;
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}

/* Sidebar and content area backgrounds */
aside,
.hextra-scrollbar {
  background-color: #040720 !important;
}

/* Footer */
footer {
  background-color: #040720 !important;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* Links — accent color */
article a,
main a {
  color: #0097B2;
}

article a:hover,
main a:hover {
  color: #5A3F8C;
}

/* ── Homepage component styles ──────────────────────────────── */

.homepage-section-heading {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 1.5rem;
  color: #ffffff;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.homepage-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  margin: 2.5rem 0;
}

/* Latest post card — primary accent left border */
.homepage-post-card {
  border-left: 3px solid #0097B2;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 0 8px 8px 0;
  padding: 1.25rem 1.5rem;
}

.homepage-post-card h3 {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 1.25rem;
  color: #ffffff;
}

.homepage-post-card a {
  color: inherit !important;
  text-decoration: none;
}

.homepage-post-card a:hover {
  color: #0097B2 !important;
}

.homepage-read-more {
  display: inline-block;
  margin-top: 1rem;
  color: #0097B2 !important;
  text-decoration: underline;
  text-underline-offset: 3px;
  font-weight: 700;
  font-size: 0.875rem;
}

.homepage-read-more:hover {
  color: #5A3F8C !important;
}

/* Author cards — secondary accent left border */
.homepage-author-card {
  border-left: 3px solid #5A3F8C;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 0 8px 8px 0;
  padding: 0.625rem 1rem;
}

.homepage-author-card a {
  color: #ffffff !important;
  text-decoration: none !important;
}

.homepage-author-card a:hover {
  color: #0097B2 !important;
}

/* Tag chips — outlined in primary accent, fill on hover */
.homepage-tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  border: 1px solid #0097B2;
  border-radius: 9999px;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: #0097B2;
  text-decoration: none;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.homepage-tag-chip:hover {
  background-color: #0097B2;
  color: #040720 !important;
}

.homepage-tag-chip span {
  opacity: 0.6;
}
```

- [ ] **Step 2: Verify typography**

Run `hugo server` and open `http://localhost:1313/`. Confirm:
- Headings render in Montserrat Bold
- Body text renders in Montserrat Light
- Background is `#040720` (very dark navy/black)
- Navbar background matches

- [ ] **Step 3: Commit**

```bash
git add assets/custom.css
git commit -m "feat: apply dark color scheme, Montserrat typography, homepage component styles"
```

---

### Task 3: Update homepage layout template

**Files:**
- Modify: `layouts/hextra-home.html`

- [ ] **Step 1: Rewrite the template**

Replace the entire contents of `layouts/hextra-home.html` with:

```html
{{ define "main" }}
  <div class="hx:mx-auto hx:flex {{ partial `utils/page-width` . }}">
    {{ partial "sidebar.html" (dict "context" . "disableSidebar" true "displayPlaceholder" true) }}
    <article class="hx:w-full hx:break-words hx:flex hx:min-h-[calc(100vh-var(--navbar-height))] hx:min-w-0 hx:justify-center hx:pb-8 hx:pr-[calc(env(safe-area-inset-right)-1.5rem)]">
      <main class="hx:w-full hx:min-w-0 hx:max-w-6xl hx:px-6 hx:pt-4 hx:md:px-12">

        {{/* ── Hero (headline, subtitle, CTA button, welcome text) ── */}}
        {{ .Content }}

        {{/* ── Latest post ────────────────────────────────────────── */}}
        <hr class="homepage-divider" />
        <section class="hx:mb-14">
          <h2 class="homepage-section-heading">Latest Post</h2>
          {{- $latestPost := index (where .Site.RegularPages "Section" "blog").ByDate.Reverse 0 -}}
          {{- with $latestPost }}
            <div class="homepage-post-card">
              <h3><a href="{{ .RelPermalink }}">{{ .Title }}</a></h3>
              <p class="hx:opacity-50 hx:text-sm hx:mt-2">
                {{ partial "utils/format-date" .Date -}}
                {{- with .Params.authors }} · {{ delimit . ", " }}{{ end }}
              </p>
              <p class="hx:mt-4 hx:leading-7 hx:opacity-80">{{ .Summary }}</p>
              <a class="homepage-read-more" href="{{ .RelPermalink }}">Continue reading →</a>
            </div>
          {{- end }}
        </section>

        {{/* ── Tag cloud ──────────────────────────────────────────── */}}
        <hr class="homepage-divider" />
        <section class="hx:mb-14">
          <h2 class="homepage-section-heading">Browse by Tag</h2>
          <div class="hx:flex hx:flex-wrap hx:gap-2">
            {{- range .Site.Taxonomies.tags.Alphabetical }}
              <a href="{{ .Page.RelPermalink }}" class="homepage-tag-chip">
                #{{ .Page.Title }}<span>{{ .Count }}</span>
              </a>
            {{- end }}
          </div>
        </section>

        {{/* ── Author index ────────────────────────────────────────── */}}
        <hr class="homepage-divider" />
        <section class="hx:mb-14">
          <h2 class="homepage-section-heading">Authors</h2>
          <div class="hx:flex hx:flex-wrap hx:gap-4">
            {{- $authorSection := .Site.GetPage "/author" -}}
            {{- if $authorSection -}}
              {{- range $authorSection.Sections.ByTitle }}
                {{- $img := .Resources.GetMatch "*.png" -}}
                {{- if not $img -}}{{- $img = .Resources.GetMatch "*.jpg" -}}{{- end -}}
                <div class="homepage-author-card">
                  <a href="{{ .RelPermalink }}" class="hx:flex hx:flex-row hx:items-center hx:gap-3 hx:no-underline">
                    {{- if $img }}
                      <img src="{{ $img.RelPermalink }}" alt="{{ .Title }}"
                           class="hx:h-10 hx:w-10 hx:rounded-full hx:object-cover" loading="lazy" />
                    {{- else }}
                      <div class="hx:h-10 hx:w-10 hx:rounded-full hx:bg-slate-700"></div>
                    {{- end }}
                    <span class="hx:text-sm hx:font-medium">{{ .Title }}</span>
                  </a>
                </div>
              {{- end }}
            {{- end }}
          </div>
        </section>

      </main>
    </article>
    <div class="hx:max-xl:hidden hx:h-0 hx:w-64 hx:shrink-0"></div>
  </div>
{{- end -}}
```

- [ ] **Step 2: Verify hero is restored**

Run `hugo server` and open `http://localhost:1313/`. Confirm:
- Hero headline "Conclusion Xforce Tech Playground" is visible at the top
- Subtitle "A space to experiment and play…" appears below it
- "Jump to latest blogs" CTA button is present
- Welcome paragraph is visible below the button

- [ ] **Step 3: Verify sections**

Still at `http://localhost:1313/`, scroll down and confirm:
- Divider line separates hero from sections
- "Latest Post" appears as a prominent `h2` above a left-bordered card
- "Browse by Tag" appears as a prominent `h2` above teal-outlined chips
- "Authors" appears as a prominent `h2` above a row of left-bordered author cards
- Clicking a tag chip navigates to the correct tag page
- Clicking an author card navigates to the correct author page
- Clicking the post title or "Continue reading →" navigates to the post

- [ ] **Step 4: Commit**

```bash
git add layouts/hextra-home.html
git commit -m "feat: restore hero content and apply visual structure to homepage"
```

---

### Task 4: Push and verify build

- [ ] **Step 1: Push branch**

```bash
git push
```

- [ ] **Step 2: Confirm Cloudflare build passes**

In the Cloudflare Pages dashboard, confirm the deployment triggered by the push completes without errors. Check the live URL to confirm the dark theme, Montserrat fonts, and homepage structure all appear correctly in production.
