# Rezon owner-local credential vault enrollment (V1)

This is an **operator action in a local, private terminal**. ChatGPT-connected remote execution, issue comments, SSH command arguments and logs are not approved credential-transfer paths. Never expose a production bearer value to them.

Rezon worker credentials remain distinct for `lappy`, `vn1`, `vn2` and `malaphor`. A successful client receipt proves the bearer-bound role claimed to the gateway, **not** cryptographic attestation that a particular host or model executed.

## Prerequisites

The production VN2 tailnet gateway runs at `https://vn2.tail86ea75.ts.net`. The *administrator* creates an episode from VN2's own local private session as documented in [TKIK_OWNER_ENROLLMENT_V1.md](TKIK_OWNER_ENROLLMENT_V1.md). Keep its admin bearer on VN2 only. Copy the resulting opaque `collective-<32 lowercase hexadecimal>` episode identifier; **this identifier is not secret**.

The owner must securely obtain each machine's assigned worker credential outside ChatGPT-connected terminals: `lappy` and `malaphor` separately on Lappy, `vn1` on VN1, and `vn2` on VN2. Do not use another worker's or the admin bearer as a substitute.

The enrollment client uses **Windows Credential Manager** (per-user Generic Credentials, target `RezonTKIK/worker/<role>`) or the local **Linux Secret Service** (via `secret-tool`, with attributes `service=rezon-tkik` and `role=<role>`). The local vault must be available/unlocked. If the platform vault cannot be accessed, the operation fails; there is no plaintext-token-file fallback. On Linux it uses `secret-tool` from `libsecret-tools` when available; otherwise it uses the `secretstorage` Python client against the **same** unlocked Secret Service. To install the pinned user-level backend without sudo from a Rezon checkout, run:

```bash
"$HOME/.local/share/rezon-venv/bin/python" -m pip install 'secretstorage==3.5.0'
```

The source binding for this optional dependency is declared as `.[linux-keyring]` in `pyproject.toml`. VN2 can access the already-running GNOME keyring; it does not need a second keyring or any privileged package installation. Neither backend writes a plaintext worker token file.

The Python fallback checks matching role metadata in the **entire** Secret Service before storing in the default collection, then rechecks that exactly one unlocked item remains and that it is the item just stored. A duplicate in another collection, locked match, or race makes enrollment fail closed rather than report a false success. This check does not retrieve other stored secrets or delete entries in another collection. A write interrupted by a concurrent conflicting item may leave a partially enrolled default-collection item: resolve the conflict using your own vault UI before retrying, not automatic cleanup. Successful metadata checks are not proof of physical-host identity or of the later gateway request.

Both Linux backends check the stored token's bytes before reporting enrollment success. With the `secret-tool` CLI, a subsequent `lookup` must return the exact token just stored; a failed/mismatched lookup fails closed. **Unlike the Python backend, the CLI's one-item lookup does not prove global uniqueness across Secret Service collections.** If your session has conflicting items for the same role, resolve them locally through the vault UI before relying on a worker. Even an exact immediate readback cannot guarantee a credential is not later replaced.

## Enroll in an owner-controlled terminal

On **Lappy and VN1**, in a **local PowerShell terminal**:

```powershell
$env:PYTHONPATH = Join-Path $env:LOCALAPPDATA 'RezonTKIK\worker-source\src'
$gateway = 'https://vn2.tail86ea75.ts.net'
$episode = 'collective-REPLACE_WITH_ACTUAL_EPISODE_ID'
python -m rezon.owner_worker enroll --role lappy --gateway $gateway --episode $episode
```

Use `--role vn1` on VN1, and separately `--role malaphor` on Lappy. Each invocation prompts for only that role's credential with hidden input, verifies its binding against the production gateway, and stores it in the **local user's operating-system vault**. If verification fails, nothing is saved.

On **VN2**, in a **local private terminal** with an unlocked Linux Secret Service:

```bash
cd "$HOME/.local/share/rezon-tkik"
export PYTHONPATH="$PWD/src"
gateway=https://vn2.tail86ea75.ts.net
episode=collective-REPLACE_WITH_ACTUAL_EPISODE_ID
"$HOME/.local/share/rezon-venv/bin/python" -m rezon.owner_worker enroll \
    --role vn2 --gateway "$gateway" --episode "$episode"
```

If VN2 has no Secret Service, the owner must configure one or use the existing **process-scoped hidden-entry** steps in [TKIK_OWNER_ENROLLMENT_V1.md](TKIK_OWNER_ENROLLMENT_V1.md); do not put its bearer in a file or CLI argument.

## Execute one explicit round

After enrollment, workers can retrieve *their own* local credential from the OS vault without requesting it again. For Windows examples (assuming `$episode` and `$gateway` from above):

```powershell
$env:REZON_MODEL_API_KEY = 'localhost-model-placeholder'
python -m rezon.owner_worker status --role lappy --gateway $gateway --episode $episode
python -m rezon.owner_worker answer --role lappy --gateway $gateway --episode $episode --model 'qwen3:4b-instruct' --max-tokens 240 --timeout 120
```

On VN1, use `--role vn1 --model 'gemma3:1b'`. On Lappy, run another distinct invocation with `--role malaphor --model 'ministral-3:14b'` (no credential switching or shared token). On VN2, use `--role vn2 --model <local Granite model path> --model-url http://127.0.0.1:11435/v1`, with the local process environment containing `REZON_MODEL_API_KEY=localhost-model-placeholder`.

Once all four accepted answers appear, repeat each worker command with `review` instead of `answer`. The client validates the correct role before attempting model inference or submission and never retries an unknown POST outcome. A nonzero exit or `OUTCOME_UNKNOWN` requires a server-state read before any manual retry.

Readback from VN2's owner session should show the **production** episode with four distinct answer identities, four reviews targeting only other answers, and the expected participant roster. Additional T'Kal challenges, defenses and decisions require their own role-authorized protocol operations.

## Safety and boundaries

- **Do not enroll from automated remote terminals, CI jobs or ChatGPT-connected tools**. Enrollment is deliberately an explicit local owner action.
- **Never provide tokens as command-line arguments**, paste them in a conversation, or write them into source, environment profiles or plain files.
- **Do not use the admin credential for a worker identity**. Any mismatched identity fails before storage or model inference.
- The vault stores user-scoped credentials, not physical-host attestation. On Lappy, `lappy` and `malaphor` are distinct vault entries for two models on one machine.
- If the local OS user session is compromised, that user may retrieve its enrolled bearer. Use OS account access controls, credential revocation and normal host hardening.
