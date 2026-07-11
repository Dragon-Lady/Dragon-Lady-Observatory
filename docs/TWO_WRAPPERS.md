# Two wrappers (Cosmic / Oracle vs Chuck)

## What’s going on

| Wrapper | How you start it | Port | Code |
|---|---|---|---|
| **Oracle / Cosmic** | whatever Cosmic Terminal runs (`observatory` cheat) | usually **4321** | often old → boots **M42 / Orion** |
| **Chuck** | `./scripts/observatory` in this repo | **4331** | `cursor/console-pins-cleanup-27c8` → **pinfix 8** |

They are **different processes**. Fixing one does not change the other until Cosmic points at this script.

## Use Chuck’s wrapper tonight

In Cosmic Terminal (or any terminal):

```bash
cd /path/to/Dragon-Lady-Observatory
git fetch origin
git checkout cursor/console-pins-cleanup-27c8
git pull
chmod +x scripts/observatory
./scripts/observatory
```

Leave it running. Open:

**http://127.0.0.1:4331/observatory**

(not 4321 — that’s still Oracle’s)

Bottom-left must show **`· pinfix 8`**.

## If “cannot be reached”

1. Look at the terminal where you ran `./scripts/observatory` — did it print `Starting Astro` or exit with `✗`?
2. Log file: `/tmp/dlo-observatory-chuck.log` (or `$TMPDIR/dlo-observatory-chuck.log`)
3. Confirm something is listening:
   ```bash
   lsof -iTCP:4331 -sTCP:LISTEN
   ```
4. Try:
   ```bash
   DLO_HOST=0.0.0.0 DLO_PORT=4331 ./scripts/observatory
   ```
   then open http://127.0.0.1:4331/observatory

## Point Cosmic at Chuck later (retire Orion rent)

```bash
cd /path/to/Dragon-Lady-Observatory
mkdir -p ~/bin
ln -sf "$(pwd)/scripts/observatory" ~/bin/observatory
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc   # or ~/.zshrc
hash -r
type -a observatory   # should show ~/bin/observatory → scripts/observatory
```

Then Cosmic’s `observatory` command is Chuck’s. Until then: use **:4331** for the fixed Atlas.
