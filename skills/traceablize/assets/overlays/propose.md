This extension is mandatory and takes precedence only where it adds traceability rules.
Keep all compatible behavior from the official propose workflow.

## Requirement-to-Spec traceability

1. Require a concrete source requirement document and use the
   `traceable-spec-driven` schema.
2. Before creating the change baseline, build a complete, auditable inventory of the
   supplied requirement document. Extract every identifiable source requirement in
   document order with its ID, revision, title, section, and normalized-content SHA-256
   (title plus requirement body, excluding export-only metadata). Persist it in the
   change directory as `source-inventory.md` or an equivalent auditable record.

   - Treat the entire supplied document as in scope by default. The change name is an
     identifier, not authority to silently discard another section of the document.
   - Mark a requirement `not-applicable` or `excluded` only when the user explicitly
     limited scope or the requirement itself states a clear exclusion. Record the scope
     decision, user instruction, and reason; never infer it solely from a heading or
     domain label.
   - Compare each inventory entry with current main specs by exact `ID@Revision` and
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
   source ID and revision. Create `source-requirements.yaml` only for in-scope added,
   revision-modified, or content-modified requirements. Preserve source IDs, revisions,
   and content hashes. Initial entries use `status: pending` and `specs: []`. The
   Chinese file header must document every permitted status and change type.
4. Put metadata immediately before every Spec Requirement heading:

   ```markdown
   <!--
   id: REQ-PC-001
   sources:
     - SwRS-100@1
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
8. After propose, offer the non-gating command:
   `python "需求追踪验证工具\validate_source_traceability.py" --change <name>`.
9. Never create an empty or README-only Spec delta just to complete OpenSpec artifacts.
   If the verified, user-authorized inventory has no in-scope added or modified
   requirements, stop as a no-op and report that no OpenSpec change is needed; do not
   report the change as implementation-ready.
