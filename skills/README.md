# Karmada Agent Skills

This directory contains seven self-contained Agent Skills for Karmada users, operators, and
contributors. Each `karmada-*` directory is an independently installable package containing its own
`SKILL.md` and runtime references.

## Choose a skill

| Skill | Use it for |
| --- | --- |
| `karmada-knowledge` | Architecture, concepts, APIs, and object flow. |
| `karmada-create-policy` | Creating propagation and override policies from explicit intent. |
| `karmada-audit-policy` | Reviewing supplied Karmada policy YAML. |
| `karmada-explain-placement` | Explaining an observed cluster or replica placement. |
| `karmada-debug-propagation` | Tracing a concrete workload propagation incident. |
| `karmada-search` | Operating or developing Karmada Search. |
| `karmada-controller-manager` | Operating or developing `karmada-controller-manager`. |

A focused workflow does not need to invoke `karmada-knowledge` first.

## Install and use

Install either all seven directories or only the workflows you need. Copy the complete skill
directory because `SKILL.md` loads package-local `references/` when needed. The `evals/` directory
is contributor evaluation tooling and must not be installed as a skill.

Inspect an existing destination before copying. `cp -R` merges directories and does not remove
files deleted by a newer version of a skill.

### Codex

Codex discovers personal skills from `$HOME/.agents/skills` and repository skills from
`.agents/skills` between the current working directory and repository root.

Personal installation:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R skills/karmada-* "$HOME/.agents/skills/"
```

Repository-scoped installation from this community repository:

```bash
mkdir -p /path/to/karmada/.agents/skills
cp -R skills/karmada-* /path/to/karmada/.agents/skills/
```

Codex can select a skill from a natural-language request. Use `/skills` or a `$` mention to invoke
one explicitly:

```text
$karmada-audit-policy Review this PropagationPolicy and separate API errors from operational risks.
```

Restart Codex if a newly installed skill does not appear. See the official
[Codex skill documentation](https://learn.chatgpt.com/docs/build-skills) for discovery behavior.

### Claude Code

Claude Code discovers personal skills from `$HOME/.claude/skills` and project skills from
`.claude/skills` between the starting directory and repository root.

Personal installation:

```bash
mkdir -p "$HOME/.claude/skills"
cp -R skills/karmada-* "$HOME/.claude/skills/"
```

Project-scoped installation from this community repository:

```bash
mkdir -p /path/to/karmada/.claude/skills
cp -R skills/karmada-* /path/to/karmada/.claude/skills/
```

Claude can select a skill automatically or invoke one directly:

```text
/karmada-debug-propagation The binding selected member-a, but no Work was created. Start read-only.
```

Restart Claude Code when a newly created top-level skill directory is not discovered. See the
official [Claude Code skill documentation](https://code.claude.com/docs/en/skills) for details.

### GitHub Copilot CLI

GitHub Copilot CLI discovers personal skills from `$HOME/.copilot/skills` and project skills from
`.github/skills`, `.agents/skills`, or `.claude/skills`.

Personal installation:

```bash
mkdir -p "$HOME/.copilot/skills"
cp -R skills/karmada-* "$HOME/.copilot/skills/"
```

Project-scoped installation from this community repository:

```bash
mkdir -p /path/to/karmada/.github/skills
cp -R skills/karmada-* /path/to/karmada/.github/skills/
```

Alternatively, register this checkout without copying it:

```bash
copilot skill add "$(pwd)/skills"
```

Keep the registered checkout at the same absolute path. Verify discovery with
`copilot skill list`. Describe the task normally and Copilot will select a relevant skill:

```text
Explain why this Karmada ResourceBinding selected member-a.
```

Use `/karmada-explain-placement` only when automatic selection is ambiguous or you want to invoke
that skill explicitly.

See the official [GitHub Copilot CLI skill documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
for discovery and skill management details.

## Evidence boundaries

The skills distinguish three evidence levels:

1. packaged knowledge for stable concepts and bounded workflows;
2. a compatible Karmada checkout for exact API, validation, implementation, and test claims;
3. supplied objects, events, logs, status, configuration, and inventory for runtime claims.

Environment-specific claims require supplied configuration, inventory, or runtime evidence; Karmada
source does not establish them.

The skills do not replace Karmada admission, controllers, scheduler, or live-cluster diagnosis.
They do not authorize production mutation merely because a likely remediation is known.

## Repository layout

```text
skills/
  README.md
  karmada-*/                Seven installable runtime skills
    SKILL.md
    references/
  evals/                    Evaluation cases, scenarios, runners, and gates
    README.md
```

There is no generated `dist/` layer. Each `karmada-*` directory is both source and installable
package. Runtime files must not depend on sibling skills, evaluation files, public web pages, local
absolute paths, or client-specific metadata.

Everything needed only to develop or evaluate the collection lives under `evals/`. See
[evals/README.md](evals/README.md) for the evaluation model, directory roles, commands, result
artifacts, release gate, and human review workflow.

## Contribute

Keep each runtime skill self-contained. Put routing, workflow, and safety instructions in
`SKILL.md`; put detailed runtime knowledge in package-local `references/`.

When routing changes, update positive, adjacent near-miss, and cross-skill cases. When output
behavior changes, update observable correctness and safety assertions rather than matching exact
prose. Use current Karmada API, validation, implementation, and tests for exact source claims.

Write documentation, instructions, references, scenarios, and evaluation prompts in English.
Unicode remains valid when technically or linguistically appropriate. Never infer country, region,
zone, provider, or topology from a cluster name.

To add a skill, include:

- `karmada-<workflow>/SKILL.md` with a matching lowercase frontmatter name;
- package-local runtime references;
- balanced positive and near-miss trigger cases;
- package-only output cases with assertion severity and safety metadata; and
- routing cases against adjacent workflows.

Run deterministic validation before submitting a change:

```bash
python3 skills/evals/scripts/run_deterministic.py \
  --root . \
  --output /path/to/results/deterministic.json
```

The release gate and human review procedure are documented in
[evals/README.md](evals/README.md).
