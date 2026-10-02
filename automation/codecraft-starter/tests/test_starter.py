import json
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from xml.etree import ElementTree


PACKAGE = Path(__file__).parents[1]
sys.path.insert(0, str(PACKAGE / "bin"))

from codecraft_starter import Doctor, StarterDistribution


class StarterDistributionTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.target = Path(self.temporary_directory.name) / "sample"
        self.target.mkdir()
        subprocess.run(["git", "init", "--quiet"], cwd=self.target, check=True)
        wrapper = self.target / "mvnw"
        wrapper.write_text("#!/bin/sh\nexit 0\n")
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
        (self.target / "AGENTS.md").write_text("# Existing project instructions\n")
        (self.target / ".gitignore").write_text("target/\n")
        self.distribution = StarterDistribution(PACKAGE)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_should_install_a_self_contained_java_maven_workflow(self):
        result = self.distribution.install(self.target, "Sample Service")

        self.assertEqual("installed CodeCraft Starter 0.3.0", result)
        self.assertTrue((self.target / ".agents/skills/codecraft/SKILL.md").is_file())
        self.assertTrue((self.target / ".agents/skills/committer/SKILL.md").is_file())
        self.assertTrue((self.target / ".codecraft/bin/codecraft_doctor.py").is_file())
        self.assertTrue((self.target / ".codecraft/bin/verify_increment.py").is_file())
        self.assertTrue((self.target / ".codecraft/bin/codecraft_run.py").is_file())
        self.assertTrue((self.target / ".codecraft/hooks/protect_assets.py").is_file())
        self.assertTrue((self.target / ".codex" / "hooks.json").is_file())
        self.assertTrue((self.target / ".claude/rules/codecraft.md").is_file())
        self.assertIn("🍀", (self.target / ".claude/rules/always.md").read_text())
        self.assertIn("Sample Service", (self.target / "automation/codecraft-working-agreement.md").read_text())
        self.assertIn("BEGIN CODECRAFT", (self.target / "AGENTS.md").read_text())
        self.assertIn(".claude/rules/always.md", (self.target / "AGENTS.md").read_text())
        self.assertIn(".codecraft/state/", (self.target / ".gitignore").read_text())
        installation = json.loads((self.target / ".codecraft/installation.json").read_text())
        self.assertEqual("0.3.0", installation["version"])
        self.assertEqual("java-maven", installation["profile"])
        self.assertEqual([], Doctor(self.target).problems())

    def test_should_be_idempotent_when_the_same_version_is_installed_again(self):
        self.distribution.install(self.target, "Sample Service")

        result = self.distribution.install(self.target, "Sample Service")

        self.assertEqual("CodeCraft Starter 0.3.0 is already installed", result)

    def test_should_preserve_project_owned_files_during_an_upgrade(self):
        self.distribution.install(self.target, "Sample Service")
        agreement = self.target / "automation/codecraft-working-agreement.md"
        agreement.write_text(agreement.read_text() + "\nLocal agreement.\n")
        review_ledger = self.target / "automation/review-decisions.json"
        review_ledger.write_text('[{"id":"local","decision":"defer"}]\n')
        conventions = self.target / ".claude/rules/always.md"
        conventions.write_text(conventions.read_text() + "\nLocal emoji convention.\n")

        result = self.distribution.upgrade(self.target)

        self.assertEqual("CodeCraft Starter 0.3.0 is current", result)
        self.assertIn("Local agreement.", agreement.read_text())
        self.assertIn('"local"', review_ledger.read_text())
        self.assertIn("Local emoji convention.", conventions.read_text())

    def test_should_manage_one_active_run_as_compact_resumable_context(self):
        self.distribution.install(self.target, "Sample Service")
        subprocess.run(["git", "config", "user.name", "CodeCraft Test"], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.email", "codecraft@example.invalid"], cwd=self.target, check=True)
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "baseline"], cwd=self.target, check=True)
        runner = self.target / ".codecraft/bin/codecraft_run.py"

        subprocess.run(
            [
                str(runner),
                "start",
                "sample-run",
                "--kind",
                "automation",
                "--objective",
                "Preserve compact workflow context",
                "--next-actor",
                "ai",
                "--next-action",
                "Implement the approved automation",
                "--context",
                "automation/codecraft-working-agreement.md",
            ],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                str(runner),
                "advance",
                "implementation",
                "--actor",
                "ai",
                "--next-action",
                "Run the focused test",
                "--command",
                "./mvnw test",
            ],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )
        resumed = subprocess.run(
            [str(runner), "resume"],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("RUN: sample-run (automation)", resumed.stdout)
        self.assertIn("STAGE: implementation", resumed.stdout)
        self.assertIn("NEXT [ai]: Run the focused test", resumed.stdout)
        self.assertIn("COMMAND: ./mvnw test", resumed.stdout)
        self.assertTrue((self.target / ".codecraft/state/runs/sample-run.json").is_file())

    def test_should_refuse_to_overwrite_a_locally_changed_managed_file(self):
        self.distribution.install(self.target, "Sample Service")
        skill = self.target / ".agents/skills/codecraft/SKILL.md"
        skill.write_text(skill.read_text() + "\nLocal managed edit.\n")

        with self.assertRaisesRegex(ValueError, "managed-file conflict"):
            self.distribution.upgrade(self.target)

        self.assertIn("Local managed edit.", skill.read_text())

    def test_should_report_missing_commands_and_managed_files(self):
        self.distribution.install(self.target, "Sample Service")
        (self.target / "mvnw").unlink()
        (self.target / ".codecraft/bin/verify_increment.py").unlink()

        problems = Doctor(self.target).problems()

        self.assertTrue(any("verification command" in problem for problem in problems))
        self.assertTrue(any("verify_increment.py" in problem for problem in problems))

    def test_should_detect_tampered_installation_state(self):
        self.distribution.install(self.target, "Sample Service")
        manifest = self.target / ".codecraft/installation.json"
        installation = json.loads(manifest.read_text())
        installation["managed"]["invented.txt"] = "0" * 64
        manifest.write_text(json.dumps(installation))

        problems = Doctor(self.target).problems()

        self.assertTrue(any("signature is invalid" in problem for problem in problems))
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            self.distribution.upgrade(self.target)

    def test_should_refuse_an_existing_managed_file_without_partial_installation(self):
        skill = self.target / ".agents/skills/codecraft/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("existing\n")

        with self.assertRaisesRegex(ValueError, "existing-file conflict"):
            self.distribution.install(self.target, "Sample Service")

        self.assertEqual("existing\n", skill.read_text())
        self.assertFalse((self.target / ".codecraft/installation.json").exists())
        self.assertFalse((self.target / "automation/codecraft-working-agreement.md").exists())

    def test_should_roll_back_a_partially_applied_installation(self):
        original_agents = (self.target / "AGENTS.md").read_bytes()
        original_ignore = (self.target / ".gitignore").read_bytes()
        real_write = self.distribution.atomic_write
        calls = 0

        def fail_during_install(path, content, mode):
            nonlocal calls
            calls += 1
            if calls == 4:
                raise OSError("injected write failure")
            real_write(path, content, mode)

        with mock.patch.object(self.distribution, "atomic_write", side_effect=fail_during_install):
            with self.assertRaisesRegex(OSError, "injected write failure"):
                self.distribution.install(self.target, "Sample Service")

        self.assertEqual(original_agents, (self.target / "AGENTS.md").read_bytes())
        self.assertEqual(original_ignore, (self.target / ".gitignore").read_bytes())
        self.assertFalse((self.target / ".agents/skills/codecraft/SKILL.md").exists())
        self.assertFalse((self.target / ".codecraft/installation.json").exists())

    def test_should_validate_the_installed_skills(self):
        self.distribution.install(self.target, "Sample Service")
        installed_validator = self.target / ".codecraft/bin/validate_skill.py"

        codecraft = subprocess.run([str(installed_validator), str(self.target / ".agents/skills/codecraft")], check=True, capture_output=True, text=True)
        committer = subprocess.run([str(installed_validator), str(self.target / ".agents/skills/committer")], check=True, capture_output=True, text=True)

        self.assertIn("Skill is valid!", codecraft.stdout)
        self.assertIn("Skill is valid!", committer.stdout)

    def test_should_verify_and_bind_a_clean_room_increment_to_its_commit(self):
        self.distribution.install(self.target, "Sample Service")
        subprocess.run(["git", "config", "user.name", "CodeCraft Test"], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.email", "codecraft@example.invalid"], cwd=self.target, check=True)
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "baseline"], cwd=self.target, check=True)
        note = self.target / "notes.md"
        note.write_text("clean room\n")
        candidate = self.target.parent / "candidate.paths"
        candidate.write_text("notes.md\n")
        verifier = self.target / ".codecraft/bin/verify_increment.py"

        verification = subprocess.run(
            [str(verifier), "documentation", "--candidate-file", str(candidate)],
            cwd=self.target,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, verification.returncode, verification.stderr)
        subprocess.run(["git", "add", "notes.md"], cwd=self.target, check=True)
        subprocess.run(
            [str(verifier), "documentation", "--candidate-file", str(candidate), "--check", "--staged"],
            cwd=self.target,
            check=True,
        )
        subprocess.run(["git", "commit", "--quiet", "-m", "d Add note", "--only", "--", "notes.md"], cwd=self.target, check=True)
        result = subprocess.run(
            [str(verifier), "documentation", "--candidate-file", str(candidate), "--check", "--check-commit", "HEAD"],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("verification receipt is current", result.stdout)

    def test_should_require_single_use_approval_for_an_existing_behavior_test(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        patch = "*** Begin Patch\n*** Update File: " + protected + "\n@@\n-original\n+changed\n*** End Patch"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"command": patch},
            "tool_use_id": "change-1",
            "cwd": str(self.target),
        }

        denied = self.run_guard(guard, event)
        self.run_guard(guard, {"hook_event_name": "UserPromptSubmit", "prompt": "a", "cwd": str(self.target)})
        approved = self.run_guard(guard, event)
        self.run_guard(guard, {**event, "hook_event_name": "PostToolUse"})
        denied_again = self.run_guard(guard, {**event, "tool_use_id": "change-2"})

        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
        self.assertEqual({}, approved)
        self.assertEqual("deny", denied_again["hookSpecificOutput"]["permissionDecision"])

    def test_should_upgrade_unchanged_managed_files_and_preserve_project_evolution(self):
        self.distribution.install(self.target, "Sample Service")
        agreement = self.target / "automation/codecraft-working-agreement.md"
        agreement.write_text(agreement.read_text() + "\nProject evolution.\n")
        next_package = Path(self.temporary_directory.name) / "codecraft-starter-0.4.0"
        shutil.copytree(PACKAGE, next_package)
        (next_package / "VERSION").write_text("0.4.0\n")
        skill_source = next_package / "payload/agents/codecraft-skill.md"
        skill_source.write_text(skill_source.read_text() + "\nDistribution improvement.\n")

        result = StarterDistribution(next_package).upgrade(self.target)

        self.assertEqual("CodeCraft Starter 0.4.0 is current", result)
        self.assertIn("Distribution improvement.", (self.target / ".agents/skills/codecraft/SKILL.md").read_text())
        self.assertIn("Project evolution.", agreement.read_text())
        installation = json.loads((self.target / ".codecraft/installation.json").read_text())
        self.assertEqual("0.4.0", installation["version"])

    def test_should_apply_an_explicit_safe_managed_file_removal_migration(self):
        self.distribution.install(self.target, "Sample Service")
        next_package = Path(self.temporary_directory.name) / "codecraft-starter-0.4.0"
        shutil.copytree(PACKAGE, next_package)
        (next_package / "VERSION").write_text("0.4.0\n")
        manifest = next_package / "payload/manifest.json"
        definition = json.loads(manifest.read_text())
        removed_entry = definition["managed"].pop()
        definition["migrations"] = [
            {
                "from": "0.3.0",
                "to": "0.4.0",
                "removeManaged": [removed_entry["target"]],
            }
        ]
        manifest.write_text(json.dumps(definition))
        (next_package / "payload" / removed_entry["source"]).unlink()

        StarterDistribution(next_package).upgrade(self.target)

        self.assertFalse((self.target / removed_entry["target"]).exists())

    def test_should_reject_a_payload_target_outside_the_repository(self):
        unsafe_package = Path(self.temporary_directory.name) / "unsafe-package"
        shutil.copytree(PACKAGE, unsafe_package)
        manifest = unsafe_package / "payload/manifest.json"
        definition = json.loads(manifest.read_text())
        definition["managed"][0]["target"] = "../escape.md"
        manifest.write_text(json.dumps(definition))

        with self.assertRaisesRegex(ValueError, "target is unsafe"):
            StarterDistribution(unsafe_package).install(self.target, "Sample Service")

        self.assertFalse((self.target.parent / "escape.md").exists())

    def test_should_run_starter_tests_and_fingerprint_the_package_during_project_verification(self):
        repository = Path(__file__).parents[3]
        namespace = {"maven": "http://maven.apache.org/POM/4.0.0"}
        project = ElementTree.parse(repository / "java/pom.xml")
        executions = project.findall(".//maven:execution", namespace)
        identifiers = [execution.findtext("maven:id", namespaces=namespace) for execution in executions]
        lanes = json.loads((repository / ".codecraft/completion-lanes.json").read_text())

        self.assertIn("verify-codecraft-starter", identifiers)
        self.assertIn("automation/codecraft-starter/**/*", lanes["lanes"]["automation"]["inputs"])

    def test_should_validate_the_distribution_manifest_and_payload(self):
        self.assertEqual([], self.distribution.package_problems())

    def test_should_reject_unexpected_release_artifacts(self):
        changed_package = Path(self.temporary_directory.name) / "changed-package"
        shutil.copytree(PACKAGE, changed_package)
        (changed_package / "unexpected.tmp").write_text("not part of the release\n")

        problems = StarterDistribution(changed_package).package_problems()

        self.assertTrue(any("unexpected release files" in problem for problem in problems))

    def test_should_reject_changed_distribution_content_under_the_same_version(self):
        self.distribution.install(self.target, "Sample Service")
        changed_package = Path(self.temporary_directory.name) / "changed-package"
        shutil.copytree(PACKAGE, changed_package)
        skill = changed_package / "payload/agents/codecraft-skill.md"
        skill.write_text(skill.read_text() + "\nUnversioned change.\n")

        with self.assertRaisesRegex(ValueError, "version content changed"):
            StarterDistribution(changed_package).install(self.target, "Sample Service")

    def test_should_reject_changed_installer_content_on_a_direct_same_version_upgrade(self):
        self.distribution.install(self.target, "Sample Service")
        changed_package = Path(self.temporary_directory.name) / "changed-package"
        shutil.copytree(PACKAGE, changed_package)
        installer = changed_package / "bin/codecraft_starter.py"
        installer.write_text(installer.read_text() + "\n# changed installer\n")

        with self.assertRaisesRegex(ValueError, "version content changed"):
            StarterDistribution(changed_package).upgrade(self.target)

    def test_should_reject_a_distribution_downgrade(self):
        newer_package = Path(self.temporary_directory.name) / "codecraft-starter-0.4.0"
        shutil.copytree(PACKAGE, newer_package)
        (newer_package / "VERSION").write_text("0.4.0\n")
        StarterDistribution(newer_package).install(self.target, "Sample Service")

        with self.assertRaisesRegex(ValueError, "downgrade"):
            self.distribution.upgrade(self.target)

    def test_should_upgrade_after_the_target_repository_moves(self):
        self.distribution.install(self.target, "Sample Service")
        moved = self.target.parent / "moved-sample"
        shutil.move(self.target, moved)

        result = self.distribution.upgrade(moved)

        self.assertEqual("CodeCraft Starter 0.3.0 is current", result)
        self.assertTrue((moved / ".agents/skills/codecraft/SKILL.md").is_file())

    def test_should_reject_non_repository_and_escaping_project_paths_before_writing(self):
        plain = Path(self.temporary_directory.name) / "plain"
        plain.mkdir()

        with self.assertRaisesRegex(ValueError, "Git repository"):
            self.distribution.install(plain, "Plain")
        with self.assertRaisesRegex(ValueError, "project path"):
            self.distribution.install(self.target, "Sample Service", test_root="../outside")

        self.assertFalse((plain / ".codecraft").exists())
        self.assertFalse((self.target / ".codecraft/installation.json").exists())

    def test_should_reject_symlinked_merge_and_append_targets_before_writing(self):
        outside_agents = self.target.parent / "outside-agents.md"
        outside_ignore = self.target.parent / "outside-ignore"
        outside_agents.write_text("outside agents\n")
        outside_ignore.write_text("outside ignore\n")
        (self.target / "AGENTS.md").unlink()
        (self.target / ".gitignore").unlink()
        (self.target / "AGENTS.md").symlink_to(outside_agents)
        (self.target / ".gitignore").symlink_to(outside_ignore)

        with self.assertRaisesRegex(ValueError, "symlink"):
            self.distribution.install(self.target, "Sample Service")

        self.assertEqual("outside agents\n", outside_agents.read_text())
        self.assertEqual("outside ignore\n", outside_ignore.read_text())
        self.assertFalse((self.target / ".codecraft/installation.json").exists())

    def test_should_refuse_to_adopt_an_unrecorded_managed_instruction_block(self):
        (self.target / "AGENTS.md").write_text(
            "<!-- BEGIN CODECRAFT -->\nLocal block\n<!-- END CODECRAFT -->\n"
        )

        with self.assertRaisesRegex(ValueError, "managed-block conflict"):
            self.distribution.install(self.target, "Sample Service")

        self.assertIn("Local block", (self.target / "AGENTS.md").read_text())

    def test_should_render_quoted_project_names_as_valid_json(self):
        self.distribution.install(self.target, 'A "Quoted" Service')

        project = json.loads((self.target / ".codecraft/project.json").read_text())

        self.assertEqual('A "Quoted" Service', project["projectName"])

    def test_should_validate_append_targets_as_part_of_package_integrity(self):
        unsafe_package = Path(self.temporary_directory.name) / "unsafe-append-package"
        shutil.copytree(PACKAGE, unsafe_package)
        manifest = unsafe_package / "payload/manifest.json"
        definition = json.loads(manifest.read_text())
        definition["appendLines"][0]["target"] = "../outside-ignore"
        manifest.write_text(json.dumps(definition))

        problems = StarterDistribution(unsafe_package).package_problems()

        self.assertTrue(any("target is unsafe" in problem for problem in problems))

    def test_should_protect_non_shell_write_tools(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": str(source), "content": "changed\n"},
            "tool_use_id": "write-1",
            "cwd": str(self.target),
        }

        denied = self.run_guard(guard, event)

        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])

    def test_should_atomically_reserve_a_single_approval(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        patch = "*** Begin Patch\n*** Update File: " + protected + "\n@@\n-original\n+changed\n*** End Patch"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"command": patch},
            "tool_use_id": "change-1",
            "session_id": "session-1",
            "cwd": str(self.target),
        }
        self.run_guard(guard, event)
        self.run_guard(
            guard,
            {"hook_event_name": "UserPromptSubmit", "prompt": "approve", "session_id": "session-1", "cwd": str(self.target)},
        )

        first = self.run_guard(guard, event)
        second = self.run_guard(guard, {**event, "tool_use_id": "change-2"})

        self.assertEqual({}, first)
        self.assertEqual("deny", second["hookSpecificOutput"]["permissionDecision"])

    def test_should_not_reuse_an_approval_from_another_session(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": str(source), "content": "changed\n"},
            "tool_use_id": "write-1",
            "session_id": "session-1",
            "cwd": str(self.target),
        }
        self.run_guard(guard, event)
        self.run_guard(
            guard,
            {"hook_event_name": "UserPromptSubmit", "prompt": "y", "session_id": "session-1", "cwd": str(self.target)},
        )

        denied = self.run_guard(guard, {**event, "session_id": "session-2"})

        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])

    def test_should_retain_approval_after_a_harmless_tool_failure(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": str(source), "content": "changed\n"},
            "tool_use_id": "write-1",
            "session_id": "session-1",
            "cwd": str(self.target),
        }
        self.run_guard(guard, event)
        self.run_guard(
            guard,
            {"hook_event_name": "UserPromptSubmit", "prompt": "a", "session_id": "session-1", "cwd": str(self.target)},
        )
        self.run_guard(guard, event)
        self.run_guard(guard, {**event, "hook_event_name": "PostToolUse", "tool_response": {"success": False}})

        retry = self.run_guard(guard, {**event, "tool_use_id": "write-2"})

        self.assertEqual({}, retry)

    def test_should_detect_glob_and_dynamic_shell_targets(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"

        glob = self.run_guard(
            guard,
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "rm src/test/java/*_bdd.java"},
                "tool_use_id": "shell-1",
                "cwd": str(self.target),
            },
        )
        dynamic = self.run_guard(
            guard,
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python3 -c 'mutate_a_computed_path()'"},
                "tool_use_id": "shell-2",
                "cwd": str(self.target),
            },
        )

        self.assertEqual("deny", glob["hookSpecificOutput"]["permissionDecision"])
        self.assertEqual("deny", dynamic["hookSpecificOutput"]["permissionDecision"])

    def test_should_enroll_existing_approval_companions(self):
        companion = self.target / "src/test/resources/combat.approved.txt"
        companion.parent.mkdir(parents=True, exist_ok=True)
        companion.write_text("approved output\n")

        self.distribution.install(self.target, "Sample Service")

        registered = json.loads((self.target / ".codecraft/protected-assets.json").read_text())
        self.assertIn("src/test/resources/combat.approved.txt", registered)

    def test_should_detect_a_missing_managed_instruction_block(self):
        self.distribution.install(self.target, "Sample Service")
        (self.target / "AGENTS.md").write_text("# Existing project instructions\n")

        problems = Doctor(self.target).problems()

        self.assertTrue(any("managed block" in problem for problem in problems))

    def test_should_not_issue_a_receipt_when_candidate_changes_during_verification(self):
        note = self.target / "notes.md"
        note.write_text("verified version\n")
        mutation = f"from pathlib import Path; Path({str(note)!r}).write_text('raced version\\n')"
        self.distribution.install(self.target, "Sample Service", verify_command=f"python3 -c {mutation!r}")
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.name", "CodeCraft Test"], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.email", "codecraft@example.invalid"], cwd=self.target, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "baseline"], cwd=self.target, check=True)
        note.write_text("verified version\n")
        candidate = self.target.parent / "candidate-race.paths"
        candidate.write_text("notes.md\n")
        verifier = self.target / ".codecraft/bin/verify_increment.py"

        result = subprocess.run(
            [str(verifier), "behavior", "--candidate-file", str(candidate)],
            cwd=self.target,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertFalse((self.target / ".codecraft/state/behavior-verification.json").exists())

    def test_should_reject_a_symlink_candidate_from_isolated_verification(self):
        self.distribution.install(self.target, "Sample Service", verify_command="true")
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.name", "CodeCraft Test"], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.email", "codecraft@example.invalid"], cwd=self.target, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "baseline"], cwd=self.target, check=True)
        outside = self.target.parent / "outside-note.md"
        outside.write_text("outside\n")
        (self.target / "notes.md").symlink_to(outside)
        candidate = self.target.parent / "candidate-symlink.paths"
        candidate.write_text("notes.md\n")
        verifier = self.target / ".codecraft/bin/verify_increment.py"

        result = subprocess.run(
            [str(verifier), "behavior", "--candidate-file", str(candidate)],
            cwd=self.target,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)

    def test_should_reject_governing_automation_from_the_documentation_lane(self):
        self.distribution.install(self.target, "Sample Service")
        governing = self.target / "automation/local-policy.md"
        governing.write_text("policy\n")
        candidate = self.target.parent / "governing.paths"
        candidate.write_text("automation/local-policy.md\n")
        verifier = self.target / ".codecraft/bin/verify_increment.py"

        result = subprocess.run(
            [str(verifier), "documentation", "--candidate-file", str(candidate)],
            cwd=self.target,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("documentation lane", result.stderr)

    def run_guard(self, guard, event):
        result = subprocess.run(
            [sys.executable, str(guard)],
            input=json.dumps(event),
            cwd=self.target,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout) if result.stdout else {}


if __name__ == "__main__":
    unittest.main()
