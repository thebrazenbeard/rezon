# Owner-operated credential enrollment and first live Rezon episode (V1)

**Execution boundary:** These are local, human-operated steps. They are not ChatGPT/Executor tool commands. Previous remote attempts to read or distribute protected Rezon credentials were blocked; **do not retry through another remote tool, paste secrets into ChatGPT, place secrets in Git or logs, weaken SSH verification, or disable gateway authentication**. No operation described here proves host attestation, four physical hosts, or reasoning accuracy.

The running VN2 gateway has distinct worker bearer credentials for `lappy`, `vn1`, `vn2`, and `malaphor`. It is reachable inside the Tailscale tailnet at `https://vn2.tail86ea75.ts.net`; its local listener is `127.0.0.1:18765`. The service configuration is owner-only at `~/.config/rezon-tkik/gateway.env`. There is **one administrative credential**, different from all worker credentials.

## Gate 1 — owner-controlled confidential enrollment

1. On **VN2's physical/local owner session**, open the existing owner-only configuration in a private terminal/editor. Do **not** print it into any ChatGPT-connected terminal response or troubleshooting log.
2. Using an independently approved encrypted password manager or equivalent owner-controlled confidential transfer, make the `lappy` worker credential available **only** to the Lappy owner session, and the `vn1` credential **only** to the VN1 owner session. Keep `vn2` on VN2. The `malaphor` credential is distinct from `lappy` even though both models execute on Lappy: never reuse either identity for the other.
3. Do not persist credentials in scripts, dotfiles, shell profiles, screenshots, issue comments or command lines. Start from an interactive owner shell and enter each credential with hidden input. The commands below use a *process-scoped* environment variable; operating-system and process administrators may still inspect its memory. Clear the variable and exit the shell when finished.
4. **Stop** if the credential/config identity is inconsistent, the Tailscale certificate is not valid, the gateway cannot verify its service schema, or a worker's reported `agent_id` is not its assigned role.

For Lappy and VN1, open a **local PowerShell terminal**, not an Executor-run command. After obtaining **that worker's** credential securely, enter it without command-line echo:

```powershell
$secret = Read-Host "Assigned worker bearer token" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try { $env:REZON_WORKER_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr); $bstr = [IntPtr]::Zero }
Remove-Variable secret -ErrorAction SilentlyContinue
$env:REZON_MODEL_API_KEY = "localhost-model-placeholder"
$py = Join-Path $env:LOCALAPPDATA 'RezonTKIK\worker-venv\Scripts\python.exe'
```

On VN2, in a **local Bash terminal**, enter VN2's own worker credential separately:

```bash
IFS= read -r -s -p "VN2 worker bearer token: " REZON_WORKER_TOKEN
printf '\n'
export REZON_WORKER_TOKEN
export REZON_MODEL_API_KEY=localhost-model-placeholder
```

Never display the value of `REZON_WORKER_TOKEN`. An unset or mismatched token must stop the run; never fall back to an administrator token.

## Gate 2 — authorized administrator creates a single fixed-roster episode

In a separate **VN2 local owner terminal**, manually enter its *admin* bearer credential using hidden input, then create the episode via the existing authenticated loopback API. **This is an owner operation, not a remote ChatGPT tool action.**

```bash
IFS= read -r -s -p "Admin bearer token: " REZON_COLLECTIVE_ADMIN_TOKEN
printf '\n'
export REZON_COLLECTIVE_ADMIN_TOKEN
python3 - <<'PY'
import json, os
from urllib.request import Request, urlopen

data = json.dumps({
    "prompt": "Assess whether training an in-house maintenance technician could reduce unplanned downtime by 20% over 90 days. Propose controls, falsifiers and safety stops; do not invent empirical results.",
    "agents": ["lappy", "vn1", "vn2", "malaphor"],
}).encode("utf-8")
req = Request("http://127.0.0.1:18765/v1/episodes", method="POST",
    data=data, headers={
        "Authorization": "Bearer " + os.environ["REZON_COLLECTIVE_ADMIN_TOKEN"],
        "Content-Type": "application/json",
    })
with urlopen(req, timeout=15) as res:
    assert res.status == 201
    obj = json.load(res)
print("EPISODE_ID=" + obj["episode_id"])  # public opaque identifier, not a credential
PY
unset REZON_COLLECTIVE_ADMIN_TOKEN
```

Do not create additional episodes on command timeout without inspecting durable server state. Preserve the exact returned `collective-<32 hex>` episode ID.

## Gate 3 — verify identity, then submit one first answer per worker

After the administrator supplies the nonsecret episode ID, the operator sets it as `$episode` in PowerShell or `EPISODE` in Bash. Use the same ID for all four roles.

