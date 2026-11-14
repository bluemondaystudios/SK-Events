# SK Events

Sekhukhune Entertainment News — built with [Jekyll](https://jekyllrb.com/),
hosted on GitHub Pages.

## Writing a new article

No admin panel — articles are markdown files in `_posts/`, named
`YYYY-MM-DD-a-short-title.md` (the date becomes the publish date; the rest
of the filename becomes the URL slug). Easiest way: in GitHub, open
`_posts/`, click **Add file → Create new file**, and use this template:

```markdown
---
title: "Your Article Title"
categories: [news]
excerpt: "One or two sentences shown in article listings. Optional -- leave it out and the first ~30 words of the body are used instead."
image: /assets/images/your-image.jpg
author: Your Name
---

Write the article here, in plain markdown. Blank lines between
paragraphs. **Bold**, *italic*, [links](https://example.com) all work.
```

`categories` must be exactly one of: `news`, `interview`, `event-recap`,
`new-release`, `opinion` (see `_data/categories.yml` for the full list with
display labels — add a new one there if you need another category).

`image` is optional. Upload the file under `assets/images/` first (GitHub's
"Add file" lets you drag one in), then reference its path.

Commit the file (GitHub does this for you when you click "Commit new
file") and the site rebuilds automatically within a minute or two.

### Drafts

Want to write something without publishing it yet? Put the file in
`_drafts/` instead of `_posts/` (no date prefix needed there — just
`a-short-title.md`). It won't appear on the live site. When it's ready,
move it into `_posts/` and rename it with today's date prefix.

## Local preview (optional)

Not required for publishing — only useful if you want to see changes
before committing them.

```
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000.
