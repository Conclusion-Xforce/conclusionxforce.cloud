# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the Conclusion Xforce tech blog, a static site built with [Hugo](https://gohugo.io/) and the [Hextra theme](https://github.com/imfing/hextra) (included as a git submodule).

## Setup

Requires Python >= 3.9. Hugo is installed via pip (pinned to `0.145.0` in `requirements-dev.txt`).

```bash
pip3 install -r requirements-dev.txt
git submodule init
git submodule update
```

## Common Commands

```bash
hugo server                     # Start local dev server at http://localhost:1313/
hugo new blog/My-Blog-Title     # Create a new blog post
hugo new author/Your-Name       # Create a new author page
```

## Architecture

### Content Structure

All content lives under `content/` in three sections:

- `content/blog/<slug>/` — Each post is a directory with `index.md` and any supporting images stored alongside it.
- `content/author/<Name>/` — One directory per author, containing `_index.md` and a profile photo.
- `content/about/` — Single about page.

### Blog Post Frontmatter

New posts are scaffolded from `archetypes/blog/default.md`. Required fields:

```yaml
---
title: My Blog Title
subtitle: My subtitle
description: A short blurb about my blog
authors: [Author Name]          # must match the title in the author's _index.md
date: '2026-01-01'
tags: [tag1, tag2]
draft: false
---
```

### Theme and Customization

- **Theme**: `themes/hextra/` (git submodule — do not edit files here).
- **Layout overrides**: `layouts/author/` contains custom Hugo templates that override the theme's author list/single views.
- **CSS**: `static/css/custom-styles.css` for site-wide custom styles (loaded via `layouts/partials/custom/head-end.html`).
- **Site config**: `hugo.yaml` controls navigation menus, search (flexsearch), syntax highlighting, and theme parameters.

### CI

Pull requests are linted via GitHub Actions (`.github/workflows/pull-request.yaml`) using `markdownlint-cli2`. Some blog directories have a local `.markdownlint.json` to override rules for that post.