**Lappy / Qwen** (Lappy's credential only):

```powershell
$episode = "collective-REPLACE_WITH_THE_CREATED_ID"
& $py -m rezon.worker_client status --gateway https://vn2.tail86ea75.ts.net --episode $episode
& $py -m rezon.worker_client answer --gateway https://vn2.tail86ea75.ts.net --episode $episode --model qwen3:4b-instruct --max-tokens 240 --timeout 120
```

**VN1 / Gemma** (VN1's credential only):

```powershell
$episode = "collective-REPLACE_WITH_THE_CREATED_ID"
& $py -m rezon.worker_client status --gateway https://vn2.tail86ea75.ts.net --episode $episode
& $py -m rezon.worker_client answer --gateway https://vn2.tail86ea75.ts.net --episode $episode --model gemma3:1b --max-tokens 240 --timeout 120
```

**VN2 / Granite** (VN2's credential only):

```bash
EPISODE="collective-REPLACE_WITH_THE_CREATED_ID"
PYTHON="$HOME/.local/share/rezon-venv/bin/python"
MODEL="/home/patrick/vera-review-sandbox/models/ibm-granite_granite-3.3-2b-instruct-Q4_K_M.gguf"
"$PYTHON" -m rezon.worker_client status --gateway https://vn2.tail86ea75.ts.net --episode "$EPISODE"
"$PYTHON" -m rezon.worker_client answer --gateway https://vn2.tail86ea75.ts.net --episode "$EPISODE" --model "$MODEL" --model-url http://127.0.0.1:11435/v1 --max-tokens 240 --timeout 120
```

**Lappy / Ministral** (in a separate owner shell, clear the previous `lappy` token first; enter `malaphor` token via the same hidden-entry procedure):

```powershell
$episode = "collective-REPLACE_WITH_THE_CREATED_ID"
& $py -m rezon.worker_client status --gateway https://vn2.tail86ea75.ts.net --episode $episode
& $py -m rezon.worker_client answer --gateway https://vn2.tail86ea75.ts.net --episode $episode --model ministral-3:14b --max-tokens 240 --timeout 120
```

A receipt with `gateway_status=ACCEPTED_UNATTESTED` establishes acceptance under the bearer-bound *claimed* role, not proof of which physical host ran it. If exit code is **3 / OUTCOME_UNKNOWN**, inspect server episode state before doing anything again; **never blindly retry the POST**. A failed model invocation must not be recorded as an accepted contribution.

## Gate 4 — peer-review barrier and acceptance receipts

When **all four first answers** have been accepted, each worker uses its own credential again and runs the analogous explicit `review` command:

```powershell
& $py -m rezon.worker_client review --gateway https://vn2.tail86ea75.ts.net --episode $episode --model gemma3:1b --max-tokens 240 --timeout 120
```

Replace the example model with that worker's model from Gate 3. VN2 uses the additional `--model-url http://127.0.0.1:11435/v1`. The server withholds the peer round until initial answers are complete. Each worker must target exactly the **three other** answer IDs. Keep client receipt IDs, source-head identifiers, model claims and outcome-unknown cases distinct from host attestation.

For the VN2 review step, the exact local invocation is:

```bash
"$PYTHON" -m rezon.worker_client review --gateway https://vn2.tail86ea75.ts.net --episode "$EPISODE" --model "$MODEL" --model-url http://127.0.0.1:11435/v1 --max-tokens 240 --timeout 120
```

The bounded `--max-tokens` argument controls the **generation budget**, not gateway security. If a model times out, retain the explicit failed/outcome-unknown status and inspect the durable episode before retrying.

The **local VN2 owner** verifies the durable store separately after the round (no bearer material required):

```bash
cd "$HOME/.local/share/rezon-tkik"
"$HOME/.local/share/rezon-venv/bin/python" - <<'PY'
from pathlib import Path
from rezon.collective import CollectiveStore
from dataclasses import asdict

# Replace only the opaque episode ID; this is a local owner read.
episode_id = "collective-REPLACE_WITH_THE_CREATED_ID"
store = CollectiveStore(Path.home() / ".local/state/rezon-tkik/episodes.sqlite3")
snapshot = store.snapshot(episode_id)
print({
    "episode_id": episode_id,
    "agent_count": len(snapshot.agents),
    "answer_count": len(snapshot.answers),
    "review_count": len(snapshot.reviews),
    "initial_round_complete": snapshot.complete,
})
assert len(snapshot.agents) == 4
assert len(snapshot.answers) == 4
assert len(snapshot.reviews) == 4
assert snapshot.complete
PY
```

If the store has fewer than 4 accepted answers or reviews, the live hearing is incomplete. Never promote a rehearsal file as an authenticated contribution. Additional T'Kal hearing challenge/defense/determination steps and a fourth *physical* host are separate qualifications.

## Cleanup

When finished, from each owner PowerShell terminal: `Remove-Item Env:\REZON_WORKER_TOKEN,Env:\REZON_MODEL_API_KEY -ErrorAction SilentlyContinue`. From VN2 Bash: `unset REZON_WORKER_TOKEN REZON_MODEL_API_KEY`. Close those shells. Do not expose or transmit the private environment variables while reporting results. Preserve the real server database and audit records.
