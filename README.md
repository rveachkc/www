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

The spec 301-redirects the old WordPress `/feed/` URL to `/feed.xml`.

DNS for `ryanveach.com` is hosted on DigitalOcean. At cutover, add both domains to the spec with
`zone: ryanveach.com` so App Platform manages their records, plus the `www` → apex redirect rule
commented at the bottom of the spec. First remove any conflicting A records in
Networking → Domains.

## Enabling comments (giscus)

Comments use [giscus](https://giscus.app) (GitHub Discussions). They are wired up but disabled
because giscus needs a **public** repo. When ready:

1. Make `rveachkc/www` public.
2. Settings → Features → enable **Discussions**, and create a category named **Comments** with
   the **Announcement** format, so only maintainers and giscus can open new threads.
3. Install the [giscus GitHub App](https://github.com/apps/giscus) on the repo.
4. On [giscus.app](https://giscus.app), enter the repo and choose the Comments category and
   the "pathname" mapping, then copy `data-repo-id` and `data-category-id`.
5. In `_config.yml`, set `comments.provider: giscus` and fill in `repo_id` and `category_id`.
6. Push, then leave a test comment and check that a Discussion titled with the post's path appears.

## WordPress migration

Posts were imported from a WordPress WXR export with `scripts/wp_import.py` (see its docstring).
It's a one-shot tool: posts have been hand-edited since, so re-running it would overwrite them.
Export files (`*.WordPress.*.xml`, `import/`) are git-ignored because they contain commenter PII.

## AI disclosure

All posts and other written content on this site are written by a human (Ryan Veach).
AI tools were used to help with the Jekyll configuration, site styling, and deployment
automation, including the WordPress import script. They were not used to write the content.
