# .agents/ — cross-harness skill surface (Tier 2)

This directory is the **Tier 2 Skills** adapter: Agent Skills layout for
harnesses that do not read `.claude/skills/` (Cursor, Codex, Gemini CLI, and
others that follow the Agent Skills standard).

It is generated. Do not edit files under `skills/` by hand.

```bash
python3 scripts/generate-agents-skills.py          # write adapters
python3 scripts/generate-agents-skills.py --check  # CI drift gate
```

Canonical skills live in `.claude/skills/`. The generator copies each
`SKILL.md` (and instruction companions such as `AGENT_INSTRUCTIONS.md`) here,
strips Claude-only frontmatter (`hooks:`, `context:`, `model_routing:`), and
leaves user-authored `skills/*-custom/` directories untouched.

These copies are **adapters, not a second source of truth.** A 3-skill
hand-mirror cannot stay current; generation is how this surface stays at
parity with the canonical set.

Claude Code remains the **Tier 3 Full** reference (hooks, injectors,
self-learning). That is a stated position — see
[`docs/architecture/HARNESS-CAPABILITY.md`](../docs/architecture/HARNESS-CAPABILITY.md)
and the tier table in the root README.

Instruction-honesty and configuration-truth tests still cover the generated
files (`core/tests/test_instruction_honesty.py`,
`core/tests/test_granola_configuration_truth.py`,
`core/tests/test_harness_capability_contract.py`,
`scripts/check-instructed-tools.py`). Change a canonical skill, regenerate,
re-run those tests.

This directory is `brain`-classed in the portable ownership contract and is
provisioned into installs (`core/provision-contract.json`). User-authored
variants belong in `.agents/skills/*-custom/`, which updates never touch.
