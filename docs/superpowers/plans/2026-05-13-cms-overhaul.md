# CMS Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a functioning tags taxonomy, tag-cloud sidebar, clickable author bylines, author post listings, and a redesigned homepage — all via Hugo layout overrides, no content file changes.

**Architecture:** Hugo's built-in taxonomy system handles tag routing (`/tags/<name>/`). All new pages are static layout overrides in `layouts/` that follow the existing Hextra class-and-partial patterns visible in `layouts/author/list.html`. The right-panel spacer div in each layout is replaced with the `sidebar-tags.html` partial, keeping tag links as plain anchors so JS filtering can be wired up later without markup changes.

**Tech Stack:** Hugo 0.145.0, Hextra theme (git submodule), Go templates, Tailwind CSS (via Hextra's `hx:` prefix classes)

---

## Prerequisites (run once, not a task)

```bash
pip3 install -r requirements-dev.txt   # installs hugo 0.145.0
git submodule update --init        # fetches the Hextra theme
hugo build                         # baseline — must succeed with 0 errors before starting
```

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `hugo.yaml` | Enable tags taxonomy |
| Create | `layouts/taxonomy/tag.html` | Single-tag post listing (`/tags/aws/`) |
| Create | `layouts/taxonomy/tags.html` | All-tags index at `/tags/` |
| Create | `layouts/partials/sidebar-tags.html` | Compact tag list partial (reused in blog layouts) |
| Create | `layouts/blog/list.html` | Blog list override adding sidebar-tags panel |
| Create | `layouts/partials/author-byline.html` | Author avatar + name link partial |
| Create | `layouts/blog/single.html` | Blog post override with author byline + sidebar-tags |
| Modify | `layouts/author/single.html` | Add post listing below author bio |
| Create | `layouts/hextra-home.html` | New homepage (latest post + tag cloud + author index) |

---

## Task 1: Enable tags taxonomy

**Files:**
- Modify: `hugo.yaml`

- [ ] **Step 1: Add taxonomy block to hugo.yaml**

Open `hugo.yaml` and add the following block directly after the `enableEmoji: false` line:

```yaml
taxonomies:
  tag: tags
```

- [ ] **Step 2: Build and verify no errors**

```bash
hugo build
```

Expected: exit code 0, no `ERROR` lines. Hugo will now generate `/tags/` and `/tags/<name>/` pages using its default templates (unstyled for now — that's fine).

- [ ] **Step 3: Confirm tag pages exist in output**

```bash
ls public/tags/
```

Expected: a directory per tag (e.g. `aws/`, `dynatrace/`, `observability/`) plus an `index.html` at the root.

- [ ] **Step 4: Commit**

```bash
git add hugo.yaml
git commit -m "feat: enable tags taxonomy"
```

---

## Task 2: Create tag term layout

**Files:**
- Create: `layouts/taxonomy/tag.html`

- [ ] **Step 1: Create the directory and file**

```bash
mkdir -p layouts/taxonomy
```

Create `layouts/taxonomy/tag.html` with the following content:

```html
{{ define "main" }}
  {{- $readMore := "Read more →" -}}
  <div class="hx:mx-auto hx:flex {{ partial `utils/page-width` . }}">
    {{ partial "sidebar.html" (dict "context" . "disableSidebar" true "displayPlaceholder" true) }}
    <article class="hx:w-full hx:break-words hx:flex hx:min-h-[calc(100vh-var(--navbar-height))] hx:min-w-0 hx:justify-center hx:pb-8 hx:pr-[calc(env(safe-area-inset-right)-1.5rem)]">
      <main class="hx:w-full hx:min-w-0 hx:max-w-6xl hx:px-6 hx:pt-4 hx:md:px-12">
        <h1 class="hx:mt-2 hx:text-4xl hx:font-bold hx:tracking-tight hx:text-slate-900 hx:dark:text-slate-100">#{{ .Title }}</h1>
        <p class="hx:mt-2 hx:opacity-60 hx:text-sm">{{ len .Pages }} {{ if eq (len .Pages) 1 }}post{{ else }}posts{{ end }}</p>
        {{- range .Pages.ByDate.Reverse }}
          <div class="hx:mb-10 hx:mt-8">
            <h3>
              <a style="color:inherit;text-decoration:none;" class="hx:block hx:font-semibold hx:text-2xl" href="{{ .RelPermalink }}">{{ .Title }}</a>
            </h3>
            <p class="hx:opacity-50 hx:text-sm hx:mt-1">{{ partial "utils/format-date" .Date }}</p>
            <p class="hx:opacity-80 hx:mt-4 hx:leading-7">{{ partial "utils/page-description" . }}</p>
            <p class="hx:mt-2">
              <a class="hx:text-[color:hsl(var(--primary-hue),100%,50%)] hx:underline hx:underline-offset-2 hx:decoration-from-font" href="{{ .RelPermalink }}">{{ $readMore }}</a>
            </p>
          </div>
        {{- end }}
      </main>
    </article>
    <div class="hx:max-xl:hidden hx:h-0 hx:w-64 hx:shrink-0"></div>
  </div>
{{- end -}}
```

- [ ] **Step 2: Build and check a tag page**

```bash
hugo build && ls public/tags/aws/
```

Expected: `index.html` is present, no build errors.

- [ ] **Step 3: Spot-check the rendered HTML**

```bash
grep -i "ArgoCD" public/tags/aws/index.html
```

Expected: the ArgoCD post title appears (it's tagged `AWS`). If the tag is capitalised differently, check `public/tags/` for the exact directory name.

- [ ] **Step 4: Commit**

```bash
git add layouts/taxonomy/tag.html
git commit -m "feat: add tag term layout"
```

---

## Task 3: Create tag index layout

**Files:**
- Create: `layouts/taxonomy/tags.html`

- [ ] **Step 1: Create `layouts/taxonomy/tags.html`**

```html
{{ define "main" }}
  <div class="hx:mx-auto hx:flex {{ partial `utils/page-width` . }}">
    {{ partial "sidebar.html" (dict "context" . "disableSidebar" true "displayPlaceholder" true) }}
    <article class="hx:w-full hx:break-words hx:flex hx:min-h-[calc(100vh-var(--navbar-height))] hx:min-w-0 hx:justify-center hx:pb-8 hx:pr-[calc(env(safe-area-inset-right)-1.5rem)]">
      <main class="hx:w-full hx:min-w-0 hx:max-w-6xl hx:px-6 hx:pt-4 hx:md:px-12">
        <h1 class="hx:mt-2 hx:text-4xl hx:font-bold hx:tracking-tight hx:text-slate-900 hx:dark:text-slate-100">Tags</h1>
        <div class="hx:mt-6 hx:flex hx:flex-wrap hx:gap-3">
          {{- range .Data.Terms.Alphabetical }}
            <a href="{{ .Page.RelPermalink }}"
               class="hx:inline-flex hx:items-center hx:gap-1 hx:rounded-full hx:border hx:px-3 hx:py-1 hx:text-sm hx:font-medium hx:transition-colors hover:hx:bg-slate-100 hx:dark:hover:hx:bg-slate-800">
              #{{ .Page.Title }}<span class="hx:opacity-50">{{ .Count }}</span>
            </a>
          {{- end }}
        </div>
      </main>
    </article>
    <div class="hx:max-xl:hidden hx:h-0 hx:w-64 hx:shrink-0"></div>
  </div>
{{- end -}}
```

- [ ] **Step 2: Build and verify `/tags/` page**

```bash
hugo build && grep -c "rounded-full" public/tags/index.html
```

Expected: a count ≥ 1 (the tag chips are rendered).

- [ ] **Step 3: Commit**

```bash
git add layouts/taxonomy/tags.html
git commit -m "feat: add tag index layout"
```

---

## Task 4: Create sidebar tags partial

**Files:**
- Create: `layouts/partials/sidebar-tags.html`

- [ ] **Step 1: Create `layouts/partials/sidebar-tags.html`**

```html
<div class="hx:p-4 hx:sticky hx:top-16">
  <p class="hx:text-xs hx:font-semibold hx:uppercase hx:tracking-wide hx:text-slate-500 hx:dark:text-slate-400 hx:mb-3">Tags</p>
  <ul class="hx:space-y-1">
    {{- range .Site.Taxonomies.tags.Alphabetical }}
      <li>
        <a href="{{ .Page.RelPermalink }}"
           class="hx:flex hx:justify-between hx:items-center hx:text-sm hx:py-0.5 hx:text-slate-600 hx:dark:text-slate-300 hover:hx:text-slate-900 hx:dark:hover:hx:text-slate-100">
          <span>#{{ .Page.Title }}</span>
          <span class="hx:opacity-40 hx:text-xs hx:tabular-nums">{{ .Count }}</span>
        </a>
      </li>
    {{- end }}
  </ul>
  <div class="hx:mt-4 hx:border-t hx:pt-3">
    <a href="/tags/" class="hx:text-xs hx:text-[color:hsl(var(--primary-hue),100%,50%)]">All tags →</a>
  </div>
</div>
```

> **Route to B note:** Each `<a>` tag here is a plain anchor. When adding JS filtering later, adding `data-tag="{{ .Page.Title | urlize }}"` to each `<a>` and a `data-tag` attribute on each post card in the list is all that's needed to wire up a filter without changing this markup.

- [ ] **Step 2: Build (partial is not yet included anywhere — just verify no parse errors)**

```bash
hugo build
```

Expected: 0 errors.

- [ ] **Step 3: Commit**

```bash
git add layouts/partials/sidebar-tags.html
git commit -m "feat: add sidebar-tags partial"
```

---

## Task 5: Create blog list layout with sidebar tags

**Files:**
- Create: `layouts/blog/list.html`

- [ ] **Step 1: Create `layouts/blog/list.html`**

This overrides the Hextra default blog list, preserving the sort-by-date behaviour and tag display from `hugo.yaml` (`params.blog.list.*`), while replacing the right spacer with the tag sidebar and making tag chips link to their taxonomy pages.

```html
{{ define "main" }}
  {{- $readMore := "Read more →" -}}
  {{- $sortBy := site.Params.blog.list.sortBy | default "date" -}}
  {{- $sortOrder := site.Params.blog.list.sortOrder | default "desc" -}}
  <div class="hx:mx-auto hx:flex {{ partial `utils/page-width` . }}">
    {{ partial "sidebar.html" (dict "context" . "disableSidebar" true "displayPlaceholder" true) }}
    <article class="hx:w-full hx:break-words hx:flex hx:min-h-[calc(100vh-var(--navbar-height))] hx:min-w-0 hx:justify-center hx:pb-8 hx:pr-[calc(env(safe-area-inset-right)-1.5rem)]">
      <main class="hx:w-full hx:min-w-0 hx:max-w-6xl hx:px-6 hx:pt-4 hx:md:px-12">
        {{ if .Title }}<h1 class="hx:text-center hx:mt-2 hx:text-4xl hx:font-bold hx:tracking-tight hx:text-slate-900 hx:dark:text-slate-100">{{ .Title }}</h1>{{ end }}
        <div class="content">{{ .Content }}</div>
        {{- $pages := partial "utils/sort-pages" (dict "page" . "by" $sortBy "order" $sortOrder) -}}
        {{- range $pages }}
          <div class="hx:mb-10">
            <h3>
              <a style="color:inherit;text-decoration:none;" class="hx:block hx:font-semibold hx:mt-8 hx:text-2xl" href="{{ .RelPermalink }}">{{ .Title }}</a>
            </h3>
            {{- if site.Params.blog.list.displayTags -}}
              {{- with .Params.tags }}
                <p class="hx:opacity-50 hx:text-sm hx:leading-7">
                  {{- range . }}
                    <a class="hx:inline-block hx:mr-2 hover:hx:opacity-80" href="/tags/{{ . | urlize }}/">#{{ . }}</a>
                  {{- end -}}
                </p>
              {{- end -}}
            {{- end -}}
            <p class="hx:opacity-80 hx:mt-4 hx:leading-7">{{ partial "utils/page-description" . }}</p>
            <p class="hx:opacity-80 hx:mt-1 hx:leading-7">
              <a class="hx:text-[color:hsl(var(--primary-hue),100%,50%)] hx:underline hx:underline-offset-2 hx:decoration-from-font" href="{{ .RelPermalink }}">{{ $readMore }}</a>
            </p>
            <p class="hx:opacity-50 hx:text-sm hx:mt-4 hx:leading-7">{{ partial "utils/format-date" .Date }}</p>
          </div>
        {{- end }}
      </main>
    </article>
    <div class="hx:max-xl:hidden hx:w-64 hx:shrink-0 hx:pt-8">
      {{ partial "sidebar-tags.html" . }}
    </div>
  </div>
{{- end -}}
```

- [ ] **Step 2: Build**

```bash
hugo build
```

Expected: 0 errors, `public/blog/index.html` exists.

- [ ] **Step 3: Verify tag links are rendered in the blog list**

```bash
grep "href=\"/tags/" public/blog/index.html | head -5
```

Expected: multiple lines with `/tags/<name>/` hrefs.

- [ ] **Step 4: Verify sidebar-tags is included**

```bash
grep "All tags" public/blog/index.html
```

Expected: the "All tags →" link appears.

- [ ] **Step 5: Commit**

```bash
git add layouts/blog/list.html
git commit -m "feat: blog list with sidebar tags and linked tag chips"
```

---

## Task 6: Create author byline partial

**Files:**
- Create: `layouts/partials/author-byline.html`

This partial receives `(dict "site" $.Site "name" $authorName)` and renders an avatar + name linking to the author's page. Author pages live at `content/author/<Name>/` as branch bundles (`_index.md`).

- [ ] **Step 1: Create `layouts/partials/author-byline.html`**

```html
{{- $name := .name -}}
{{- $site := .site -}}
{{- $candidates := where $site.Pages "Type" "author" -}}
{{- $authorPage := index (where $candidates "Title" $name) 0 -}}
{{- if $authorPage -}}
  {{- $img := $authorPage.Resources.GetMatch "*.png" -}}
  {{- if not $img -}}{{- $img = $authorPage.Resources.GetMatch "*.jpg" -}}{{- end -}}
  <a href="{{ $authorPage.RelPermalink }}"
     class="hx:group hx:inline-flex hx:items-center hx:gap-x-1.5 hx:text-current hx:no-underline hx:mx-1">
    {{- if $img }}
      <img src="{{ $img.RelPermalink }}" alt="{{ $name }}"
           class="hx:inline-block hx:h-5 hx:w-5 hx:rounded-full hx:object-cover" loading="lazy" />
    {{- end }}
    <span class="hx:group-hover:hx:underline">{{ $name }}</span>
  </a>
{{- else -}}
  <span class="hx:mx-1">{{ $name }}</span>
{{- end -}}
```

- [ ] **Step 2: Build (partial not yet included anywhere)**

```bash
hugo build
```

Expected: 0 errors.

- [ ] **Step 3: Commit**

```bash
git add layouts/partials/author-byline.html
git commit -m "feat: add author-byline partial"
```

---

## Task 7: Create blog single layout

**Files:**
- Create: `layouts/blog/single.html`

This overrides the Hextra default single-post template. It preserves all existing Hextra features (breadcrumb, ToC, pagination, comments, last-updated) and adds: linked author bylines via `author-byline.html` and clickable inline tag links. The sidebar-tags panel was removed from single posts to give the article full width.

- [ ] **Step 1: Create `layouts/blog/single.html`**

```html
{{ define "main" }}
  <div class="hx:mx-auto hx:flex {{ partial `utils/page-width` . }}">
    {{ partial "sidebar.html" (dict "context" . "disableSidebar" true "displayPlaceholder" true) }}
    {{ partial "toc.html" . }}
    <article class="hx:w-full hx:break-words hx:flex hx:min-h-[calc(100vh-var(--navbar-height))] hx:min-w-0 hx:justify-center hx:pb-8 hx:pr-[calc(env(safe-area-inset-right)-1.5rem)]">
      <main class="hx:w-full hx:min-w-0 hx:max-w-6xl hx:px-6 hx:pt-4 hx:md:px-12">
        {{ partial "breadcrumb.html" . }}
        {{ if .Title }}<h1 class="hx:mt-2 hx:text-4xl hx:font-bold hx:tracking-tight hx:text-slate-900 hx:dark:text-slate-100">{{ .Title }}</h1>{{ end }}
        <div class="hx:mt-4 hx:mb-4 hx:text-gray-500 hx:text-sm hx:flex hx:items-center hx:flex-wrap hx:gap-y-2">
          {{- with $date := .Date }}<span class="hx:mr-1">{{ partial "utils/format-date" $date }}</span>{{ end -}}
          {{ if and .Date .Params.authors }}<span class="hx:mx-1">·</span>{{ end -}}
          {{- with $.Params.authors -}}
            {{- range $i, $author := . -}}
              {{- if $i }}<span class="hx:mr-1">,</span>{{ end -}}
              {{- if reflect.IsMap $author -}}
                <a {{ with $author.link }}href="{{ . }}" target="_blank"{{ end }}
                   class="hx:group hx:inline-flex hx:items-center hx:text-current hx:gap-x-1.5 hx:mx-1"
                   {{ with $author.name }}title="{{ . }}"{{ end }}>
                  {{- with $author.image -}}
                    <img src="{{ . | safeURL }}" alt="{{ $author.name }}"
                         class="hx:inline-block hx:h-5 hx:w-5 hx:rounded-full" loading="lazy" />
                  {{- end -}}
                  <div class="hx:group-hover:hx:underline">{{ $author.name }}</div>
                </a>
              {{- else -}}
                {{ partial "author-byline.html" (dict "site" $.Site "name" $author) }}
              {{- end -}}
            {{- end -}}
          {{- end -}}
        </div>
        {{- with .Params.tags }}
          <div class="hx:mb-8 hx:flex hx:flex-wrap hx:gap-2">
            {{- range . }}
              <a href="/tags/{{ . | urlize }}/"
                 class="hx:text-sm hx:opacity-60 hover:hx:opacity-100">#{{ . }}</a>
            {{- end }}
          </div>
        {{- end }}
        <div class="content">{{ .Content }}</div>
        {{- partial "components/last-updated.html" . -}}
        {{- if (site.Params.blog.article.displayPagination | default true) -}}
          {{- .Scratch.Set "reversePagination" true -}}
          {{- partial "components/pager.html" . -}}
        {{- end }}
        {{- partial "components/comments.html" . -}}
      </main>
    </article>
    <div class="hx:max-xl:hidden hx:h-0 hx:w-64 hx:shrink-0"></div>
  </div>
{{ end }}
```

- [ ] **Step 2: Build**

```bash
hugo build
```

Expected: 0 errors.

- [ ] **Step 3: Verify a blog post has author links and tag links**

```bash
grep "href=\"/author/" public/blog/ArgoCD-SSO-based-on-AWS-Cognito-Userpools/index.html
grep "href=\"/tags/" public/blog/ArgoCD-SSO-based-on-AWS-Cognito-Userpools/index.html
```

Expected: at least one `/author/` link and at least one `/tags/` link per check.

- [ ] **Step 4: Commit**

```bash
git add layouts/blog/single.html
git commit -m "feat: blog single layout with author bylines and tag links"
```

---

## Task 8: Add post listing to author single page

**Files:**
- Modify: `layouts/author/single.html`

- [ ] **Step 1: Replace `layouts/author/single.html` with the following**

The addition is the `<section>` block after `{{ .Content }}`. Everything before it is the existing file content, preserved exactly.

```html
{{ define "main" }}
  <div class="hx:mx-auto hx:flex {{ partial `utils/page-width` . }}">
    {{ partial "sidebar.html" (dict "context" . "disableSidebar" true "displayPlaceholder" true) }}
    {{ partial "toc.html" . }}
    <article class="hx:w-full hx:break-words hx:flex hx:min-h-[calc(100vh-var(--navbar-height))] hx:min-w-0 hx:justify-center hx:pb-8 hx:pr-[calc(env(safe-area-inset-right)-1.5rem)]">
      <main class="hx:w-full hx:min-w-0 hx:max-w-6xl hx:px-6 hx:pt-4 hx:md:px-12">
        {{ partial "breadcrumb.html" . }}
        {{ if .Title }}<h1 class="hx:mt-2 hx:text-4xl hx:font-bold hx:tracking-tight hx:text-slate-900 hx:dark:text-slate-100">{{ .Title }}</h1>{{ end }}
        <div class="hx:mt-4 hx:mb-16 hx:text-gray-500 hx:text-sm hx:flex hx:items-center hx:flex-wrap hx:gap-y-2">
          {{- with $date := .Date }}<span class="hx:mr-1">{{ partial "utils/format-date" $date }}</span>{{ end -}}
          {{- $lazyLoading := site.Params.enableImageLazyLoading | default true -}}
          {{ if and .Date .Params.authors }}<span class="hx:mx-1">·</span>{{ end -}}
          {{- with $.Params.authors -}}
            {{- range $i, $author := . -}}
              {{- if reflect.IsMap $author -}}
                {{- if and $i (not $author.image) }}<span class="hx:mr-1">,</span>{{ end -}}
                <a
                  {{ with $author.link }}href="{{ . }}" target="_blank"{{ end }}
                  class="hx:group hx:inline-flex hx:items-center hx:text-current hx:gap-x-1.5 hx:mx-1"
                  {{ with $author.name }}title="{{ . }}"{{ end }}
                >
                  {{- with $image := $author.image }}
                    {{- $isLocal := not (urls.Parse $image).Scheme -}}
                    {{- $startsWithSlash := hasPrefix $image "/" -}}
                    {{- if and $isLocal $startsWithSlash }}
                      {{- $image = (relURL (strings.TrimPrefix "/" $image)) -}}
                    {{ end -}}
                    <img src="{{ $image | safeURL }}" alt="{{ $author.name }}" class="hx:inline-block hx:h-4 hx:w-4 hx:rounded-full" {{ if $lazyLoading }}loading="lazy"{{ end }} />
                  {{ end -}}
                  <div class="hx:group-hover:underline">{{ $author.name }}</div>
                </a>
              {{- else -}}
                {{- if $i }}<span class="hx:mr-1">,</span>{{ end -}}<span class="hx:mx-1">{{ $author }}</span>
              {{- end -}}
            {{- end -}}
          {{- end -}}
        </div>
        <div class="content">
          {{ .Content }}
        </div>
        {{- $authorName := .Title -}}
        {{- $posts := where .Site.RegularPages ".Params.authors" "intersect" (slice $authorName) | sort "Date" "desc" -}}
        {{- if $posts }}
          <section class="hx:mt-12">
            <h2 class="hx:text-2xl hx:font-bold hx:tracking-tight hx:text-slate-900 hx:dark:text-slate-100 hx:mb-6">Posts by {{ $authorName }}</h2>
            {{- range $posts }}
              <div class="hx:mb-8">
                <h3>
                  <a style="color:inherit;text-decoration:none;" class="hx:font-semibold hx:text-xl" href="{{ .RelPermalink }}">{{ .Title }}</a>
                </h3>
                <p class="hx:opacity-50 hx:text-sm hx:mt-1">{{ partial "utils/format-date" .Date }}</p>
                <p class="hx:opacity-80 hx:mt-2 hx:leading-7">{{ partial "utils/page-description" . }}</p>
              </div>
            {{- end }}
          </section>
        {{- end }}
        {{- partial "components/last-updated.html" . -}}
        {{- if (site.Params.blog.article.displayPagination | default true) -}}
          {{- .Scratch.Set "reversePagination" true -}}
          {{- partial "components/pager.html" . -}}
        {{ end }}
        {{- partial "components/comments.html" . -}}
      </main>
    </article>
  </div>
{{ end }}
```

- [ ] **Step 2: Build**

```bash
hugo build
```

Expected: 0 errors.

- [ ] **Step 3: Verify an author page lists their posts**

```bash
grep -i "ArgoCD" public/author/svenkooiman/index.html 2>/dev/null || \
grep -i "posts by" public/author/*/index.html | head -5
```

Expected: post titles appear under "Posts by <Author>". Check which author wrote which post if needed: `grep "authors" content/blog/*/index.md`.

- [ ] **Step 4: Commit**

```bash
git add layouts/author/single.html
git commit -m "feat: author page lists posts by that author"
```

---

## Task 9: Create new homepage layout

**Files:**
- Create: `layouts/hextra-home.html`

The homepage `content/_index.md` declares `layout: hextra-home`, so Hugo resolves our `layouts/hextra-home.html` before the theme's copy. This layout does **not** render `.Content` (the old hero shortcodes), replacing it with: the latest blog post summary, a tag cloud, and the author index.

- [ ] **Step 1: Create `layouts/hextra-home.html`**

```html
{{ define "main" }}
  <div class="hx:mx-auto hx:flex {{ partial `utils/page-width` . }}">
    {{ partial "sidebar.html" (dict "context" . "disableSidebar" true "displayPlaceholder" true) }}
    <article class="hx:w-full hx:break-words hx:flex hx:min-h-[calc(100vh-var(--navbar-height))] hx:min-w-0 hx:justify-center hx:pb-8 hx:pr-[calc(env(safe-area-inset-right)-1.5rem)]">
      <main class="hx:w-full hx:min-w-0 hx:max-w-6xl hx:px-6 hx:pt-4 hx:md:px-12">

        {{/* ── Latest post ──────────────────────────────────────────── */}}
        {{- $latestPost := index (where .Site.RegularPages "Section" "blog" | sort "Date" "desc") 0 -}}
        {{- with $latestPost }}
          <section class="hx:mb-14">
            <p class="hx:text-xs hx:font-semibold hx:uppercase hx:tracking-wide hx:text-slate-500 hx:dark:text-slate-400 hx:mb-3">Latest post</p>
            <h1 class="hx:text-3xl hx:font-bold hx:tracking-tight hx:text-slate-900 hx:dark:text-slate-100">
              <a style="color:inherit;text-decoration:none;" href="{{ .RelPermalink }}">{{ .Title }}</a>
            </h1>
            <p class="hx:opacity-50 hx:text-sm hx:mt-2">
              {{ partial "utils/format-date" .Date -}}
              {{- with .Params.authors }} · {{ delimit . ", " }}{{ end }}
            </p>
            <p class="hx:mt-4 hx:leading-7 hx:opacity-80">{{ .Summary }}</p>
            <a class="hx:mt-4 hx:inline-block hx:text-[color:hsl(var(--primary-hue),100%,50%)] hx:underline hx:underline-offset-2 hx:decoration-from-font"
               href="{{ .RelPermalink }}">Continue reading →</a>
          </section>
        {{- end }}

        {{/* ── Tag cloud ────────────────────────────────────────────── */}}
        <section class="hx:mb-14">
          <p class="hx:text-xs hx:font-semibold hx:uppercase hx:tracking-wide hx:text-slate-500 hx:dark:text-slate-400 hx:mb-3">Tags</p>
          <div class="hx:flex hx:flex-wrap hx:gap-2">
            {{- range .Site.Taxonomies.tags.Alphabetical }}
              <a href="{{ .Page.RelPermalink }}"
                 class="hx:inline-flex hx:items-center hx:gap-1 hx:rounded-full hx:border hx:px-3 hx:py-1 hx:text-sm hx:font-medium hx:transition-colors hover:hx:bg-slate-100 hx:dark:hover:hx:bg-slate-800">
                #{{ .Page.Title }}<span class="hx:opacity-50">{{ .Count }}</span>
              </a>
            {{- end }}
          </div>
        </section>

        {{/* ── Author index ─────────────────────────────────────────── */}}
        <section>
          <p class="hx:text-xs hx:font-semibold hx:uppercase hx:tracking-wide hx:text-slate-500 hx:dark:text-slate-400 hx:mb-3">Authors</p>
          <div class="hx:flex hx:flex-wrap hx:gap-8">
            {{- $authorSection := .Site.GetPage "/author" -}}
            {{- if $authorSection -}}
              {{- range $authorSection.Sections | sort "Title" }}
                {{- $img := .Resources.GetMatch "*.png" -}}
                {{- if not $img -}}{{- $img = .Resources.GetMatch "*.jpg" -}}{{- end -}}
                <a href="{{ .RelPermalink }}"
                   class="hx:flex hx:flex-col hx:items-center hx:gap-2 hx:no-underline hx:text-center">
                  {{- if $img }}
                    <img src="{{ $img.RelPermalink }}" alt="{{ .Title }}"
                         class="hx:h-16 hx:w-16 hx:rounded-full hx:object-cover" loading="lazy" />
                  {{- else }}
                    <div class="hx:h-16 hx:w-16 hx:rounded-full hx:bg-slate-200 hx:dark:hx:bg-slate-700"></div>
                  {{- end }}
                  <span class="hx:text-sm hx:font-medium">{{ .Title }}</span>
                </a>
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

- [ ] **Step 2: Build**

```bash
hugo build
```

Expected: 0 errors.

- [ ] **Step 3: Verify homepage has the three sections**

```bash
grep "Latest post"   public/index.html
grep "rounded-full"  public/index.html | head -3   # tag chips
grep "/author/"      public/index.html | head -5   # author links
```

Expected: all three greps return matches.

- [ ] **Step 4: Smoke-test locally in a browser**

```bash
hugo server
```

Open `http://localhost:1313/` and verify:
- Latest post summary + "Continue reading →" link
- Tag chips with counts, each linking to `/tags/<name>/`
- Author avatars, each linking to `/author/<name>/`

Open `http://localhost:1313/blog/` and verify:
- Blog list renders with tag chips and sidebar-tags panel on the right (on wide screens)

Open any blog post and verify:
- Author name(s) link to their author page(s)
- Inline tag links work

Open `/author/jitseklomp/` and verify:
- Author bio appears
- "Posts by Jitse Klomp" section lists their posts

Open `/tags/aws/` and verify:
- Posts tagged AWS are listed

- [ ] **Step 5: Commit**

```bash
git add layouts/hextra-home.html
git commit -m "feat: new homepage with latest post, tag cloud, author index"
```
