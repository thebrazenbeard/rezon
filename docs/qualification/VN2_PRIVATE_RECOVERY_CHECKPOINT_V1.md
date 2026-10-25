# VN2 Rezon private checkpoint and upgrade gate

Status: **source-controlled, source-tested, non-disruptive checkpoint utility**.
Not a deployment, a live service upgrade, or permission to change credentials.

## Observed VN2 contract — 2026-10-25

- Live Rezon is a **systemd user** unit, `rezon-tkik.service`, not a root unit.
- Active source directory: `/home/patrick/.local/share/rezon-tkik` at
  `d27da3cab31ae96aff3c65385fc31354dc8aeb8c`.
- Active state: `/home/patrick/.local/state/rezon-tkik/episodes.sqlite3`.
- User unit: `/home/patrick/.config/systemd/user/rezon-tkik.service`.
- Source candidate qualified at the original observation:
  `74e952ccccc96fe7e806b826351faced21eb7fef`.
- GitHub `main` subsequently advanced to
  `d6b5a1026cd39ca1c37880296abd7acc0da4aca3` (Windows readiness-test
  SQLite handle cleanup, PR #128). The new source head is not an installed
  upgrade; this checkpoint branch is based on that revision.
- Source suite on VN2: 440 passed plus 27 subtests. Its **separate** disposable
  gateway canary passed authenticated HMAC challenge, replay denial and readiness.
- The unchanged production gateway and Granite inferer stayed healthy. The six
  new readiness SQL query shapes worked read-only against the existing schema.

These facts establish an upgrade **candidate**, not an installed upgrade. The
user-unit configuration references a private `EnvironmentFile`; its contents
must never enter GitHub, CLI arguments, logs or reviewer transcripts.

## Non-disruptive private recovery checkpoint

The standard-library `scripts/vn2_rezon_checkpoint.py` checks an exact **clean
tracked Git source HEAD**, then snapshots live SQLite through its transactional
backup API (not a raw copy of a WAL-active database). It copies the user unit
and explicitly identified private files into a fresh `0700` directory with
`0600` files, stores SHA-256/size custody, checks SQLite integrity and rehearses
a restore into a disposable private directory. Its output only includes an
aggregate PASS/HOLD and source SHA: **no database rows or credentials**.

On VN2, with the source-controlled script available through a separately
verified checkout, the authorized local operator can use:

```sh
install -d -m 700 /home/patrick/.local/state/rezon-tkik-recovery
python3 scripts/vn2_rezon_checkpoint.py create \
  --source-checkout /home/patrick/.local/share/rezon-tkik \
  --expected-head d27da3cab31ae96aff3c65385fc31354dc8aeb8c \
  --database /home/patrick/.local/state/rezon-tkik/episodes.sqlite3 \
  --unit-file /home/patrick/.config/systemd/user/rezon-tkik.service \
  --unit-name rezon-tkik.service \
  --private-file /ABSOLUTE/LOCAL/PATH/TO/REZON_ENV_FILE \
  --checkpoint-dir /home/patrick/.local/state/rezon-tkik-recovery/CHECKPOINT_UNIQUE_ID
python3 scripts/vn2_rezon_checkpoint.py verify \
  --checkpoint-dir /home/patrick/.local/state/rezon-tkik-recovery/CHECKPOINT_UNIQUE_ID
```

Resolve the `EnvironmentFile` path **on VN2 only** by inspecting the existing
unit locally; pass a genuine, non-symlink regular file. The placeholders above
are deliberately non-executable. Never paste private contents or tokens into
the PR. Private EnvironmentFiles must already be owner-only (`0600` or tighter)
and must exactly match both the literal unit directive and the active systemd
user-unit effective binding. The script fails closed on active drop-ins;
the VN2 unit had none at the observation. A later drop-in must be reviewed and
captured separately, not silently ignored. Only run `create` after comparing the actual source revision and state
paths against these observations. Every checkpoint directory must be new.

The checkpoint script never stops systemd, restarts a model, modifies live
SQLite, switches source versions, enrolls a reader, or restores state. A
`PASS` means the **snapshot** is private, checksum-bound and disposable-restore
readable, not that the old service can recover under every operational failure.
The checksum manifest detects accidental drift but is **not** an independently
signed tamper-resistant attestation against an attacker controlling the same user.
On failure, an incomplete 0700 directory may remain; a directory without a
valid manifest is not a checkpoint and must never be offered as rollback input.

## Separate installation / rollback gates

1. Pin and independently review an immutable new Rezon source revision. Stage
   a **separate versioned directory and environment**, without `git pull` in
   the live source. Keep the old checkout untouched and record its HEAD.
2. Verify checkpoint creation, full private configuration custody, isolated
   source tests, disposable canary and source/schema compatibility. Establish
   rollback ownership and outage window. Service-specific unit and private
   env-file restoration must be rehearsed before any cutover.
3. Under separate live-effect authorization, stop only the user gateway and
   confirm writers ceased. Never run old and new releases simultaneously
   against the same writable SQLite file. Retain a **recoverable copy** of
   pre-switch SQLite plus WAL/SHM state until cutover is qualified.
4. Switch versioned source/configuration atomically without modifying the old
   checkout. Restart user gateway only; check health, authenticated readiness,
   fixed-episode challenge/HMAC with real custodian and replay denial. Verify
   model inferer unchanged.
5. On failure, stop the candidate, restore old source/unit/env configuration
   and **restore the checkpoint only through a separately tested data recovery
   procedure** after writers are stopped. Recheck old source HEAD, user-unit
   readiness and state integrity. Do not overwrite the live DB just because a
   portable SQLite backup exists; reconcile WAL and any post-checkpoint writes.

**Current HOLD:** source snapshot utility has not yet been run against VN2's
private files; neither a live service upgrade nor a rollback was exercised.
PORTAL on a different host cannot call `127.0.0.1` on VN2; a separate
authenticated transport qualification remains necessary.
