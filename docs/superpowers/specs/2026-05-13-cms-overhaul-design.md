# CMS Overhaul Design

**Date:** 2026-05-13
**Scope:** Hugo layout overrides only — no content files touched in this PR. Tag normalization (casing, consistency) is a follow-up PR.

## Problem

- Clicking a tag does nothing useful (no taxonomy index exists)
- Blog listing is buried; homepage requires a click to reach any content
- No tag index in the sidebar
- Author pages do not list posts written by that author
- Post pages do not link back to author profiles

## Approach

Pure Hugo taxonomy + layout overrides. All output is static — no JavaScript. This keeps the path to adding client-side tag filtering later fully open: the tag anchor markup produced here can be reused as filter triggers without structural changes.

---

## Section 1 — Tag Taxonomy

**`hugo.yaml` change:**
```yaml
taxonomies:
  tag: tags
```

This gives every tag a canonical URL (`/tags/<name>/`) and a root index at `/tags/`. Hugo resolves existing `tags:` frontmatter on all posts automatically.

**New layout files:**
- `layouts/taxonomy/tag.html` — posts for a single tag, sorted by date desc, matching the existing blog list style
- `layouts/taxonomy/tags.html` — root tag cloud at `/tags/`, showing all tags with post counts as linked chips

Tag casing inconsistencies (e.g. `observability` vs `Observability`) are **not** fixed here — deferred to a second PR that touches only content files.

---

## Section 2 — Homepage

**New file:** `layouts/index.html`

Three regions, top to bottom:

1. **Latest post** — title, date, author(s), Hugo `.Summary` (~70 words auto-extracted), "Continue reading →" link. Sourced from `.Site.RegularPages` sorted by date desc, first result.
2. **Tag cloud** — all tags from `.Site.Taxonomies.tags` rendered as linked chips with post count. Each chip links to `/tags/<name>/`.
3. **Author index** — avatars and names of all authors, sourced from `.Site.Pages` filtered to section `author`, linking to `/author/<name>/`.

No manual excerpt markers (`<!--more-->`) required in posts.

---

## Section 3 — Sidebar Tag Cloud

**New file:** `layouts/partials/sidebar-tags.html`

A partial rendering a compact tag list (tag name + post count, linked to `/tags/<name>/`) to be included in the sidebar on the blog list page and individual post pages.

The Hextra theme sidebar is delivered via the git submodule. Rather than editing the submodule, the relevant sidebar partial is copied into `layouts/partials/` and extended there. This keeps the theme upgradeable.

**Route to B (JS filtering):** The tag links here are plain `<a href="/tags/foo/">` anchors. A future JS layer can intercept these as filter triggers with no markup changes.

---

## Section 4 — Author Pages

### Author single page

**File:** `layouts/author/single.html` (already custom — extend it)

Queries `.Site.RegularPages` and filters to pages where `.Params.authors` contains the current author's `.Title`. Renders the matching posts as a dated list with title and description, consistent with the blog list style. No content file changes needed — the `authors` field already exists on every post.

### Post author attribution

**New files:** `layouts/partials/author-byline.html` + `layouts/blog/single.html`

`author-byline.html` renders one author's avatar and name as a link to `/author/<name>/`. `layouts/blog/single.html` wraps the Hextra single-post layout and includes the byline partial for each entry in `.Params.authors`. Multiple authors are supported (the `authors` field is an array).

---

## Out of Scope (this PR)

- Tag normalization / casing cleanup (second PR, content-only)
- Client-side JS tag filtering on the blog list page (Option B — future)
- Any changes to `content/` files
