This extension is mandatory for traceable implementation and preserves all compatible
official apply behavior.

## Executable-task gate

1. Classify every pending task as exactly one of `local`, `external-adapter`, or
   `product-decision`. A task that mixes classes is a legacy mixed task.
2. Complete all executable local tasks before considering a pause. A missing external
   broker, RPC contract, service, or product decision never blocks independent local work.
3. For a legacy mixed task, update `tasks.md` to split it into local and external or
   decision replacements. Add a task-note recording the original task number, split
   reason, replacement task IDs, and exact dependency. Keep replacement IDs unique.
4. For cross-module capability, first implement local ports, state model, migrations,
   in-memory/fake adapter, applicable API/UI boundary, automated tests, and verification
   evidence. Put real Kafka/RPC/service integration in a separate `external-adapter` task.
5. Mark a task complete only with applicable implementation, migration, API/UI, test,
   and verification-command evidence; a port or placeholder alone is not completion.
6. `Implementation Paused` is valid only when no executable local task remains. Its
   report must separately list completed tasks, still-executable tasks, blocked tasks,
   and the exact dependency or decision for each blocker.
