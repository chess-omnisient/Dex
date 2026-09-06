# Release catalog item declarations

This is the publisher-owned source of truth for lifecycle catalog items. The
release builder reads every JSON file here in filename order, except the
separately modeled `bridge-release.json` and the generated
`release-hashes.json`, and emits the canonical
`System/.release-catalog.json` through the B1 model and schema.

`bridge-release.json` keeps the publisher-owned bridge contract and transaction
journal compatibility window. During a release build, the same generator that
emits `System/.release-catalog.json` stamps only its `release_version` from
`package.json`, validates the complete declaration through the strict bridge
model, and ships both files with the same version. The checked-in declaration
matches the repository package version for local development; it is not a
placeholder and the release build does not weaken the runtime equality check.

Each source file is a closed document:

```json
{
  "catalog_source_version": 1,
  "items": [
    {
      "id": "decision-log",
      "kind": "skill",
      "version": "1.0.0",
      "files": [
        {
          "path": ".claude/skills/decision-log/SKILL.md",
          "source_path": ".claude/skills/decision-log/SKILL.md",
          "sha256": "<exact lowercase sha256>",
          "byte_size": 1234
        }
      ],
      "dependencies": [],
      "capabilities": []
    }
  ]
}
```

`path` is the active transaction target. Optional `source_path` is the
release-shipped payload whose exact bytes adoption writes there; when omitted,
it defaults to `path`. The paths are identical for files that ship active,
while optional capabilities can remain dormant until an approved adoption. The
publisher declaration pins each payload's exact hash and byte size. The
generator rejects stale pins, derives target ownership classes and rewind
tokens from the exact release tree, and validates the emitted items through the
v1 model and schema. The first official item declarations live in
`official-capabilities.json`.

## `release-hashes.json` — the whole-tree hash table (generated)

The catalog's `items` prove only the publisher-declared capability payloads.
Full release identity for every other shipped file lives in a **sibling
whole-tree hash table**, `core/lifecycle/catalog/release-hashes.json`, which
the release build generates and the catalog binds by the exact SHA-256 of the
table's bytes in the optional `release.hash_table` field:

```json
"hash_table": {
  "path": "core/lifecycle/catalog/release-hashes.json",
  "sha256": "<sha256 of the table's exact bytes>"
}
```

The table itself is a closed canonical-JSON document (sorted keys, compact
separators, UTF-8, one trailing newline):

```json
{
  "hash_table_version": 1,
  "release": {"version": "<release semver>", "source_commit": "<full commit>"},
  "files": {"<release-relative path>": "<sha256 of exact release bytes>"}
}
```

Rows cover every installed-manifest file whose portable-contract ownership is
`brain` (release-owned), except the table itself and the catalog: the table's
own bytes are proven by the catalog binding, and the catalog is proven by its
`catalog_sha256` plus the manifest binding. Seed, generated, and runtime files
never get rows — they are legitimately rewritten after install and a hash row
would misclassify those edits as release divergence.

Consumers fail closed: `load_release_baseline` merges the table's rows into
the expected-hash baseline only when the installed catalog is verified AND the
table's bytes match the binding hash exactly (with the one centralized
CRLF→LF tolerance from `release_bytes_match`). A missing, unreadable, or
mismatched table contributes nothing — behavior is identical to a catalog
without the binding, and files whose bytes match no proven hash stay
never-pristine. Catalog item rows win over table rows on any path conflict.

An older catalog without `release.hash_table` keeps exactly its historic
behavior; the field is optional in the v2 schema and absent from the frozen
public v1 schema.
