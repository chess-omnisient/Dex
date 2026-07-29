# Release-fleet acceptance for Dex updates

This is the release gate for the promise that no existing Dex installation is
left behind. It is deliberately stricter than the normal unit tests: a green
test of the updater source does not prove that a person running an old,
published Dex can reach it.

## What must pass

Every distinct tree behind the published `dist/release/v*` tags is a starting
case. If two tags point at different trees—even when they share the same
version number—they are separate cases. Byte-identical trees are one case.

Each case must complete two real update hops:

1. **Historic release to the foundation release.** The foundation is the first
   public release containing the self-delivering updater. Use the old vault's
   own `/dex-update` instructions. If that old route safely refuses, follow
   only its documented one-time rescue route. Record the user-visible wording,
   approval prompts, final release identity, and `/dex-doctor` verdict.
2. **Foundation release to a follow-up release.** From the same fixture, run
   `/dex-update` again. This hop must use the foundation release's delivery
   path: fetch the exact verified release, show the exact preview, collect a
   fresh approval, and commit the receipt-backed update. Record the same
   evidence.

For both hops, the fixture's user-owned hashes must be identical before and
after. A changed hash, an unknown result, a missing transcript, a missing
receipt, or an unhealthy Doctor result is a failure—not something to explain
away.

## Build the historic fixtures

Use a fresh temporary directory. The builder never copies a founder's vault
and refuses to overwrite an existing case.

```bash
fleet_root=$(mktemp -d /private/tmp/dex-release-fleet.XXXXXX)
python3 scripts/release_fleet.py build --repo . --output "$fleet_root" \
  > "$fleet_root/manifest.json"
```

`manifest.json` records each immutable starting tag, commit, tree, fixture
path, and the exact hashes of the synthetic user content that must survive.
The starting source must be public distribution tags; never use `main`, a
working tree, or an untagged release candidate as a historical starting point.

## Validate the finished evidence

After both release tags are public and every case has its journey transcript
and report entry, validate the report against the full tag set:

```bash
python3 scripts/release_fleet.py check-report --repo . REPORT.json
```

The command passes only when the report covers every discovered starting tree
and every case has reached both hops, kept its user hashes unchanged, has a
healthy Doctor result after each hop, and names a user-visible transcript.

## Claim language

Before this check passes, say only that the updater is implemented and locally
tested. After it passes against the two actual public tags on every supported
platform, it is accurate to say that historical Dex installations have a
proven path to the normal `/dex-update` experience.
