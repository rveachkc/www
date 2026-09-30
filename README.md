# www

Source for [ryanveach.com](https://ryanveach.com): a [Jekyll](https://jekyllrb.com/) site using the
[Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme (as a gem), deployed to
DigitalOcean App Platform as a static site.

## Local development

No local Ruby is needed; everything runs in a `ruby:3.3` container. Gems are cached in the
`www-bundle` volume.

```sh
./serve_dev.sh                  # http://<host>:4000, all interfaces, live reload, includes _drafts/
RUNTIME=podman ./serve_dev.sh   # same, with podman instead of docker
PORT=8080 ./serve_dev.sh        # different host port
```

New posts go in `_posts/YYYY-MM-DD-slug.md`. Front matter defaults (layout, comments, sharing,
etc.) come from `_config.yml`, so a post only needs `title`, `categories`, and `tags`, plus an
optional `header.overlay_image` / `header.teaser`. Images live in `assets/images/YYYY/MM/`.

## Deployment

`.do/app.yaml` is the App Platform spec. Pushes to `main` deploy automatically.

To change app settings, edit `.do/app.yaml`, then paste it into the DigitalOcean console
(App → Settings → App Spec → Edit). Console edits aren't synced back to the repo, so copy any
changes made there into this file.

The spec serves `ryanveach.com` and 301-redirects `www.ryanveach.com` to it, and redirects the
old WordPress `/feed/` URL to `/feed.xml`. DNS for the domain is hosted on DigitalOcean, and the
`zone: ryanveach.com` on each domain lets App Platform manage those records itself. Leave the
Google Workspace MX records alone.

## Comments (giscus)

Post comments use [giscus](https://giscus.app), backed by GitHub Discussions in this repo's
**Comments** category (Announcement format, so only giscus and maintainers open threads). Each
post maps to a discussion titled with its URL path, created on the first comment. Settings are
under `comments:` in `_config.yml`; the giscus GitHub App must stay installed on the repo.

To disable comments on one post, add `comments: false` to its front matter.

## WordPress migration

Posts were imported from a WordPress WXR export with `scripts/wp_import.py` (see its docstring).
It's a one-shot tool: posts have been hand-edited since, so re-running it would overwrite them.
Export files (`*.WordPress.*.xml`, `import/`) are git-ignored because they contain commenter PII.

## AI disclosure

All posts and other written content on this site are written by a human (Ryan Veach).
AI tools were used to help with the Jekyll configuration, site styling, and deployment
automation, including the WordPress import script. They were not used to write the content.
