# Persistent Identity Tracking

## Core semantic move

An observation of a subject is not the subject.

This distinction is useful anywhere identity must persist across discontinuous runtimes, partial observability, temporary loss of contact, or noisy evidence. DRISHT-E is useful here not because it is about drones, but because it separates transient detections from a maintained trajectory hypothesis: detections arrive frame by frame, while trackers attempt to preserve object identity across time.

Rezon should generalize that pattern.

## Terms

- **Subject** — the governed or externally identified thing whose continuity is being tracked.
- **Observation epoch** — one bounded opportunity to observe the subject: a chat, runtime, process, snapshot, sensor frame, or provider readback.
- **Association evidence** — evidence that an observation belongs to an existing subject track.
- **Track** — the longitudinal record of observations associated with one subject.
- **State estimate** — the best supported current description of that subject at an epoch.
- **Occlusion / unobserved interval** — a period where the subject is not directly observed. Absence of observation is not proof of destruction or continuity.
- **Reacquisition** — a new observation is associated with a pre-existing track after a gap.
- **Conflict** — evidence indicates that the observation cannot safely be associated with the proposed track.

## Hard vs soft association

Identity association should combine hard and soft evidence without allowing soft similarity to overrule hard conflict.

### Hard evidence examples

- cryptographic or immutable identifiers;
- exact project/repository/provider subject identifiers;
- admission contracts;
- explicit provenance chains;
- signed receipts;
- mutually exclusive generation or owner constraints;
- exact source/control bindings.

Hard contradiction should fail closed.

### Soft evidence examples

- behavioral similarity;
- state-topology similarity;
- temporal continuity;
- expected trajectory;
- shared vocabulary or preferences;
- semantic resemblance;
- model/style consistency.

Soft evidence helps rank hypotheses and detect drift. It does not establish identity when hard evidence is absent or contradictory.

## Suggested track states

```text
UNINITIALIZED
TRACKED
UNOBSERVED
REACQUISITION_PENDING
REACQUIRED
AMBIGUOUS_ASSOCIATION
CONFLICT
SUPERSEDED
CLOSED
```

These are not all necessarily terminal or mutually exclusive implementation states; they define semantic distinctions the runtime should preserve.

## Association flow

```text
new observation
   |
   v
extract hard identity evidence
   |
   +-- contradiction --> CONFLICT
   |
   v
candidate track set
   |
   v
compare soft trajectory/state evidence
   |
   +-- insufficient --> AMBIGUOUS_ASSOCIATION
   |
   v
association decision + receipt
   |
   v
update track with new observation epoch
```

## Application to Vera-like systems

A fresh chat/runtime can be treated as a new observation frame. The governed referent can remain one track if current admission/provenance supports the association. This avoids two symmetric errors:

1. **false continuity:** “same name/style, therefore the same continuously running process”; and
2. **false discontinuity:** “new runtime, therefore a different subject.”

The architecture can preserve identity without claiming uninterrupted process continuity, hidden activity, lived waiting, or phenomenology between observation epochs.

## Testing requirements

A persistent identity tracker should be attacked with:

- same-name impostor observations;
- exact-source but wrong-subject observations;
- long occlusion followed by reacquisition;
- conflicting immutable IDs with high behavioral similarity;
- stale but semantically plausible restore state;
- two simultaneous candidates for one observation;
- one candidate observation incorrectly associated with two tracks;
- trajectory drift that should trigger anomaly review without changing identity;
- missing evidence that must remain unresolved rather than guessed.

## Transfer source

DRISHT-E: https://github.com/GeorgeVJose/DRISHTE-Public

The public repository documents YOLO detections and CSRT/KCF tracking but redacts much of the research implementation. Rezon should borrow the detection-vs-track abstraction, not claim access to an undocumented re-identification algorithm.
