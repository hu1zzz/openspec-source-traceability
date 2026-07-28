Exit code: 0
Wall time: 2.4 seconds
Output:
This extension is mandatory and takes precedence only where it adds traceability rules.
Keep all compatible behavior from the official propose workflow.

## Requirement-to-Spec traceability

## Approved external follow-up registry input

The normal requirement-document workflow remains the default. Activate this registry
input mode only when the user explicitly passes `openspec/external-follow-up-registry.yaml`
as the input. Do not infer registry mode from an `external-follow-up.md` file and do not
automatically generate a change from any per-change `external-follow-up.md` candidate.

1. Read the complete entries in `openspec/external-follow-up-registry.yaml`. Select only
   entries with `status: approved` and `generatedChange: null`. An entry that was already
   consumed (`generatedChange` is not null) must be rejected and reported rather than
   reused. Reject and report an entry with missing required fields, including its `EXT-*`
   identifier, `originalChange`, `originalTask`, `targetChange`, the linked `SRC-*` and
   `REQ-*` identifiers, or `acceptancePoints`.
2. Validate the complete traceability chain for every selected entry before creating any
   work: `EXT-* → SRC-* → originalChange/originalTask → REQ-* → acceptancePoints`.
   Reject and report any inconsistent link, including a source, requirement, original
   change/task, or acceptance point that cannot be reconciled with the registry and
   referenced change artifacts.
3. First group them by `targetChange`. Multiple entries in the same target group may retain
   separate, complete traceability chains; each entry must carry its own `EXT-* → SRC-* →
   originalChange/originalTask → REQ-* → acceptancePoints` links. Reject only when fields
   within the same entry contradict one another, or the merged functional scope or
   objectives cannot all be satisfied. For each valid group, generate the follow-up
   OpenSpec change named by its `targetChange`, carrying every complete selected registry
   entry and its full traceability chain into the generated proposal, specs, design, and
   tasks.
4. Only after a group has been generated successfully, update each corresponding registry
   entry to `status: in-progress` and set `generatedChange` to that generated change
   name. Do not update rejected entries.
5. Do not generate a change when no approved entries exist. Report this no-op explicitly,
   as well as the distinct rejection reasons for no approved entries, missing fields,
   already consumed entries, target change conflicts, and inconsistent traceability.

Registry mode is an explicit alternate input path; when it is not activated, continue
the normal requirement-document inventory and proposal flow unchanged.

1. Require a concrete source requirement document and use the
   `traceable-spec-driven` schema.
2. As the first internal propose phase, build `source-inventory.yaml` in the change
   directory. The user does not run a separate inventory command. Read the supplied
   requirement document or selected work package directly and list every identifiable
   source item in document order.

   - Assign the workflow's stable `SRC-001`, `SRC-002`, and subsequent IDs. Do not
     derive them from, or require, any source-system naming convention.
   - Preserve an original identifier only when present, as optional `externalId`.
     `revision` is also optional. Record a usable `locator`, title or concise content,
     normalized-content `contentHash`, and any extraction `limitation`.

   - Treat the entire supplied document as in scope by default. The change name is an
     identifier, not authority to silently discard another section of the document.
   - Mark a requirement `not-applicable` or `excluded` only when the user explicitly
     limited scope or the requirement itself states a clear exclusion. Record the scope
     decision, user instruction, and reason; never infer it solely from a heading or
     domain label.
   - Compare each inventory entry with current main specs by stable `SRC-*` ID and
     available revision/hash evidence, and with prior inventories or archives by
     normalized-content SHA-256. If content
     changed without a revision increase, register it as `changeType: modified`, set
     `contentChangedWithoutRevision: true`, retain prior/current hashes when available,
     and surface the source-document revision defect to the user.
   - Report inventory totals before creating the baseline: total found, exact main-spec
     matches, added, revision-modified, content-modified-without-revision, and proposed
     exclusions/not-applicable entries. Ask for scope direction before any exclusion
     that lacks explicit authorization.

