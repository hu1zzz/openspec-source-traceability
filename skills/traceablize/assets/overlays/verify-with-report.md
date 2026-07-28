Exit code: 0
Wall time: 2.3 seconds
Output:
This extension is mandatory and takes precedence only where it adds exhaustive
inventory coverage and persistent reporting. Keep all compatible behavior from the
official verify workflow.

## Exhaustive verification and persistent report

1. Inventory every task, Requirement, Scenario, source mapping, and key design
   decision before judging implementation.
2. Give every item one explicit status: `VERIFIED`, `PARTIAL`, `UNVERIFIED`,
   `ENVIRONMENT_REQUIRED`, or `NOT_APPLICABLE`. A checkbox or keyword match is not
   proof.
3. Verify implementation and automated-test evidence separately, citing
   repository-relative `path:line` references.
4. For traceability, read the original source document or work package,
   `source-inventory.yaml`, `source-requirements.yaml`, delta and main Specs,
   implementation, and test evidence. Verify every inventory row semantically; cite
   repository-relative `path:line` references wherever the source format permits.

   - `SRC-*` is the stable workflow ID. `externalId` and `revision` are optional
     source metadata and must not be assumed to follow a fixed pattern.
   - For each row, record source locator, extraction limitation, mapping/Spec links,
     acceptance-point links, code evidence, test evidence, status, and next action.
   - do not invoke a fixed-format parser and do not infer a pass from zero parsed rows.
     If a scanned PDF, image, table, missing document, or other format prevents reliable
     review, record the limitation and use `PARTIAL` or `UNVERIFIED`.
5. Audit executable-task discipline before accepting task completion or a pause:

   - Every task must display exactly one class: `local`, `external-adapter`, or
     `product-decision`. A task with mixed execution classes is `PARTIAL` and prevents
     `PASS`.
   - For every replacement of a legacy task, require a task-note that states the
     original task number, split reason, and replacement task IDs. An unexplained task split is
     `UNVERIFIED` and prevents `PASS`.
   - The replacement task IDs must be unique, must exist in `tasks.md`, and each
     replacement ID's execution class must match the replacement task's declared class.
     A missing, duplicate, or class-mismatched replacement ID is `UNVERIFIED` and
     prevents `PASS`.
   - A port, interface, schema/table, TODO, mock declaration, or other placeholder is
     not sufficient local-task evidence. Require applicable implementation artifacts,
     migrations, API/UI evidence, automated tests, and verification-command evidence.
   - If a report says `Implementation Paused`, include completed tasks,
     still-executable tasks, blocked tasks, and the exact dependency or decision for
     each blocker. A pause with any remaining executable `local` task, or without this
     ledger, is an invalid pause and prevents `PASS`.

6. Audit external follow-up state separately from local implementation:

   - An unconfirmed candidate recorded in `external-follow-up.md` is `UNVERIFIED`.
     It has no authorized handoff and must retain the original task, blocker, and next
     local or confirmation action in the ledger.
   - A registry entry is an authorized handoff only when its registry state is
     `status: approved` or `status: in-progress`, it has an `EXT-*` ID, and its complete traceability fields are
     mutually consistent with the current report: `targetChange`, `generatedChange`,
     `originalChange`, `originalTask`, at least one source ID, at least one Requirement
     ID, at least one acceptance point, and the dependency chain. Record those fields,
     plus `followUpChange`, `externalItems`, and a concrete next action in the report.
     It is `PARTIAL` and must not count as implemented or `VERIFIED`: the handoff
     records ownership of remaining work, not evidence that the behavior exists locally.
   - A candidate, a `cancelled` or other non-authorizing registry status, a missing
     complete traceability field, a contradictory chain, or a local item without
     verification is not an authorized handoff. Keep it `UNVERIFIED` or `PARTIAL` and
     make it a `FAIL` cause.
   - Classify a local behavior as `VERIFIED` only when implementation evidence,
     automated-test evidence, and successful verification-command evidence are all
     present. Missing any of those is `PARTIAL` or `UNVERIFIED` as appropriate.
   - Keep candidates, authorized handoffs, and locally verified behavior as distinct
     report rows; never upgrade one state merely because another state exists.

7. Apply the coverage gate:

   ```text
   inventory source-item count == report source-item rows
   parsed Requirement count == report Requirement rows
   parsed Scenario count    == report Scenario rows
   parsed task count        == report task rows
   unique parsed IDs        == unique reported IDs
   ```

8. Always write `<changeRoot>/verification-report.md`, including on failure. The
   report is Chinese-first and contains: 运行元数据、执行摘要、覆盖门禁、任务核验台账、
   需求证据矩阵、场景证据矩阵、来源需求追踪（含来源定位、可选 externalId 与提取限制）、设计一致性、验证命令、问题清单、
   环境验证、最终评估.
9. Every non-VERIFIED ledger row requires a concrete action.
10. Result is `FAIL` for incomplete tasks, failed required commands, traceability
   errors, inventory mismatch, `UNVERIFIED`, missing, contradictory behavior, or any
   `PARTIAL` row that is not an authorized handoff as defined above. Use
   `ENVIRONMENT_VERIFICATION_REQUIRED` when only real-environment evidence remains.
11. Use `PASS_WITH_AUTHORIZED_HANDOFF` exactly once as the final result only when all
   local items are `VERIFIED`, every remaining `PARTIAL` row is an authorized handoff,
   and the coverage gate passes. The report must explicitly state that those external
   items are not implemented locally. This result permits sync/archive for the current
   change's reduced local scope; it does not permit treating handoffs as implemented.
12. Never claim all specs implemented unless the coverage gate passes and the final
   result is `PASS`; the qualified-handoff result is explicitly not that claim.
