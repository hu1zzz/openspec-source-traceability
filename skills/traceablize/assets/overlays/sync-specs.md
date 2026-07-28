Exit code: 0
Wall time: 2.2 seconds
Output:
This extension is mandatory and takes precedence only where it adds traceability rules.
Keep all compatible behavior from the official sync workflow.

## Traceability-preserving sync

1. Preserve Requirement metadata immediately before its heading.
2. For MODIFIED or RENAMED Requirements, preserve the main-spec stable `REQ-*` ID.
   ADDED Requirements retain the delta ID. Stop on an ID conflict.
3. Treat `sources` as current provenance:
   - union different source IDs;
   - deduplicate equal ID and revision;
   - replace an older main revision with a newer delta revision;
   - stop on revision regression;
   - retain only one revision per source ID and sort deterministically.
4. Preserve `origin: derived` and `rationale` for source-free derived Requirements.
5. REMOVED deletes the entire Requirement block and its metadata.
6. Never drop `id` or `sources` during intelligent merging.
7. Use the synchronized current main specs as the coverage baseline; archives remain
   historical audit material.
8. Report IDs, operations, sources added or preserved, revisions replaced, removals,
   and conflicts.
9. Sync only locally VERIFIED behavior. A candidate or authorized handoff is not
   locally VERIFIED merely because it has an `EXT-*` ID, a `targetChange`, or an
   approved registry status; do not synchronize that unimplemented behavior as
   complete.
10. Preserve `followUpChange` and `externalItems` metadata for every transferred
    external item so the target change and remaining follow-up work stay traceable
    after synchronization, including the handoff's `EXT-*`, `targetChange`,
    `generatedChange`, `originalChange`, `originalTask`, source IDs, Requirement IDs,
    acceptance points, and dependency chain. Report preserved metadata and any attempt
    to treat a handoff as completed behavior. A `PASS_WITH_AUTHORIZED_HANDOFF` result
    permits synchronization only for locally `VERIFIED` rows; it does not synchronize
    the handoff as implemented behavior.
