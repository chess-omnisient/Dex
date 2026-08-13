#!/bin/bash
set -euo pipefail

if ! REMOTE_TAGS="$(
  git ls-remote --tags origin 'refs/tags/dist/release/v*'
)"; then
  echo "❌ Release-tag uniqueness gate failed: could not read dist/release tags from origin; git ls-remote failed." >&2
  exit 1
fi
if [ -z "$REMOTE_TAGS" ]; then
  echo "❌ Release-tag uniqueness gate failed: origin returned no readable dist/release tags, so uniqueness cannot be verified." >&2
  exit 1
fi

# Annotated tags also produce a peeled ^{} ref; count only the tag ref itself.
DUPLICATE_VERSIONS="$(
  printf '%s\n' "$REMOTE_TAGS" |
    awk '
      $2 !~ /\^\{\}$/ &&
      $2 ~ /^refs\/tags\/dist\/release\/v[0-9]+\.[0-9]+\.[0-9]+-[0-9a-f]+$/ {
        version = $2
        sub(/^refs\/tags\/dist\/release\/v/, "", version)
        sub(/-[0-9a-f]+$/, "", version)
        counts[version]++
      }
      END {
        for (version in counts) {
          if (counts[version] > 1) {
            print version, counts[version]
          }
        }
      }
    ' |
    sort
)"

FAILED=0
while read -r VERSION COUNT; do
  [ -n "${VERSION:-}" ] || continue
  echo "❌ v$VERSION has $COUNT dist/release tags; each version may publish exactly one artifact." >&2
  FAILED=1
done <<EOF
$DUPLICATE_VERSIONS
EOF

if [ "$FAILED" -ne 0 ]; then
  echo "❌ Release-tag uniqueness gate failed: one or more versions have duplicate dist/release tags." >&2
  echo "Archive the duplicates under dist/archive/*. The likely cause is a git push --tags from a clone holding stale local tags." >&2
  exit 1
fi

echo "Release-tag uniqueness gate passed."
