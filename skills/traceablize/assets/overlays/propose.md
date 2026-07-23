This extension is mandatory and takes precedence only where it adds traceability rules.
Keep all compatible behavior from the official propose workflow.

## Requirement-to-Spec traceability

1. Require a concrete source requirement document and use the
   `traceable-spec-driven` schema.
2. Before creating the change baseline, build a complete, auditable inventory of the
   supplied requirement document. Extract every identifiable source requirement in
   document order. Persist it in the change directory as `source-inventory.yaml`; this
   is an internal propose phase, not a separate user command.

   - Assign stable workflow IDs `SRC-001`, `SRC-002`, and so on. Preserve an original
     identifier only when present as optional `externalId`; revision is optional too.
   - Record a locator, title or concise content, normalized-content SHA-256, and any
     extraction limitation. Never require a source-system ID format.

   - Treat the entire supplied document as in scope by default. The change name is an
     identifier, not authority to silently discard another section of the document.
   - Mark a requirement `not-applicable` or `excluded` only when the user explicitly
     limited scope or the requirement itself states a clear exclusion. Record the scope
     decision, user instruction, and reason; never infer it solely from a heading or
     domain label.
   - Compare each inventory entry with current main specs by stable `SRC-*` ID and
     available revision/hash evidence, and
     with prior inventories or archives by normalized-content SHA-256. If content
     changed without a revision increase, register it as `changeType: modified`, set
     `contentChangedWithoutRevision: true`, retain prior/current hashes when available,
     and surface the source-document revision defect to the user.
   - Report inventory totals before creating the baseline: total found, exact main-spec
     matches, added, revision-modified, content-modified-without-revision, and proposed
     exclusions/not-applicable entries. Ask for scope direction before any exclusion
     that lacks explicit authorization.

3. Scan `openspec/specs/**/*.md`. A source requirement is already covered only when a
   main-spec Requirement has a stable `REQ-*` ID and its `sources` contains the exact
   inventory ID plus available revision/hash evidence. Create `source-requirements.yaml` only for in-scope added,
   revision-modified, or content-modified requirements. Preserve source IDs, revisions,
   and content hashes. Initial entries use `status: pending` and `specs: []`. The
   Chinese file header must document every permitted status and change type.

   For every newly handled source requirement, extract an **acceptance-point inventory**
   before writing Specs. Each independently testable API route, request/response field,
   filter, state transition, deletion policy, validation rule, persistence rule, table
   row, or bullet becomes one stable `ACP-<source-id>-NNN` point. Do not collapse a
   detailed table into a single generic Requirement.

   Record each point in `source-requirements.yaml` with `id`, `text`, `status`, `specs`,
   and `scenarios`. `mapped` is permitted only when every acceptance point is mapped to
   exact `REQ-*` IDs and named `#### Scenario:` headings. Otherwise the source requirement
   MUST be `partial`, with every unmapped point listed in `uncovered` and a reason. The
   post-Spec reconciliation must check this point-level matrix in both directions.
4. Put metadata immediately before every Spec Requirement heading:

   ```markdown
   <!--
   id: REQ-PC-001
   sources:
     - SRC-001
   -->
   ```

5. After specs are generated, reopen them and reconcile `source-requirements.yaml`:
   write exact `REQ-*` IDs into `specs`, then set `mapped`, `partial`, `excluded`,
   `not-applicable`, or `conflict` with required explanations. Do not leave a fully
   processed entry as `pending`.
6. Use current main specs for incremental comparison. Archives are audit history,
   not the routine coverage baseline.
7. Do not infer links from similar wording and do not fabricate source IDs. A derived
   Requirement uses `sources: []`, `origin: derived`, and a rationale.
8. Do not invoke a fixed-format parser or infer coverage from a source-ID pattern.
   `openspec-verify-with-report` performs the later semantic evidence review.
9. Never create an empty or README-only Spec delta just to complete OpenSpec artifacts.
   If the verified, user-authorized inventory has no in-scope added or modified
   requirements, stop as a no-op and report that no OpenSpec change is needed; do not
   report the change as implementation-ready.
10. Before tasks are written, produce a coverage report that lists every source
    requirement and its acceptance-point totals (`mapped`, `uncovered`, `conflict`). A
    source-ID link alone is not evidence of semantic coverage.

## Executable task contract

Every task must be exactly one class: `local`, `external-adapter`, or
`product-decision`; never mix local implementation with an external integration or
product decision. Split cross-module work so a local task delivers ports, state model,
migrations, in-memory/fake adapter, applicable API/UI, automated tests, and verification
evidence. Put Kafka/RPC/real-service integration in a separate `external-adapter` task.
