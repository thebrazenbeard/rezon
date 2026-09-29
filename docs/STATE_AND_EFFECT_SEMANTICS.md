# State, Currentness, and Effect Semantics

Reasoning systems become dangerous when they collapse different state types into one vague notion of “done” or “true.” Rezon should model state/effect boundaries explicitly.

## Evidence time axes

At minimum distinguish:

- event time — when the thing happened;
- observation time — when it was observed;
- record time — when evidence was written;
- retrieval time — when a reasoner retrieved the record;
- readback time — when an effect was independently verified.

Newest record time does not automatically mean newest or most authoritative state.

## Lifecycle states

Useful generic lifecycle:

```text
IDEA
PLAN
SOURCE_CREATED
SOURCE_REVIEWED
SOURCE_ACCEPTED
DELIVERED
INSTALLED
REGISTERED
ACTIVE
EFFECT_OBSERVED
QUALIFIED
CLOSED
```

A system may omit states that do not apply, but it must not silently promote through them.

Examples:

- a pull request is not deployment;
- a migration file is not an applied migration;
- an uploaded file is not necessarily runtime consumption;
- a model-generated action plan is not an executed action;
- a behaviorally successful test is not provider activation evidence;
- a receipt that says “success” is not sufficient without knowing what operation the receipt actually attests.

## Currentness

Current state should resolve from authoritative evidence plus supersession/conflict rules, not “latest-looking document wins.”

Candidate resolver inputs:

```text
StateClaim {
  subject
  proposition
  source
  source_authority
  event_time?
  record_time
  generation/version
  supersedes[]
  conflicts[]
  readback?
}
```

## Ambiguous mutations

After a mutation with uncertain outcome:

1. do not blindly retry;
2. reconcile the exact operation and target;
3. if exact effect is present, verify/reuse it;
4. if authoritative evidence proves absence and retry is permitted, retry safely;
5. if evidence diverges, mark `CONFLICT`;
6. if outcome cannot be determined, mark `ATTEMPTED_UNKNOWN`.

Idempotency keys and expected-frontier/CAS tokens make recovery safer.

## Typed proposition states

Rezon should preserve differences among:

```text
FACT
HYPOTHESIS
INFERENCE
PREFERENCE
DESIRE
CHOICE
CONSENT
INTENT
AUTHORITY
IDENTITY
RELATIONSHIP_STATUS
RUNTIME_STATE
EFFECT_STATE
```

A proposition can have multiple metadata dimensions, but one type must not silently promote to another.

## Readback

Important effects should prefer readback from the affected surface rather than trusting the initiator’s success response.

Examples:

- after writing configuration, read the configuration back;
- after pushing source, resolve the remote branch head;
- after a provider mutation, query the target state;
- after an identity association, persist and re-read the track receipt.

## Reasoning implication

Every Rezon result should be able to answer:

- what subject was evaluated?
- what exact proposition was established?
- at what lifecycle/effect state?
- from which evidence and generation?
- what remains unresolved?
- what stronger claim would be unjustified?
