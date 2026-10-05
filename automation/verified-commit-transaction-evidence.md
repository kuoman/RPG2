# Verified Commit Transaction Evidence

## Decision

CodeCraft Starter 0.5.1 adds one receipt-bound commit transaction. A read-only `prepare` command reports the exact lane, base commit, signed-receipt digest, candidate and evidence paths and content digests, Arlo message, and transaction identity. After human approval, one guarded `execute` operation stages those exact paths, checks the staged receipt, creates one path-limited commit, and checks the committed receipt.

The transaction never pushes and does not authorize later reuse. A changed base, receipt, manifest path, candidate content, evidence content, lane, or message produces a different identity and fails closed.

## Triggering evidence

The same interaction occurred in three consecutive behavior increments:

- IP-061: staging consumed the protected approval before the Element 2 commit.
- IP-066: the same split recurred for Element 3.
- IP-071: the same split recurred for Element 4 and reached the automation threshold.

Each case used one already-approved candidate and evidence manifest, but the old guard bound approval to a single tool call while the committer used separate `git add` and `git commit --only` calls. The new helper preserves the two validations inside one guard-visible transaction rather than weakening or bypassing protected-path detection.

## Executable boundary coverage

The clean-room Starter suite proves that:

- the distribution installs the helper as executable managed machinery;
- execution over a protected BDD path is denied until an accepted human affirmation;
- compound or environment-wrapped helper commands fail closed instead of bypassing manifest inspection;
- the approval is single-use;
- changed evidence invalidates the prepared identity before staging;
- only the exact candidate and evidence paths enter the commit;
- unrelated work remains outside the commit;
- the approved Arlo message is preserved;
- the committed receipt is current; and
- reuse fails after the base commit changes.

The existing receipt tests continue to cover invalid signatures, stale candidates, changed verification inputs, and exact commit-path binding.

## Verification record

- Pre-change doctor: `CodeCraft Starter 0.4.1: healthy`
- Outside red: the new install assertion, helper execution, and guard recognition tests failed before machinery existed.
- Implementation check: 55 Starter tests passed; 9 Java tests ran with 8 passing and 1 intentionally skipped.
- Package check: `CodeCraft package: healthy`
- Intermediate upgrade doctor: `CodeCraft Starter 0.5.0: healthy`
- Review hardening release: 0.5.1 rejects compound helper commands before manifest inspection.
- Final package check: `CodeCraft package: healthy`
- Final post-upgrade doctor: `CodeCraft Starter 0.5.1: healthy`

## Process learning

The first upgrade attempt was correctly blocked for a standalone protected approval, but its retry required an avoidable second interaction after the host sandbox rejected writes under `.agents`. The escalated retry had the same semantic command but a different guard digest because 0.4.1 hashes host-only tool metadata. Future preparation should include known filesystem escalation before the human checkpoint. Semantic transaction identities should remain independent of sandbox transport metadata.
