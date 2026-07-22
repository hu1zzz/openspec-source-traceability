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
4. For traceability, read the source document or work package, `source-inventory.yaml`,
   `source-requirements.yaml`, delta and main Specs, implementation, and test evidence.
   Verify every inventory row semantically with source locator, optional `externalId`,
   mapping/Spec links, code/test evidence, status, and next action.

   - Do not invoke a fixed-format parser or infer a pass from zero parsed rows.
   - If a scanned PDF, image, table, missing document, or other format prevents reliable
     review, record the limitation and use `PARTIAL` or `UNVERIFIED`.
5. Apply the coverage gate:

   ```text
   inventory source-item count == report source-item rows
   parsed Requirement count == report Requirement rows
   parsed Scenario count    == report Scenario rows
   parsed task count        == report task rows
   unique parsed IDs        == unique reported IDs
   ```

6. Always write `<changeRoot>/verification-report.md`, including on failure. The
   report is Chinese-first and contains: 运行元数据、执行摘要、覆盖门禁、任务核验台账、
   需求证据矩阵、场景证据矩阵、来源需求追踪、设计一致性、验证命令、问题清单、
   环境验证、最终评估.
7. Every non-VERIFIED ledger row requires a concrete action.
8. Result is `FAIL` for incomplete tasks, failed required commands, traceability
   errors, inventory mismatch, `PARTIAL`, `UNVERIFIED`, missing, or contradictory
   behavior. Use `ENVIRONMENT_VERIFICATION_REQUIRED` when only real-environment
   evidence remains.
9. Never claim all specs implemented unless the coverage gate passes and the final
   result is `PASS`.
