# Conclusion Xforce techblog

This repo contains the source code for the Conclusion Xforce techblog, built
with [Hugo](https://gohugo.io/) and the
[Hextra](https://github.com/imfing/hextra/) theme.

## Local setup

**Prerequisites:** Hugo 0.145.0. Install it (and pin the version) via pip:

```bash
pip3 install -r requirements-dev.txt
```

The [Hextra theme](https://github.com/imfing/hextra/) is included as a Git
submodule. Fetch it once after cloning:

```bash
git submodule init
git submodule update
```

Start the dev server:

```bash
hugo server
```

The site is then available at `http://localhost:1313/`.

## Writing content

### Blog posts

Each post lives in its own directory under `content/blog/`. Scaffold one with:

```bash
hugo new blog/My-Blog-Title
```

This creates `content/blog/My-Blog-Title/index.md` from the archetype. Fill in
the frontmatter:

```yaml
---
title: My Blog Title
subtitle: My subtitle
description: A short blurb about my blog
authors: [Author Name]   # must match the title in the author's _index.md
date: '2026-01-01'
tags: [tag1, tag2]
draft: false
---
```

Place any images for the post in the same directory as `index.md`.

### Author pages

First-time author? Create your page with:

```bash
hugo new author/Your-Name
```

This creates `content/author/Your-Name/_index.md`. Add a profile photo in that
directory and update the frontmatter.

## Contributing

Fork the repository and open a pull request against `main`. Pull requests are
linted automatically — make sure your Markdown passes `markdownlint-cli2`
before pushing.

## License

All content in this repository is licensed under the
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
You are free to share and adapt the content, but you must give appropriate
credit, provide a link to the license, and indicate if changes were made.
You may not use the material for commercial purposes. See [LICENSE](./LICENSE)
for the full license text.

For any other use, please contact the author for permission.
