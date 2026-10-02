# Approval Aliases

Date: 2026/09/29

Automation: CodeCraft protection hook

## Intent

Accept the standalone replies `approve`, `a`, `yes`, and `y` as equivalent human confirmations for an exact pending protected change.

## Diagnosis

The hook already accepted `approve`, `yes`, and `y`. Earlier rejections occurred when approval preceded the first blocked attempt, because no exact command hash was pending yet. Only `a` was absent from the recognized affirmations.

## Test-First Evidence

`ApprovalAliasesTest.test_should_accept_requested_approval_aliases` exercised all four requested replies. It initially failed only for `a` while the other three passed.

## Smallest Implementation

Added `a` to `ProtectionPolicy.AFFIRMATIONS`. Exact-command hashing, the pending-change requirement, and single-use consumption remain unchanged.

## Verification

- Focused approval-alias test: passing
- Complete Java suite: 27 tests passing
- Complete workflow-automation suite: 21 tests passing
- Habit Hooks: all enforced checks passing
- Canonical command: `./mvnw verify`

## Decision

Approval replies remain standalone and case-insensitive. Broader sentences are not parsed as authorization, preserving narrow intent.

## Evolution in CodeCraft 0.7.0

Protected changes can now be prepared before their first mutation attempt. The preparation command records an exact normalized tool-input digest without granting permission, so a later standalone alias authorizes that first unchanged attempt. Authorization is reserved until PostToolUse reports the outcome rather than being consumed before the tool runs.
