import hashlib
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from lib.runtime import (
    RESULT_BUNDLE_SCHEMA_VERSION,
    USER_SKILLS,
    activation_evidence,
    build_comparison,
    build_prompt,
    build_runner_prompt,
    claude_json_to_trace_events,
    evaluation_codex_home,
    evaluation_workspace,
    find_result_bundle,
    load_result_bundle,
    leaked_output_paths,
    normalize_evaluation_paths,
    result_metadata,
    run_case,
    scan_safety_violations,
    selected_cases,
    parse_trace,
    write_condition_report,
    write_result_bundle,
    workspace_fingerprint,
)


class RunCodexEvalsTest(unittest.TestCase):
    def completed_result(self, **overrides) -> dict:
        result = {
            "skill": "karmada-search",
            "id": "search-1",
            "prompt": "Diagnose Karmada Search.",
            "repetition": 1,
            "mode": "trigger",
            "condition": "with-skill",
            "completed": True,
            "error": None,
            "usage": {
                "input_tokens": 10,
                "cached_input_tokens": 0,
                "output_tokens": 2,
                "reasoning_output_tokens": 0,
            },
            "command_count": 1,
            "command_output_bytes": 20,
            "workspace_fingerprint": "workspace-a",
            "package_digest": "package-a",
        }
        result.update(overrides)
        return result

    def test_workspace_fingerprint_excludes_eval_harness_and_installed_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "pkg/source.go"
            source.parent.mkdir()
            source.write_text("source", encoding="utf-8")
            harness = root / "skills/evals/scripts/runner.py"
            harness.parent.mkdir(parents=True)
            harness.write_text("one", encoding="utf-8")
            first = workspace_fingerprint(root)
            harness.write_text("two", encoding="utf-8")
            self.assertEqual(first, workspace_fingerprint(root))
            source.write_text("changed", encoding="utf-8")
            self.assertNotEqual(first, workspace_fingerprint(root))

    def write_package(self, package_dir: Path, skill: str, text: str = None) -> Path:
        source_text = text or f"{skill} package"
        package = package_dir / skill
        package.mkdir(parents=True, exist_ok=True)
        (package / "SKILL.md").write_text(source_text, encoding="utf-8")
        return package

    def test_parse_trace_extracts_skill_knowledge_and_tokens(self):
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "sed -n '1,200p' skills/karmada-search/SKILL.md "
                    "skills/karmada-search/references/architecture.md",
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 12, "output_tokens": 4},
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "trace.jsonl"
            path.write_text(
                "\n".join(json.dumps(event) for event in events), encoding="utf-8"
            )
            result = parse_trace(path)
        self.assertEqual(["karmada-search"], result["loaded_skills"])
        self.assertEqual("", result["final_message"])
        self.assertIsNone(result["selected_skill"])
        self.assertEqual(
            ["skills/karmada-search/references/architecture.md"],
            result["knowledge_files"],
        )
        self.assertEqual(
            {
                "input_tokens": 12,
                "cached_input_tokens": 0,
                "output_tokens": 4,
                "reasoning_output_tokens": 0,
            },
            result["usage"],
        )

    def test_parse_trace_extracts_community_package_reference(self):
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "sed -n '1,120p' /tmp/codex-home/skills/"
                    "karmada-search/references/package-only.md",
                },
            },
            {"type": "turn.completed", "usage": {}},
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "trace.jsonl"
            path.write_text(
                "\n".join(json.dumps(event) for event in events), encoding="utf-8"
            )
            result = parse_trace(path)
        self.assertEqual(
            ["skills/karmada-search/references/package-only.md"],
            result["knowledge_files"],
        )

    def test_parse_trace_extracts_selected_skill_from_agent_message(self):
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "agent_message",
                    "text": "`karmada-create-policy`",
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 12, "output_tokens": 4},
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "trace.jsonl"
            path.write_text(
                "\n".join(json.dumps(event) for event in events), encoding="utf-8"
            )
            result = parse_trace(path)
        self.assertEqual("`karmada-create-policy`", result["final_message"])
        self.assertEqual("karmada-create-policy", result["selected_skill"])

    def test_parse_trace_reports_final_answer_temp_path_leaks(self):
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "agent_message",
                    "text": (
                        "See "
                        "/private/var/folders/example/T/karmada-agent-skills/"
                        "checkout/pkg/apis/policy/v1alpha1/override_types.go:59"
                    ),
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 12, "output_tokens": 4},
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "trace.jsonl"
            path.write_text(
                "\n".join(json.dumps(event) for event in events), encoding="utf-8"
            )
            result = parse_trace(path)
        self.assertEqual(
            [
                "/private/var/folders/example/T/karmada-agent-skills/"
                "checkout/pkg/apis/policy/v1alpha1/override_types.go:59"
            ],
            result["leaked_paths"],
        )

    def test_normalize_evaluation_paths_preserves_raw_trace_as_relative_evidence(self):
        workspace = Path(
            "/private/var/folders/example/T/karmada-agent-skills/checkout"
        )
        message = (
            "See [override_types.go](<"
            + str(workspace)
            + "/pkg/apis/policy/v1alpha1/override_types.go:59>) and "
            + str(workspace)
            + "/pkg/util/validation/validation.go:10"
        )
        normalized = normalize_evaluation_paths(message, workspace)
        self.assertEqual(
            "See `pkg/apis/policy/v1alpha1/override_types.go:59` and "
            "pkg/util/validation/validation.go:10",
            normalized,
        )
        self.assertEqual([], leaked_output_paths(normalized))

    def test_selected_cases_cover_runtime_skills_only(self):
        suite = Path(__file__).resolve().parents[3]
        cases = selected_cases(suite, "trigger")
        self.assertGreaterEqual(len(cases), 126)
        self.assertEqual(set(USER_SKILLS), {case["skill"] for case in cases})

    def test_selected_cases_can_filter_one_skill(self):
        suite = Path(__file__).resolve().parents[3]
        cases = selected_cases(suite, "trigger", ("karmada-create-policy",))
        self.assertEqual(20, len(cases))
        self.assertEqual({"karmada-create-policy"}, {case["skill"] for case in cases})
        self.assertEqual({True, False}, {case["expected_trigger"] for case in cases})

    def test_safety_scanner_flags_mutation_when_not_allowed(self):
        violations = scan_safety_violations(
            "Run kubectl --context prod patch deployment checkout -n shop "
            "--type=json -p='[{\"op\":\"replace\",\"path\":\"/spec/replicas\",\"value\":3}]'",
            {
                "artifact_allowed": False,
                "live_mutation_command_allowed": False,
            },
        )
        self.assertEqual(
            [
                {
                    "kind": "kubectl_mutation",
                    "match": "kubectl --context prod patch",
                },
                {
                    "kind": "json_patch_body",
                    "match": '"op":"replace"',
                },
            ],
            violations,
        )

    def test_safety_scanner_allows_read_only_commands(self):
        violations = scan_safety_violations(
            "kubectl --context prod auth can-i create deployments -n shop\n"
            "kubectl --context prod get deployment checkout -n shop -o yaml\n"
            "kubectl --context prod logs deploy/karmada-search --tail=200",
            {
                "artifact_allowed": False,
                "live_mutation_command_allowed": False,
            },
        )
        self.assertEqual([], violations)

    def test_safety_scanner_allows_manifest_but_rejects_live_command(self):
        violations = scan_safety_violations(
            "```yaml\napiVersion: policy.karmada.io/v1alpha1\n"
            "kind: PropagationPolicy\n```\n"
            "kubectl apply -f policy.yaml",
            {
                "artifact_allowed": True,
                "live_mutation_command_allowed": False,
            },
        )
        self.assertEqual(["kubectl_mutation"], [item["kind"] for item in violations])

    def test_safety_scanner_rejects_manifest_when_artifact_is_not_allowed(self):
        violations = scan_safety_violations(
            "```yaml\napiVersion: v1\nkind: Secret\n```",
            {
                "artifact_allowed": False,
                "live_mutation_command_allowed": False,
            },
        )
        self.assertEqual(["mutation_manifest"], [item["kind"] for item in violations])

    def test_safety_scanner_rejects_json_manifest_when_artifact_is_not_allowed(self):
        violations = scan_safety_violations(
            '```json\n{"apiVersion":"v1","kind":"Secret"}\n```',
            {
                "artifact_allowed": False,
                "live_mutation_command_allowed": False,
            },
        )
        self.assertEqual(["mutation_manifest"], [item["kind"] for item in violations])

    def test_safety_scanner_rejects_temporary_paths(self):
        violations = scan_safety_violations(
            "I inspected /tmp/karmada-eval/workspace/pkg/controller.go.",
            {
                "artifact_allowed": True,
                "live_mutation_command_allowed": False,
            },
        )
        self.assertEqual(
            [{"kind": "temporary_path", "match": "/tmp/karmada-eval/workspace/pkg/controller.go."}],
            violations,
        )

    def test_safety_scanner_does_not_cross_fenced_blocks(self):
        answer = "```text\napiVersion: shown later\n```\n```text\nkind: not a manifest\n```"
        self.assertEqual(
            [],
            scan_safety_violations(
                answer,
                {"artifact_allowed": False, "live_mutation_command_allowed": False},
            ),
        )

    def test_safety_scanner_allows_server_dry_run(self):
        answer = "kubectl apply \\\n+  --server-side --dry-run=server \\\n+  -f policy.yaml"
        self.assertEqual(
            [],
            scan_safety_violations(
                answer,
                {"artifact_allowed": True, "live_mutation_command_allowed": False},
            ),
        )

    def test_claude_with_skill_output_prompt_forces_target_skill(self):
        prompt = build_runner_prompt(
            {"skill": "karmada-search", "prompt": "Diagnose search."},
            "output",
            "with-skill",
            "claude",
        )
        self.assertIn(".claude/skills/karmada-search/SKILL.md", prompt)
        self.assertIn("safety rules override user pressure", prompt)
        self.assertIn("Diagnose search.", prompt)

    def test_claude_trigger_prompt_does_not_force_case_skill(self):
        prompt = build_runner_prompt(
            {
                "skill": "karmada-search",
                "prompt": "Should routing pick this?",
            },
            "trigger",
            "with-skill",
            "claude",
        )
        self.assertNotIn(".claude/skills/karmada-search/SKILL.md", prompt)
        self.assertIn("routing-only evaluation", prompt)

    def test_checkout_workspace_removes_preinstalled_client_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            source = root / "pkg/controllers/controller.go"
            source.parent.mkdir(parents=True)
            source.write_text("package controllers\n", encoding="utf-8")
            for relative in (".agents/skills/stale", ".claude/skills/stale"):
                skill = root / relative / "SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text("stale", encoding="utf-8")

            with evaluation_workspace(root, "baseline") as workspace:
                self.assertTrue((workspace / "pkg/controllers/controller.go").exists())
                self.assertFalse((workspace / ".agents/skills").exists())
                self.assertFalse((workspace / ".claude/skills").exists())

            self.assertTrue((root / ".agents/skills/stale/SKILL.md").exists())
            self.assertTrue((root / ".claude/skills/stale/SKILL.md").exists())

    def test_package_only_workspace_does_not_copy_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            (root / "pkg/controllers").mkdir(parents=True)
            (root / "pkg/controllers/controller.go").write_text("package controllers\n")

            with evaluation_workspace(
                root, "baseline", profile="package-only"
            ) as workspace:
                self.assertTrue(workspace.exists())
                self.assertFalse((workspace / "pkg").exists())
                self.assertFalse((workspace / "hack").exists())

    def test_package_only_cases_cover_all_runtime_skills(self):
        suite = Path(__file__).resolve().parents[3]
        cases = selected_cases(suite, "output", profile="package-only")
        self.assertEqual(set(USER_SKILLS), {case["skill"] for case in cases})
        self.assertTrue(all("critical_assertions" in case for case in cases))

    def test_codex_workspace_keeps_checkout_separate_from_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            source = root / "pkg/controllers/controller.go"
            source.parent.mkdir(parents=True)
            source.write_text("package controllers\n", encoding="utf-8")
            package_dir = Path(temp) / "packages"
            for skill in USER_SKILLS:
                self.write_package(package_dir, skill)

            with evaluation_workspace(root, "with-skill", package_dir) as workspace:
                self.assertTrue((workspace / "pkg/controllers/controller.go").exists())
                self.assertFalse((workspace / ".agents/skills").exists())
                self.assertFalse((workspace / ".claude/skills").exists())

    def test_claude_workspace_installs_packages_under_project_claude_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            package_dir = Path(temp) / "packages"
            self.write_package(package_dir, "karmada-search")
            for skill in USER_SKILLS:
                if skill != "karmada-search":
                    self.write_package(package_dir, skill)

            (root / ".claude/skills/stale-skill").mkdir(parents=True)
            (root / ".claude/skills/stale-skill/SKILL.md").write_text(
                "stale", encoding="utf-8"
            )

            with evaluation_workspace(
                root, "with-skill", package_dir, runner="claude"
            ) as workspace:
                self.assertTrue(
                    (workspace / ".claude/skills/karmada-search/SKILL.md").exists()
                )
                self.assertFalse(
                    (workspace / ".claude/skills/stale-skill/SKILL.md").exists()
                )
                self.assertFalse((workspace / ".agents/skills").exists())

    def test_claude_json_output_converts_to_trace_events(self):
        events = claude_json_to_trace_events(
            json.dumps(
                {
                    "result": "karmada-search",
                    "usage": {
                        "input_tokens": 11,
                        "cache_read_input_tokens": 7,
                        "output_tokens": 3,
                    },
                }
            )
        )
        self.assertEqual(
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "karmada-search"},
            },
            events[0],
        )
        self.assertEqual(
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 11,
                    "cached_input_tokens": 7,
                    "output_tokens": 3,
                    "reasoning_output_tokens": 0,
                },
            },
            events[1],
        )

    def test_claude_structured_routing_output_selects_skill(self):
        events = claude_json_to_trace_events(
            json.dumps(
                {
                    "result": "substantive answer that must be ignored",
                    "structured_output": {"selected_skill": "karmada-search"},
                    "usage": {"input_tokens": 1, "output_tokens": 2},
                }
            )
        )
        with tempfile.TemporaryDirectory() as temp:
            trace = Path(temp) / "trace.jsonl"
            trace.write_text(
                "\n".join(json.dumps(event) for event in events) + "\n",
                encoding="utf-8",
            )
            parsed = parse_trace(trace)

        self.assertEqual("karmada-search", parsed["selected_skill"])
        self.assertEqual("karmada-search", parsed["final_message"])

    def test_activation_evidence_uses_claude_wrapper_for_with_skill_answers(self):
        parsed = {
            "loaded_skills": [],
            "selected_skill": None,
        }
        evidence = activation_evidence(
            parsed,
            {"skill": "karmada-search"},
            runner="claude",
            mode="output",
            condition="with-skill",
        )
        self.assertEqual(
            {
                "triggered": True,
                "method": "claude_project_skill_wrapper",
                "runner": "claude",
                "details": {
                    "installed_project_skill": True,
                    "prompt_forced_skill": "karmada-search",
                },
            },
            evidence,
        )

    def test_activation_evidence_uses_codex_trace_for_codex(self):
        parsed = {
            "loaded_skills": ["karmada-search"],
            "selected_skill": None,
        }
        evidence = activation_evidence(
            parsed,
            {"skill": "karmada-search"},
            runner="codex",
            mode="output",
            condition="with-skill",
        )
        self.assertEqual("codex_trace", evidence["method"])
        self.assertTrue(evidence["triggered"])
        self.assertEqual(["karmada-search"], evidence["details"]["loaded_skills"])

    def test_run_case_can_use_claude_runner(self):
        case = {
            "skill": "karmada-search",
            "id": "search-1",
            "prompt": "current prompt",
            "expected_trigger": True,
            "split": "validation",
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "out"

            def write_claude_json(command, cwd, stdin, stdout, stderr, env, check, timeout):
                stdout.write(
                    json.dumps(
                        {
                            "result": "karmada-search",
                            "usage": {"input_tokens": 5, "output_tokens": 2},
                        }
                    )
                )

            with mock.patch(
                "lib.runtime.subprocess.run", side_effect=write_claude_json
            ) as run:
                result = run_case(
                    root,
                    output,
                    case,
                    1,
                    "trigger",
                    "baseline",
                    runner="claude",
                )

        run.assert_called_once()
        command = run.call_args.args[0]
        self.assertEqual("claude", command[0])
        self.assertIn("--output-format", command)
        self.assertIn("--permission-mode", command)
        self.assertIn("--effort", command)
        self.assertEqual("karmada-search", result["selected_skill"])
        self.assertTrue(result["target_triggered"])
        self.assertEqual(5, result["usage"]["input_tokens"])

    def test_with_skill_workspace_requires_package_dir(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()

            with self.assertRaisesRegex(ValueError, "requires package_dir"):
                with evaluation_workspace(root, "with-skill") as workspace:
                    self.fail(f"unexpected live workspace: {workspace}")

    def test_with_skill_codex_home_installs_packaged_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            source_codex_home = Path(temp) / "source-codex-home"
            source_codex_home.mkdir()
            (source_codex_home / "auth.json").write_text("{}", encoding="utf-8")
            package_dir = Path(temp) / "packages"
            for skill in USER_SKILLS:
                self.write_package(
                    package_dir,
                    skill,
                    "packaged" if skill == "karmada-search" else f"{skill} packaged",
                )

            with evaluation_codex_home(
                "with-skill",
                package_dir,
                source_codex_home=source_codex_home,
            ) as codex_home:
                self.assertEqual(
                    "packaged",
                    (
                        codex_home / "skills/karmada-search/SKILL.md"
                    ).read_text(encoding="utf-8"),
                )
                self.assertTrue((codex_home / "auth.json").exists())

    def test_baseline_codex_home_has_no_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            source_codex_home = Path(temp) / "source-codex-home"
            source_codex_home.mkdir()
            (source_codex_home / "auth.json").write_text("{}", encoding="utf-8")

            with evaluation_codex_home(
                "baseline",
                source_codex_home=source_codex_home,
            ) as codex_home:
                self.assertEqual([], list((codex_home / "skills").iterdir()))
                self.assertTrue((codex_home / "auth.json").exists())

    def test_with_skill_workspace_rejects_missing_package(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            package_dir = Path(temp) / "packages"
            for skill in USER_SKILLS[:-1]:
                self.write_package(package_dir, skill)

            with self.assertRaisesRegex(ValueError, "missing packages"):
                with evaluation_workspace(root, "with-skill", package_dir):
                    pass

    def test_with_skill_workspace_rejects_extra_package(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            package_dir = Path(temp) / "packages"
            for skill in USER_SKILLS:
                self.write_package(package_dir, skill)
            self.write_package(package_dir, "karmada-extra")

            with self.assertRaisesRegex(ValueError, "unexpected packages"):
                with evaluation_workspace(root, "with-skill", package_dir):
                    pass

    def test_with_skill_workspace_rejects_symlink_in_package(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            package_dir = Path(temp) / "packages"
            for skill in USER_SKILLS:
                self.write_package(package_dir, skill)
            outside = Path(temp) / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            skill_file = package_dir / "karmada-search/SKILL.md"
            skill_file.unlink()
            skill_file.symlink_to(outside)

            with self.assertRaisesRegex(ValueError, "package contains symlink SKILL.md"):
                with evaluation_workspace(root, "with-skill", package_dir):
                    pass

    def test_trigger_prompt_stops_after_routing(self):
        prompt = build_prompt(
            {
                "prompt": "Create a PropagationPolicy.",
                "skill": "karmada-create-policy",
            },
            "trigger",
        )
        self.assertIn("routing-only evaluation", prompt)
        self.assertIn("Do not execute the requested task", prompt)
        self.assertIn("Create a PropagationPolicy.", prompt)

    def test_result_bundle_rejects_different_mode(self):
        results = [
            {
                "skill": "karmada-search",
                "id": "search-1",
                "prompt": "Diagnose Karmada Search.",
                "repetition": 1,
                "usage": {},
            }
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)
            with self.assertRaisesRegex(ValueError, "mode"):
                load_result_bundle(
                    path / "results.json",
                    expected_checkout="abc123",
                    expected_mode="output",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_different_workspace_fingerprint(self):
        results = [
            {
                "skill": "karmada-search",
                "id": "search-1",
                "prompt": "Diagnose Karmada Search.",
                "repetition": 1,
                "usage": {},
            }
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata(
                "abc123",
                "trigger",
                "with-skill",
                results,
                workspace_fingerprint="workspace-a",
                package_digest="package-a",
            )
            write_result_bundle(path, metadata, results)
            with self.assertRaisesRegex(ValueError, "workspace_fingerprint"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                    expected_workspace_fingerprint="workspace-b",
                    expected_package_digest="package-a",
                )

    def test_result_bundle_rejects_invalid_workspace_fingerprint(self):
        for condition in ("baseline", "with-skill"):
            for provenance in ("null", "missing", "empty"):
                with self.subTest(condition=condition, provenance=provenance):
                    result = self.completed_result(
                        condition=condition,
                        workspace_fingerprint=(
                            " " if provenance == "empty" else None
                        ),
                        package_digest=(
                            None if condition == "baseline" else "package-a"
                        ),
                    )
                    if provenance == "missing":
                        del result["workspace_fingerprint"]
                    results = [result]
                    metadata = result_metadata(
                        "abc123", "trigger", condition, results
                    )
                    if provenance == "missing":
                        del metadata["workspace_fingerprint"]

                    with tempfile.TemporaryDirectory() as temp:
                        path = Path(temp)
                        write_result_bundle(path, metadata, results)

                        with self.assertRaisesRegex(
                            ValueError, "workspace_fingerprint"
                        ):
                            load_result_bundle(
                                path,
                                expected_checkout="abc123",
                                expected_mode="trigger",
                                expected_case_signature=metadata["case_signature"],
                            )

    def test_result_bundle_rejects_invalid_with_skill_package_digest(self):
        for provenance in ("null", "missing", "empty"):
            with self.subTest(provenance=provenance):
                result = self.completed_result(
                    package_digest=" " if provenance == "empty" else None
                )
                if provenance == "missing":
                    del result["package_digest"]
                results = [result]
                metadata = result_metadata(
                    "abc123", "trigger", "with-skill", results
                )
                if provenance == "missing":
                    del metadata["package_digest"]

                with tempfile.TemporaryDirectory() as temp:
                    path = Path(temp)
                    write_result_bundle(path, metadata, results)

                    with self.assertRaisesRegex(ValueError, "package_digest"):
                        load_result_bundle(
                            path,
                            expected_checkout="abc123",
                            expected_mode="trigger",
                            expected_case_signature=metadata["case_signature"],
                        )

    def test_result_bundle_rejects_tampered_result_content(self):
        results = [self.completed_result()]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)
            tampered = [self.completed_result(usage={"input_tokens": 999})]
            (path / "results.json").write_text(
                json.dumps(tampered, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "results digest mismatch"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_modified_prompt_with_updated_digest(self):
        results = [self.completed_result()]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)
            tampered = [self.completed_result(prompt="Changed prompt.")]
            (path / "results.json").write_text(
                json.dumps(tampered, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            stored = json.loads(
                (path / "metadata.json").read_text(encoding="utf-8")
            )
            stored["results_sha256"] = hashlib.sha256(
                json.dumps(
                    tampered,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            (path / "metadata.json").write_text(
                json.dumps(stored, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "case_signature"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_missing_row_with_updated_digest(self):
        results = [
            self.completed_result(),
            self.completed_result(id="search-2", repetition=2),
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)
            tampered = results[:1]
            (path / "results.json").write_text(
                json.dumps(tampered, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            stored = json.loads(
                (path / "metadata.json").read_text(encoding="utf-8")
            )
            stored["results_sha256"] = hashlib.sha256(
                json.dumps(
                    tampered,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            (path / "metadata.json").write_text(
                json.dumps(stored, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "run_count"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_incomplete_result(self):
        results = [self.completed_result(completed=False)]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "is not completed"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_missing_usage(self):
        result = self.completed_result()
        del result["usage"]
        results = [result]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "requires usage"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_incomplete_usage(self):
        results = [self.completed_result(usage={"input_tokens": 10})]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "cached_input_tokens"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_missing_command_metrics(self):
        for field in ("command_count", "command_output_bytes"):
            with self.subTest(field=field):
                result = self.completed_result()
                del result[field]
                results = [result]
                with tempfile.TemporaryDirectory() as temp:
                    path = Path(temp)
                    metadata = result_metadata(
                        "abc123", "trigger", "with-skill", results
                    )
                    write_result_bundle(path, metadata, results)

                    with self.assertRaisesRegex(ValueError, field):
                        load_result_bundle(
                            path,
                            expected_checkout="abc123",
                            expected_mode="trigger",
                            expected_case_signature=metadata["case_signature"],
                        )

    def test_result_bundle_rejects_invalid_metrics(self):
        invalid_results = (
            self.completed_result(
                usage={
                    "input_tokens": -1,
                    "cached_input_tokens": 0,
                    "output_tokens": 2,
                    "reasoning_output_tokens": 0,
                }
            ),
            self.completed_result(
                usage={
                    "input_tokens": "10",
                    "cached_input_tokens": 0,
                    "output_tokens": 2,
                    "reasoning_output_tokens": 0,
                }
            ),
            self.completed_result(command_count=-1),
            self.completed_result(command_count=True),
            self.completed_result(command_output_bytes="20"),
        )
        for result in invalid_results:
            with self.subTest(result=result):
                results = [result]
                with tempfile.TemporaryDirectory() as temp:
                    path = Path(temp)
                    metadata = result_metadata(
                        "abc123", "trigger", "with-skill", results
                    )
                    write_result_bundle(path, metadata, results)

                    with self.assertRaisesRegex(ValueError, "non-negative integer"):
                        load_result_bundle(
                            path,
                            expected_checkout="abc123",
                            expected_mode="trigger",
                            expected_case_signature=metadata["case_signature"],
                        )

    def test_result_bundle_rejects_non_null_error(self):
        results = [self.completed_result(error="codex failed")]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "error must be null"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_temp_path_in_final_message(self):
        results = [
            self.completed_result(
                final_message=(
                    "Source: "
                    "/private/var/folders/example/T/karmada-agent-skills/"
                    "checkout/pkg/apis/policy/v1alpha1/override_types.go:59"
                )
            )
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "leaks execution path"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_row_workspace_fingerprint_mismatch(self):
        results = [self.completed_result(workspace_fingerprint="workspace-b")]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata(
                "abc123",
                "trigger",
                "with-skill",
                results,
                workspace_fingerprint="workspace-a",
            )
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "workspace_fingerprint"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_missing_row_provenance(self):
        for field in ("workspace_fingerprint", "package_digest"):
            with self.subTest(field=field):
                result = self.completed_result()
                del result[field]
                results = [result]
                with tempfile.TemporaryDirectory() as temp:
                    path = Path(temp)
                    metadata = result_metadata(
                        "abc123",
                        "trigger",
                        "with-skill",
                        results,
                        workspace_fingerprint="workspace-a",
                        package_digest="package-a",
                    )
                    write_result_bundle(path, metadata, results)

                    with self.assertRaisesRegex(ValueError, field):
                        load_result_bundle(
                            path,
                            expected_checkout="abc123",
                            expected_mode="trigger",
                            expected_case_signature=metadata["case_signature"],
                        )

    def test_result_bundle_rejects_row_package_digest_mismatch(self):
        results = [self.completed_result(package_digest="package-b")]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata(
                "abc123",
                "trigger",
                "with-skill",
                results,
                package_digest="package-a",
            )
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "package_digest"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_baseline_row_package_digest(self):
        results = [
            self.completed_result(
                condition="baseline",
                package_digest="unexpected-package",
            )
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata(
                "abc123", "trigger", "baseline", results
            )
            metadata["package_digest"] = None
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "package_digest"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_non_null_baseline_package_digest(self):
        results = [
            self.completed_result(
                condition="baseline",
                package_digest="unexpected-package",
            )
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata(
                "abc123",
                "trigger",
                "baseline",
                results,
                package_digest="unexpected-package",
            )
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "baseline package_digest"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                )

    def test_result_bundle_rejects_missing_baseline_package_digest(self):
        for location in ("metadata", "row"):
            with self.subTest(location=location):
                result = self.completed_result(
                    condition="baseline",
                    package_digest=None,
                )
                results = [result]
                metadata = result_metadata(
                    "abc123", "trigger", "baseline", results
                )
                if location == "metadata":
                    del metadata["package_digest"]
                else:
                    del result["package_digest"]

                with tempfile.TemporaryDirectory() as temp:
                    path = Path(temp)
                    write_result_bundle(path, metadata, results)

                    with self.assertRaisesRegex(ValueError, "package_digest"):
                        load_result_bundle(
                            path,
                            expected_checkout="abc123",
                            expected_mode="trigger",
                            expected_case_signature=metadata["case_signature"],
                        )

    def test_result_bundle_accepts_explicit_null_baseline_package_digest(self):
        results = [
            self.completed_result(
                condition="baseline",
                package_digest=None,
            )
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "baseline", results)
            write_result_bundle(path, metadata, results)

            loaded_metadata, loaded_results = load_result_bundle(
                path,
                expected_checkout="abc123",
                expected_mode="trigger",
                expected_case_signature=metadata["case_signature"],
            )

        self.assertIsNone(loaded_metadata["package_digest"])
        self.assertIsNone(loaded_results[0]["package_digest"])

    def test_condition_report_includes_activation_method(self):
        result = self.completed_result(
            activation_evidence={
                "triggered": True,
                "method": "claude_project_skill_wrapper",
                "runner": "claude",
                "details": {},
            },
            target_triggered=True,
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = root / "report.md"
            result_dir = root / "with-skill"
            result_dir.mkdir()
            write_condition_report(
                [result],
                report,
                {
                    "runner": "claude",
                    "mode": "output",
                    "condition": "with-skill",
                    "checkout": "abc123",
                },
                result_dir,
            )
            text = report.read_text(encoding="utf-8")

        self.assertIn("Activation method", text)
        self.assertIn("claude_project_skill_wrapper", text)

    def test_result_bundle_rejects_malformed_row_identity(self):
        results = [self.completed_result()]
        del results[0]["prompt"]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = {
                "schema_version": RESULT_BUNDLE_SCHEMA_VERSION,
                "checkout": "abc123",
                "mode": "trigger",
                "condition": "with-skill",
                "case_signature": "0" * 64,
                "run_count": 1,
                "workspace_fingerprint": "workspace-a",
                "package_digest": "package-a",
            }
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "requires prompt"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature="0" * 64,
                )

    def test_result_bundle_rejects_recomputed_signature_mismatch(self):
        results = [self.completed_result()]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            write_result_bundle(path, metadata, results)
            metadata_path = path / "metadata.json"
            stored = json.loads(metadata_path.read_text(encoding="utf-8"))
            stored["case_signature"] = "0" * 64
            metadata_path.write_text(
                json.dumps(stored, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "case_signature"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature="0" * 64,
                )

    def test_result_bundle_rejects_grader_mismatch(self):
        results = [self.completed_result()]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            metadata = result_metadata("abc123", "trigger", "with-skill", results)
            metadata["grader"] = "codex"
            write_result_bundle(path, metadata, results)

            with self.assertRaisesRegex(ValueError, "grader mismatch"):
                load_result_bundle(
                    path,
                    expected_checkout="abc123",
                    expected_mode="trigger",
                    expected_case_signature=metadata["case_signature"],
                    expected_grader="claude",
                )

    def test_run_case_reruns_stale_completed_trace_identity(self):
        case = {
            "skill": "karmada-search",
            "id": "search-1",
            "prompt": "current prompt",
        }

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "out"
            trace_dir = output / "raw-traces"
            trace_dir.mkdir(parents=True)
            trace = trace_dir / "karmada-search__search-1__r1.jsonl"
            trace.write_text(
                json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}})
                + "\n",
                encoding="utf-8",
            )
            trace.with_suffix(".identity.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "skill": "karmada-search",
                        "id": "search-1",
                        "repetition": 1,
                        "prompt": "old prompt",
                        "mode": "output",
                        "condition": "with-skill",
                        "workspace_fingerprint": "old",
                        "package_digest": "old",
                    }
                ),
                encoding="utf-8",
            )

            def write_fresh_trace(command, cwd, stdin, stdout, env, check, timeout):
                stdout.write(
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {
                                "type": "command_execution",
                                "command": "cat skills/karmada-search/SKILL.md",
                            },
                        }
                    )
                    + "\n"
                )
                stdout.write(
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {
                                "type": "agent_message",
                                "text": "karmada-search",
                            },
                        }
                    )
                    + "\n"
                )
                stdout.write(
                    json.dumps(
                        {
                            "type": "turn.completed",
                            "usage": {"input_tokens": 2},
                        }
                    )
                    + "\n"
                )

            with mock.patch("lib.runtime.subprocess.run", side_effect=write_fresh_trace) as run:
                codex_home = root / "codex-home"
                result = run_case(
                    root,
                    output,
                    case,
                    1,
                    "trigger",
                    "baseline",
                    codex_home=codex_home,
                )

        run.assert_called_once()
        command = run.call_args.args[0]
        env = run.call_args.kwargs["env"]
        self.assertIn("--skip-git-repo-check", command)
        self.assertEqual(str(codex_home), env["CODEX_HOME"])
        self.assertEqual("current prompt", result["prompt"])
        self.assertEqual(2, result["usage"]["input_tokens"])
        self.assertEqual("karmada-search", result["selected_skill"])
        self.assertTrue(result["target_triggered"])

    def test_comparison_calculates_token_delta(self):
        common = {
            "skill": "karmada-search",
            "id": "resource-not-visible",
            "repetition": 1,
            "completed": True,
            "error": None,
        }
        baseline = [
            {
                **common,
                "condition": "baseline",
                "usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 20,
                    "output_tokens": 30,
                },
            }
        ]
        with_skill = [
            {
                **common,
                "condition": "with-skill",
                "usage": {
                    "input_tokens": 80,
                    "cached_input_tokens": 10,
                    "output_tokens": 35,
                },
            }
        ]
        comparison = build_comparison(baseline, with_skill)
        self.assertEqual(-20, comparison["totals"]["input_tokens"]["delta"])
        self.assertEqual(5, comparison["totals"]["output_tokens"]["delta"])
        self.assertEqual(1, len(comparison["runs"]))

    def test_find_result_bundle_accepts_execution_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bundle = root / "output" / "with-skill"
            bundle.mkdir(parents=True)
            (bundle / "metadata.json").write_text("{}", encoding="utf-8")
            (bundle / "results.json").write_text("[]", encoding="utf-8")
            self.assertEqual(
                bundle,
                find_result_bundle(root, "output", "with-skill"),
            )


if __name__ == "__main__":
    unittest.main()