3. Scan `openspec/specs/**/*.md`. A source requirement is already covered only when a
   main-spec Requirement has a stable `REQ-*` ID and its `sources` contains the exact
   inventory `SRC-*` ID plus available revision/hash metadata. Create
   `source-requirements.yaml` only for in-scope added,
   revision-modified, or content-modified requirements. Preserve source IDs, revisions,
   and content hashes. Initial entries use `status: pending` and `specs: []`. The
   Chinese file header must document every permitted status and change type.

   For every newly handled source requirement, extract an **acceptance-point inventory**
   before writing Specs. Each independently testable API route, request/response field,
   filter, state transition, deletion policy, validation rule, persistence rule, table
     row, or bullet becomes one stable `ACP-<inventory-id>-NNN` point. Do not collapse a
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
8. Do not invoke a fixed-format parser or infer coverage from a source-ID pattern. The
   subsequent `openspec-verify-with-report` skill reads the source document, inventory,
   mappings, Specs, code, and tests semantically.
9. Never create an empty or README-only Spec delta just to complete OpenSpec artifacts.
   If the verified, user-authorized inventory has no in-scope added or modified
   requirements, stop as a no-op and report that no OpenSpec change is needed; do not
   report the change as implementation-ready.
10. Before tasks are written, produce a coverage report that lists every source
    requirement and its acceptance-point totals (`mapped`, `uncovered`, `conflict`). A
    source-ID link alone is not evidence of semantic coverage.

## Executable-task contract

Before writing `tasks.md`, give every task exactly one execution class: `local`,
`external-adapter`, or `product-decision`. A task with mixed classes is invalid: split
it before implementation and preserve a clear dependency between the replacement tasks.

- A `local` task is independently executable in the current repository. For a
  cross-module capability, it must first deliver the local boundary and evidence:
  ports, state models, migrations, in-memory/fake adapters, applicable APIs, and
  automated tests. Include only the artifacts that apply to that task, but never treat
  a port or interface alone as completed behavior.
- An `external-adapter` task contains only a named real integration, such as Kafka,
  RPC, or another module/service. It must name the required contract or dependency and
  must follow the corresponding `local` task; do not combine real integration with
  local implementation.
- A `product-decision` task contains only an explicitly stated business or product
  decision. It must name the decision owner and the question to resolve; do not hide
  implementation work in it.

Write the class visibly in the task line, for example
`- [ ] 2.1 [local] Implement the event state and in-memory adapter.` A cross-module
requirement therefore becomes at least one `local` task and one separate
`external-adapter` task. Do not create a broad task that can be paused merely because
one downstream integration is unavailable.

## Greenfield implementation baseline

Before creating proposal, design, or tasks, inspect the intended project root for an
implementation baseline. A baseline is source code together with a recognizable build
or application entry such as `pom.xml`, `build.gradle`, `package.json`, `pyproject.toml`,
`go.mod`, `Cargo.toml`, or an equivalent project manifest. OpenSpec artifacts, source
documents, and traceability tools alone are not an implementation baseline.

- When a baseline exists, state the detected root and build entry, then continue the
  normal traceable propose workflow without greenfield questions.
- When no baseline exists, ask first: does the user want to provide an existing code
  repository/local path, or explicitly create a greenfield project? Do not create
  business implementation tasks until one answer is received.
- If an existing repository is supplied, switch to that root and repeat the baseline
  inspection. Do not treat an unverified path as a baseline.

### Greenfield interview

For an explicitly approved greenfield project, ask **one question at a time** and wait
for each answer. Never infer a technology choice from the requirement document.

1. Ask whether the project is a backend service, frontend application, or full-stack
   system.
2. For a backend, ask in separate turns for language/framework; build tool; database
   and migration approach; API style and authentication; deployment and local start
   command.
3. For a frontend, ask in separate turns for framework; package manager/build tool; UI
   approach; state management; routing; and the source of backend APIs.
4. For a full-stack system, first ask whether frontend and backend share one repository.
   Then ask the applicable backend and frontend questions above, followed by their
   communication method and local integration start command.

### Bootstrap change contract

After the interview, create or direct the user to an independent bootstrap change before
the requested business change. The bootstrap change MUST persist
`implementation-baseline.md` with every confirmed decision and the reproducible local
start command. Its proposal, design, and tasks MUST cover only the project skeleton,
minimal runnable entry, selected build tooling, required baseline configuration, and
build or foundational-test evidence.

Do not mark the business change implementation-ready in an empty project. State that it
depends on the completed bootstrap change; after bootstrap is applied and verified,
re-run `openspec-traceable-propose` for the business work package against that code
baseline. Do not invent framework, data-layer, authentication, deployment, or module
choices merely to avoid a pause during apply.
