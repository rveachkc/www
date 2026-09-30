#!/usr/bin/env bash
# Run the Jekyll dev server in a container, listening on all interfaces.
#   ./serve_dev.sh                 # uses docker
#   RUNTIME=podman ./serve_dev.sh  # uses podman
# Site: http://<host>:4000 (live reload on 35729)
set -euo pipefail

RUNTIME="${RUNTIME:-docker}"
IMAGE="${IMAGE:-docker.io/library/ruby:3.3}"
PORT="${PORT:-4000}"

cd "$(dirname "$0")"

# Run as the invoking user so generated files (_site, caches, vendor/) aren't root-owned.
case "$RUNTIME" in
  podman) user_args=(--userns=keep-id) ;;
  *)      user_args=(--user "$(id -u):$(id -g)") ;;
esac

# Gems install into ./vendor/bundle (git-ignored) so they're owned by the same user
# and shared between docker and podman.
exec "$RUNTIME" run --rm -it "${user_args[@]}" \
  -p "$PORT:4000" -p 35729:35729 \
  -v "$PWD":/srv:Z -w /srv \
  -e HOME=/tmp \
  -e BUNDLE_PATH=/srv/vendor/bundle \
  -e BUNDLE_APP_CONFIG=/srv/.bundle \
  "$IMAGE" \
  sh -c 'bundle install && bundle exec jekyll serve -H 0.0.0.0 --livereload --drafts'
