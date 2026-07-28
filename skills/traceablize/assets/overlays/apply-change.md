Exit code: 0
Wall time: 2.4 seconds
Output:
This extension is mandatory where it adds executable-task classification, split history,
or pause controls. Keep all compatible behavior from the official apply workflow.

## Mandatory termination gate

Before any final reply, pause report, or end-of-turn, read `tasks.md` again and apply
this gate in order:

1. If any unfinished `[local]` task remains, Do not end the implementation. Continue
   applying the change; an external dependency, a partial implementation, or a completed
   response turn is not a reason to stop.
2. A `[local]` task can be checked only with implementation, applicable automated tests,
   and verification-command evidence. A port, interface, table, mock declaration, or
   task note alone does not clear the task.
3. Only after no unfinished `[local]` task remains may an `external-adapter` or
   `product-decision` block progress. Then use the pause ledger or the confirmed
   external-follow-up protocol below; never present that state as full implementation.
4. For a long-running change, maintain a progress ledger in the change directory and
   resume from it after each response turn. The ledger must show completed tasks,
   remaining local tasks, blocked external tasks, and the next executable action.

## Executable-task contract

1. Before implementation, read every change artifact and inventory each incomplete task
   as exactly one class:

   - `local`: independently executable in the current repository;
   - `external-adapter`: requires a named external contract, service, broker, or module;
   - `product-decision`: requires a stated product or business decision.

   A task must not mix classes. A missing external contract is not evidence that an
   independently executable local task is blocked.

2. Complete **all executable local tasks** before attempting an external adapter or
   reporting a pause. A local task is complete only with applicable implementation,
   migrations, API or UI evidence, automated tests, and verification-command evidence.
   A table, port, fake, or placeholder alone is not completion.

3. For a cross-module capability, implement the local port, state model, migrations,
   in-memory or fake adapter, applicable API/UI boundary, and local automated tests as a
   `local` task. Record real Kafka, RPC, service, broker, or module integration as a
   separate `external-adapter` task.

## External follow-up handoff protocol

Treat an incomplete `external-adapter` or `product-decision` task as a handoff
**candidate** only after completing all executable `local` tasks in the current change.
Do not transfer an item merely because it mentions an external system. When the current
repository has a usable official interface, fake, mock, in-memory adapter, contract test,
or local environment, implement and test the applicable local capability before treating
the remaining dependency as external.

For a genuinely blocked candidate, create or update
`openspec/changes/<current-change>/external-follow-up.md` in the current change root. It
must retain the original task number, the exact external dependency or product decision,
the remaining scope, and a handoff link placeholder. This candidate record is not a task
completion or authorization to create another change.

Until there is **explicit user confirmation** to hand off the candidate:

- Do not create `openspec/external-follow-up-registry.yaml`.
- Do not mark the original task complete.
- Do not create a follow-up change.

After explicit user confirmation, assign a unique `EXT-*` identifier and create or update
the project-level `openspec/external-follow-up-registry.yaml`. Record the confirmed item
with `status: approved`, `originalChange`, `originalTask`, and `targetChange`. The original
task retains its number, the precise dependency or decision, and a link to the `EXT-*`
registry entry and approved target change. The follow-up change is a subsequent
responsibility: create it only after the approved registry entry identifies its
`targetChange`; do not retroactively mark the original task complete merely because the
handoff was approved.

Use `externalItems` for the registry collection. A confirmed item may include
`followUpChange` only as the link to the approved `targetChange`; it does not authorize
creating that change before confirmation.

## Legacy mixed task split

When a legacy mixed task mixes a local capability with external integration or a product
decision, split it before implementation rather than pausing the entire change. Update
the task list with one or more replacement tasks, each having exactly one class. Preserve
the original task number as a parent reference and write a short task-note entry with:

- original task number and text;
- split reason;
- replacement task IDs and their classes;
- the external dependency or decision, where applicable.

Do not silently rewrite the task or claim that the original task was completed. Continue
with every newly created executable `local` replacement task.

## Pause gate and ledger

Report `Implementation Paused` only when every remaining incomplete task is genuinely
blocked and no executable `local` task remains. A pause report MUST contain this four-column
ledger: `completed tasks`, `still-executable tasks`, `blocked tasks`, and
`exact dependency or decision`. If the still-executable column is non-empty, pausing is
invalid: continue applying the change.

For each blocked task, identify the named external contract, service, broker, module, or
product decision required to resume. Do not use a missing repository, an absent runtime,
or a broad integration concern to hide independent local work.

The Mandatory termination gate applies again immediately before ending the response: a
non-empty local-task ledger means continue implementation, not `Implementation Paused`.
