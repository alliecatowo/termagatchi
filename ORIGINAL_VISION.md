
# Termagatchi — Textual + LiteLLM + Instructor (provider-agnostic)

## 0) Stack

* **Python 3.11+**
* **Textual** (TUI), **Rich** (colors/logging)
* **Typer** (CLI entrypoint)
* **LiteLLM** (single client for OpenAI, Anthropic/Claude, Google/Gemini, Azure, Mistral, Together, Fireworks, **Ollama** via OpenAI-compat, etc.)
* **Instructor** + **Pydantic** (structured outputs)
* **YAML** for items; **JSON** for save
* **Poetry** + `pipx`; optional PyInstaller for single binary

Install:

```bash
poetry add textual rich typer pydantic tomli tomli-w ruamel.yaml
poetry add litellm instructor openai  # openai is the client interface Instructor uses
```

> LiteLLM will route to whatever you configure; no custom “adapters”.

---

## 1) Environment & config

Support all providers via env/`config.toml`. Examples:

```toml
# ~/.termagatchi/config.toml
[lm]
provider = "google"           # "anthropic" | "openai" | "ollama" | "azure" | ...
model    = "gemini-1.5-flash" # "claude-3-haiku" | "gpt-4o-mini" | "llama3.1:8b" ...
timeout_s = 4
max_retries = 2

[theme]
mode = "auto"
```

Set keys as needed (only for the provider you pick):

```
export GOOGLE_API_KEY=...
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
# Ollama (OpenAI-compatible) example:
export OPENAI_API_BASE="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama"   # any non-empty string
```

> With LiteLLM you can also run a local **proxy** if you want, but not required.

---

## 2) Structured output contract (one model for everything)

We always ask the model to return **this Pydantic shape**:

```python
# ai/schema.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal

ACTIONS = (
    "SMILE","LAUGH","BLUSH","HEART","WAVE","WIGGLE","JUMP",
    "EAT","CLEAN","PLAY","NAP","SLEEPING","SAD","CRY","SICK",
    "HEAL","CONFUSED","THINK","SURPRISED","THANKS"
)

class PetReply(BaseModel):
    say: str = Field(..., description="Short, cute pet-like sentence (≤12 words).")
    action: Literal[ACTIONS]

    @field_validator("say")
    @classmethod
    def limit_words(cls, v: str) -> str:
        words = v.strip().split()
        return " ".join(words[:12]) or "hi"
```

---

## 3) LLM call (one function, all providers)

```python
# ai/client.py
import os, json
from instructor import from_openai
from openai import OpenAI
from pydantic import BaseModel
from .schema import PetReply, ACTIONS

# Instructor wraps the OpenAI-compatible interface; LiteLLM makes that interface universal
# by honoring OPENAI_API_BASE / key and env vars for selected provider.
# For Gemini/Claude/OpenAI/Azure: set normal provider keys
# For Ollama: set OPENAI_API_BASE to ollama's /v1 endpoint.

client = from_openai(OpenAI(), mode="json_schema")  # structured outputs

SYSTEM = (
    "You are a tiny terminal pet named Termagatchi. "
    "Reply with a very short, cute sentence (≤ 12 words). "
    f"Also choose exactly ONE action from ACTIONS and RETURN JSON ONLY.\n"
    f"ACTIONS={list(ACTIONS)}"
)

def make_context(stats: dict, events: list[str], last_user: str, tod: str) -> str:
    return json.dumps({
        "stats": stats,
        "recent_events": events[-6:],  # keep small
        "last_user": last_user,
        "time_of_day": tod
    }, ensure_ascii=False)

def get_pet_reply(stats: dict, events: list[str], last_user: str, tod: str, model: str, timeout: int = 4) -> PetReply:
    context = make_context(stats, events, last_user, tod)
    # Instructor handles schema coercion; if a provider supports native JSON it uses it, otherwise it validates/repairs.
    return client.chat.completions.create(
        model=model,
        temperature=0.7,
        max_tokens=64,
        messages=[
            {"role":"system", "content": SYSTEM},
            {"role":"user", "content": f"[CONTEXT]{context}[/CONTEXT]\nReturn only the JSON object."}
        ],
        timeout=timeout
    ).parse(PetReply)  # <- parsed & validated
```

* **Provider selection**: You pass `model` from config (`gemini-1.5-flash`, `claude-3-haiku`, `gpt-4o-mini`, `llama3.1:8b` via Ollama, etc.).
* **No adapters**: Switching vendors is just changing env vars + the `model` string.

**Retry policy**: wrap `get_pet_reply` in a tiny retry (2 attempts, exponential backoff). If it still fails, call a deterministic fallback.

---

## 4) Textual layout

```
┌ Termagatchi ─────────────────────────────────────────────────────┐
│ [SpriteView]              │ [StatusPanel] (5 bars + health dot)  │
├───────────────────────────┼───────────────────────────────────────┤
│ [ToastFeed] (right column; newest on top; auto-expire)           │
├──────────────────────────────────────────────────────────────────┤
│ [ChatLog] (scrolling; last 8–12 lines visible)                    │
├──────────────────────────────────────────────────────────────────┤
│ [QuickRef / Inventory]        │  [ > InputLine ]                  │
└──────────────────────────────────────────────────────────────────┘
```

**Widgets**

* `SpriteView`: plays action animations (1–3 frames @ 8–10 FPS for ~700ms).
* `StatusPanel`: 5 compact bars (`hunger`, `hygiene`, `mood`, `energy`, `affection`) + small `health` indicator; hover/focus reveals exact numbers.
* `ToastFeed`: up to 5 messages, fade out after 8–12s.
* `ChatLog`: `you:` / `tama:` alternating, max 200 entries in memory.
* `QuickRef`: slash commands + top inventory items.
* `InputLine`: single-line prompt; `/` commands or free text.

**Theme**: dark base, muted accents, accessible contrast; TCSS file for colors/borders.

---

## 5) Game logic

**Stats (0–100)**: `hunger, hygiene, mood, energy, affection, health`, plus `sleeping: bool`.

**Tick (every 60s, with catch-up on resume):**

* `hunger −1`, `hygiene −0.5`; if awake: `energy −0.5`; if sleeping: `energy +1`.
* If `hunger<40 or hygiene<40`: `mood −0.2`.
* If any of `{hunger<20, hygiene<20, energy<10}`: 5% *SICK* chance (`health −3`).
* Clamp 0–100; append `DECAY` event.

**Commands**

```
/feed [item?]  /clean [item?]  /play [item?]
/sleep [on|off]  /pet  /heal  /vet  /status  /save  /quit
```

* Items & effects come from `data/items.yaml`; each has `cooldown_s`.
* Actions map to enum animations (EAT, CLEAN, PLAY, NAP/SLEEPING, HEART, etc.).

**Persistence**

* `~/.termagatchi/save.json` + autosave every 30s and on exit.
* Backup if corrupted (`save.json.bak`).

---

## 6) Textual event flow

* `App.on_mount`: load save, start tick timer (60s) + animation timer.
* `InputLine.on_submit`:

  * If starts with `/` → parse command → apply effects → emit animation + toasts → log chat (optional pet line from deterministic responder).
  * Else (free text) → call `get_pet_reply(...)` with `(stats, events, last_user, time_of_day)` + `model` from config → append to ChatLog → play `action` animation → update bars → maybe toast.
* `on_tick`: apply decay; update UI; post threshold toasts.
* Robust try/except; on LLM errors show toast *“LLM temporarily unavailable; using default reply.”* and use deterministic fallback.

---

## 7) Deterministic fallback (one file, tiny)

Buckets keyed by need state; replies are already short/cute:

```python
# ai/fallback.py
from random import choice
def fallback_reply(stats) -> tuple[str,str]:
    if stats["hunger"] < 20:   return choice(["kibble please","tummy empty"]), "EAT"
    if stats["energy"] < 15:   return choice(["sleep soon","nap now"]), "NAP"
    if stats["hygiene"]< 25:   return choice(["wash please","soap time"]), "CLEAN"
    return choice(["hi!","wiggle!","happy now"]), "SMILE"
```

---

## 8) Files & layout

```
termagatchi/
  ├─ terminal/
  │  ├─ app.py               # Textual App + timers
  │  ├─ widgets/             # sprite.py, status.py, toasts.py, chat.py, input.py
  │  ├─ engine/
  │  │  ├─ state.py          # Stats, decay, save/load
  │  │  ├─ items.py          # YAML loader, cooldowns
  │  │  └─ actions.py        # enum + animation map
  │  ├─ ai/
  │  │  ├─ schema.py         # PetReply (Pydantic)
  │  │  ├─ client.py         # LiteLLM+Instructor call (get_pet_reply)
  │  │  └─ fallback.py
  │  ├─ assets/actions/...   # ASCII frames per action
  │  ├─ data/items.yaml
  │  ├─ themes/termagatchi.tcss
  │  └─ storage/save.json
  ├─ cli.py                  # Typer: run/config/reset/demo
  ├─ pyproject.toml
  ├─ README.md
  └─ LICENSE
```

---

## 9) CLI

```
termagatchi run
termagatchi config edit
termagatchi reset
termagatchi demo
```

* `run` reads `~/.termagatchi/config.toml`; if missing, starts deterministic mode and shows a toast guiding user to set `provider/model` and an API key.

---

## 10) Acceptance checklist

1. Launch shows all panels; deterministic mode works without any keys.
2. `/feed`, `/clean`, `/play`, `/sleep` mutate stats and animate.
3. Idle 5 minutes → visible decay and threshold toasts.
4. With **any** configured provider (Gemini, Claude, OpenAI, **Ollama**) `get_pet_reply` returns a validated `PetReply`; chat/animation update accordingly.
5. API down → deterministic fallback + warning toast; no crash.
6. Save/resume restores state; autosave works.

---

## 11) Quick provider notes

* **Gemini**: set `GOOGLE_API_KEY` + `lm.provider="google"`, `model="gemini-1.5-flash"`.
* **Claude**: `ANTHROPIC_API_KEY`, `provider="anthropic"`, `model="claude-3-haiku-20240307"` (or newer).
* **OpenAI/Azure**: `OPENAI_API_KEY` or Azure envs; set `provider="openai"`/`"azure"`.
* **Ollama (local)**: `ollama serve`; `OPENAI_API_BASE=http://127.0.0.1:11434/v1`; `OPENAI_API_KEY=ollama`; `model="llama3.1:8b"` (or whatever tag).

All of these flow through the **same** `get_pet_reply` call.

---

## 12) Nice-to-haves (after MVP)

* Grammar/JSON mode where supported (Claude JSON, OpenAI response_format, Gemini JSON), auto-enabled by Instructor when available.
* Command palette (`Ctrl-K`) with fuzzy search over slash commands and items.
* Screenshot/GIF demo mode (`termagatchi demo`) that scripts a cute session.

heck yes—this is a killer, fast-to-market idea. here’s a tight, end-to-end “Bible” you can hand to yourself (or another dev) and ship an MVP this week. it’s opinionated, scoped, and production-minded while staying tiny and fun.

---

# terminal-tama — MVP product & tech spec

## 0) one-liner & promise

**A cozy terminal Tamagotchi** with a tiny embedded local model. You type short messages or slash-commands; your pet replies using a *strict tiny vocabulary* and performs a *structured action* (emoji/animation). Stats (hunger, hygiene, mood, energy, affection) change over time and with player actions. MVP is fully offline, single-user, and cross-platform (mac/linux/windows).

---

## 1) hard scope for week-one MVP (non-negotiables)

* **Local/offline** only. No network calls.
* **TUI first** (single process). No daemon, no sockets, no plug-ins.
* **Strict vocab**: 1024 words hard cap (MVP ships with ~256 to start; upgrade to 1024 in v0.2).
* **Action enum**: pet always returns one of finite actions (e.g., `SMILE`, `JUMP`, `HEART`, `SAD`, `NAP`, `EAT`, `CLEAN`, `PLAY`, `BLUSH`, `WIGGLE`, `WAVE`).
* **Slash commands** for deterministic care loops (`/feed`, `/clean`, `/play`, `/sleep`, `/vet`, `/heal`, `/pet`, `/status`).
* **Free-text chat** allowed, but routed through the constrained LM wrapper (or rule-based fallback).
* **Persistence**: single JSON/SQLite file in `~/.terminal_tama/`.
* **ASCII animations**: 1–3 frames per action, 8–12px monospace “sprite” feel.
* **Time system**: passive stat decay with wall-clock and tick-loop.
* **No English “understanding” claims**: it’s a vibe pet, not a serious assistant.
* **Packaging**: `pipx install terminal-tama` / single binary via PyInstaller in Releases.

**Out-of-scope (this week):** VS Code extension, MCP/Calendar/Git/Gmail integrations, cloud sync, mobile/native builds, long-context language understanding, marketplace, achievements/badges, theming engine beyond light/dark.

---

## 2) product pillars

1. **Delightfully Alive in a Terminal**
   Low-latency (100–200ms), tiny animations, quick haptics (key feedback), soft sound opt-in (beeps).

2. **Constrained Personality**
   Small vocabulary + action enum + stat engine ⇒ believable, non-annoying loop.

3. **Deterministic Care Loop**
   You can *always* keep it happy via clear commands. Chat adds flavor, not required.

4. **Upgrade Path**
   The engine is already shaped for later native/web/VSCode ports and MCP connectors.

---

## 3) UX & TUI layout

```
┌──────────────── terminal-tama ────────────────┐
│  ( ^ᴥ^ )  ♥♥                                 │  ← pet viewport (ASCII frames)
│  mood: ☀︎ happy   hunger: ▮▮▮▯▯  energy: ▮▮▮▮▯│  stats with bars & decay hints
│  hygiene: ▮▮▮▮▮  affection: ▮▮▮▮▯             │
│                                               │
│  actions: /feed /clean /play /sleep /pet      │
│           /status /heal /vet /save /quit      │
│                                               │
│  chat:   you:  let's play!                    │
│          tama: "play now!"  [PLAY]            │  ← vocab text + structured action tag
│                                               │
│  >                                           _│  ← input; supports slash & free text
└───────────────────────────────────────────────┘
```

* **Hotkeys**: `f` feed, `c` clean, `p` play, `s` sleep, `v` vet, `h` heal, `.` pause tick.
* **Status popover** on `/status`: shows exact numbers, recent events, next decay ETA.
* **Autosave** every 30s and on quit.

---

## 4) core game design

### 4.1 Stats (0–100)

* `hunger`, `hygiene`, `mood`, `energy`, `affection`, `health`
* Decay: every **real-time minute** (tick), apply:

  * hunger −1, hygiene −0.5, energy −0.5 (awake), mood −0.2 (if hunger < 40 or hygiene < 40)
* Sleep state reduces decay & slowly restores energy (+1 per tick while sleeping).
* Boundaries clamp 0–100. If `health` < 20, random `SICK` event.

### 4.2 Items & actions (data-driven)

MVP ships ~40–60 entries; easy to add. Example YAML:

```yaml
# data/items.yaml
- id: kibble_small
  type: food
  label: "small kibble"
  effects: { hunger:+10, mood:+2 }
  cooldown_s: 60

- id: soap_bar
  type: clean
  label: "soap bar"
  effects: { hygiene:+20, mood:+1 }
  cooldown_s: 120

- id: ball
  type: play
  label: "bouncy ball"
  effects: { mood:+10, energy:-5, affection:+3 }
  cooldown_s: 90
```

**Slash mapping** (defaults; items are optional):

* `/feed [item?]` (default: `kibble_small`)
* `/clean [item?]` (default: `soap_bar`)
* `/play [item?]` (default: `ball`)
* `/sleep [on|off]` (toggles; off if energy > 80 or on user cmd)
* `/pet` (affection + small mood bump)
* `/heal` (uses `meds_basic` if `health<50`)
* `/vet` (big heal; cooldown 12h; minor mood penalty)
* `/status`, `/save`, `/quit`

### 4.3 Action enum

```
SMILE, LAUGH, BLUSH, HEART, WAVE, WIGGLE, JUMP,
EAT, CLEAN, PLAY, NAP, SLEEPING, SAD, CRY, SICK, HEAL,
CONFUSED, THINK, SURPRISED, THANKS
```

Each maps to 1–3 ASCII frames stored under `assets/actions/<ACTION>/*.txt`.

---

## 5) the language constraint

### 5.1 Vocab file

`data/vocab.txt` (≤256 words for v0.1; expandable to 1024). Buckets:

* **Core**: yes, no, okay, now, later, please, thank you, sorry, hello, bye
* **Emotion**: happy, sad, sleepy, hungry, clean, messy, love, friend, play, fun
* **Actions**: eat, wash, nap, jump, wiggle, wave, cuddle, vet, heal
* **Time**: soon, later, now, minute, hour
* **Quantifiers**: little, more, much, full, empty
* **Reactions**: yay, oops, hm, hmm
* **Connectors**: and, but, if, or, then
* **Pronouns**: I, you, me, we
* **Numbers**: zero…nine

> *Rule:* Generated text must be token-filtered to vocab; OOV tokens replaced by nearest allowed synonym or dropped.

### 5.2 Model plan (MVP)

* **Default:** *No-LLM deterministic mode* (fast, zero deps)

  * Template library + small finite state machine (FSM) choose from 3–7 canned strings per situation; light randomness with seeded PRNG.
* **Opt-in “Tiny LM” mode** (local)

  * 1–2B distilled model via gguf (e.g., *any* tiny instruct with permissive license you bundle/point to).
  * **Post-filter:** regex/token map -> vocab; then length cut (≤ 12 words).
  * **Classifier head emulation:** choose `action_enum` with a small logistic layer trained offline OR simply use a rule-map (first week).

> Ship both. Deterministic is the baseline; the LM is a “sparkle” toggle.

### 5.3 Prompt contract (LM mode)

**System prompt (fixed)**

```
You are a tiny virtual pet in a terminal. You must ONLY speak using words from the allowed vocabulary list.
Keep replies short (max 12 words), kind, and pet-like.
Also decide exactly ONE action from ACTIONS.

Return JSON:
{"say":"<string using allowed vocab only>", "action":"<ONE_OF_ACTIONS>"}
ACTIONS = [SMILE, LAUGH, BLUSH, HEART, WAVE, WIGGLE, JUMP, EAT, CLEAN, PLAY, NAP, SLEEPING, SAD, CRY, SICK, HEAL, CONFUSED, THINK, SURPRISED, THANKS]
```

**Context fed to model**

```json
{
  "stats": {"hunger": 34, "hygiene": 60, "mood": 72, "energy": 55, "affection": 40, "health": 88, "sleeping": false},
  "recent_events": ["FED:kibble_small:+10", "PLAY:ball:+10", "DECAY:hunger:-1"],
  "last_user": "let's play!",
  "time_of_day": "afternoon"
}
```

**Guardrail post-processor**

* Validate JSON; if fail, reformat; if OOV words exist, replace or drop; if empty, fallback to deterministic template.
* Enforce `say` non-empty and one valid `action`.

---

## 6) architecture

**Language:** Python 3.11+
**CLI/TUI:** `textual` (or `rich` + minimal input loop)
**CLI parser:** `typer`
**Config & data:** `pydantic` models
**Persistence:** tiny `SQLite` (via `sqlite3` or `sqlmodel`) or JSON file (start with JSON to ship faster)
**Packaging:** `poetry` + `pipx`; GitHub Actions to build wheels & onefile binaries

```
terminal-tama/
  ├─ terminal_tama/
  │  ├─ __init__.py
  │  ├─ app.py                 # TUI main loop
  │  ├─ cli.py                 # `tama` entrypoint (Typer)
  │  ├─ engine/
  │  │  ├─ state.py            # stats, decay, events, save/load
  │  │  ├─ fsm.py              # care loops, transitions
  │  │  ├─ actions.py          # enum + mapping to animations & effects
  │  │  └─ items.py            # load YAML items; apply effects
  │  ├─ ai/
  │  │  ├─ responder.py        # interface: deterministic | tiny_lm
  │  │  ├─ deterministic.py    # template generator
  │  │  └─ tiny_lm.py          # optional llama-cpp/ctransformers wrapper
  │  ├─ ui/
  │  │  ├─ view.py             # panels, bars, input
  │  │  └─ animations.py       # ASCII frames, tween helpers
  │  ├─ data/
  │  │  ├─ items.yaml
  │  │  ├─ vocab.txt
  │  │  └─ presets.json        # starter pet templates
  │  ├─ assets/
  │  │  └─ actions/SMILE/*.txt ...
  │  └─ storage/
  │     └─ save.json
  ├─ tests/
  ├─ pyproject.toml
  ├─ README.md
  ├─ LICENSE
  └─ CONTRIBUTING.md
```

---

## 7) data model (pydantic)

```python
class Stats(BaseModel):
    hunger: int = 70
    hygiene: int = 70
    mood: int = 70
    energy: int = 70
    affection: int = 50
    health: int = 100
    sleeping: bool = False

class Event(BaseModel):
    ts: float
    kind: Literal["DECAY","FEED","CLEAN","PLAY","SLEEP","WAKE","HEAL","VET","CHAT","SYSTEM"]
    meta: dict = {}

class PetSave(BaseModel):
    version: str = "0.1.0"
    created_at: float
    updated_at: float
    stats: Stats
    inventory: dict[str,int] = {}
    events: list[Event] = []
    options: dict = {"lm_mode": False, "theme":"auto"}
```

---

## 8) engine rules (pseudo)

* **Tick loop** every 60s:

  * If sleeping: `energy += 1`, `mood += 0.1`; else `energy -= 0.5`.
  * `hunger -= 1`, `hygiene -= 0.5` (min 0 max 100).
  * If `hunger<40` or `hygiene<40`: `mood -= 0.2`.
  * If `hunger<20` or `hygiene<20` or `energy<10`: chance 5% `SICK` (health −3).
* **Actions** apply item effects instantly; enforce cooldown; log event.
* **Sleep** toggles; cannot `PLAY` during `sleeping==True`.

---

## 9) deterministic responder (no-LLM)

**Situation → template bucket:**

* If user uses `/play`: responses from `["play now!", "yay play!", "throw ball?"]`
* If hunger < 20: overlay urgent set `["hungry… please…", "kibble now, please"]`
* If user text contains “love”: `["love you", "friend ♥"]`
* If energy < 10: `["sleep now", "nap time"]`
* Else neutral: `["hi!", "wiggle!", "happy now"]`

Each template is *already vocab-constrained*. Random pick with seed from (time + last_event) to feel varied but reproducible.

Return:

```json
{"say":"play now!","action":"PLAY"}
```

---

## 10) LM wrapper (optional)

* `tiny_lm.py` exposes `generate(context)->dict`
* Uses local backend (e.g., `llama_cpp_python` or `ctransformers`) with `n_ctx=256`, `max_tokens=30`, `temperature=0.7`, `top_p=0.8`.
* Post-process: JSON coercion → vocab filter → length cap → action validation → fallback.

---

## 11) ASCII animations (example)

* `SMILE`:

  * frame1: `( ^ᴥ^ )`
  * frame2: `( ^ᴥ^ )  ♥`
* `JUMP`:

  * frame1: `  ( ^ᴥ^ )`
  * frame2: ` (  ^ᴥ^  )`
* `SAD`:

  * frame1: `( ;ᴥ; )`
  * frame2: `( ;ᴥ; ) …`

Render at 6–10 FPS for 0.5–1.0s per action.

---

## 12) CLI & configuration

* Install: `pipx install terminal-tama`
* Run: `tama`
* Flags:

  * `--lm` toggles LM mode
  * `--save <path>` use alt save
  * `--theme light|dark|auto`
* `~/.terminal_tama/config.toml` overrides flags.

---

## 13) testing

* **Unit**: stat decay, action effects, cooldowns, JSON schema for responder.
* **Golden tests**: deterministic responder snapshots per situation.
* **Smoke**: run TUI for 120s with scripted inputs; assert no exceptions.

---

## 14) repo structure & selling access

* **License**: choose a *source-available, non-transfer* license that allows selling repo access. Options:

  * **BSL 1.1** (Business Source License) with a date-based conversion, or
  * **Prosperity Public License** (non-commercial; sell commercial grants separately).
* **Monetization (this week)**:

  * Private GitHub repo + **GitHub Sponsors** or your Nuxt site’s “buy to get access” hook.
  * Tier $9 early access (binary + repo), $19 supporter (includes LM mode assets), $39 founder (priority feature vote + name in credits).
* **Releases**: tag `v0.1.0` with macOS/Linux binaries; Windows optional if time.

---

## 15) README skeleton (drop-in)

**Title:** terminal-tama — a tiny terminal pet
**Badges:** PyPI, License, Release
**Demo GIF:** 3–5s loop of `SMILE`, `PLAY`, `/feed`

**Features**

* Offline terminal pet with constrained personality
* Slash commands or chat
* Strict vocab & action enum for consistent vibe
* Save/resume, ASCII animations, tiny footprint

**Install**

```bash
pipx install terminal-tama
tama
```

**Commands**

```
/feed [item]   /clean [item]   /play [item]   /sleep [on|off]
/pet           /heal            /vet          /status
```

**Toggle LM mode**

```
tama --lm
```

**Config & Saves**

* `~/.terminal_tama/` holds `save.json` and `config.toml`.

**License & Access**

* Source-available under <LICENSE>. Commercial use requires a grant.

---

## 16) sample items & actions (initial 48 entries)

**Foods (12):** small kibble, big kibble, fish snack, milk, tea (calm), soup, berry, cookie, ramen, rice ball, veggie bowl, cake (mood++ energy−)
**Cleaners (6):** soap bar, bubble bath, brush, towel, spray, shampoo
**Play (10):** ball, string, frisbee, plushy, music box, yo-yo, kite, puzzle, blocks, stickers
**Care (8):** bandage, meds_basic, vitamins, hot tea, hug (non-item), nap, vet, warm blanket
**Special (6):** birthday hat, sparkle dust (mood burst), cozy lamp (sleep boost), diary (affection++), star snack, fresh water
**Utility (6):** alarm, lullaby, snack box, treat jar, toy box, bath salts

(Ship with 24 on day one; the schema allows adding more without code changes.)

---

## 17) day-by-day ship plan (7 days)

**Day 1 (2–4h):**

* Repo init, poetry, Typer skeleton, state model, save/load JSON, slash commands `/feed /clean /play /status /sleep /quit`.
* Bars + simple screen with Rich. Autosave.

**Day 2:**

* Decay tick loop + events log. Items YAML loader + effects. Cooldowns. Tests for decay/effects.

**Day 3:**

* Deterministic responder templates + vocab filter (for safety even in det mode). Action enum mapping → animations (stub one frame). `/pet`, `/heal`, `/vet`.

**Day 4:**

* ASCII animation system (multi-frame). 10 actions implemented. Theme toggle. Error overlays.

**Day 5:**

* Optional tiny LM mode wrapper + JSON post-processor + fallback. Config file.

**Day 6:**

* Polish: “first-run” experience, seed inventory, tutorial tips, demo GIF. Build PyPI package + `pipx` smoke test.

**Day 7:**

* Release: cut `v0.1.0`, write README, Nuxt landing page (buy → repo invite), founder tier list. Record a 30-sec demo video.

---

## 18) future-proofing hooks (but do not build now)

* **Event bus** (in-proc): simple `publish("INTEGRATION:X", payload)`; can later bind MCP/VSCode.
* **Signals** for “workday context”: commit count, test pass %, new email count.
* **Theme packs** for the pet ASCII art; exportable to web/canvas later.
* **Serializer boundary**: keep `PetSave` stable for migration.

---

## 19) acceptance criteria (MVP done when…)

1. Fresh install runs with `tama`, shows pet and stat bars.
2. `/feed`, `/clean`, `/play`, `/sleep`, `/pet`, `/status` all work and mutate stats.
3. Tick decay visibly changes bars over ~5 minutes.
4. Chatting “let’s play” yields a valid `say` and `action` response (det mode).
5. Action renders an ASCII animation (≥ 8 actions implemented).
6. Save resumes correctly after restart.
7. Optional `--lm` works; invalid LM output is corrected or safely falls back.
8. No crashes during a 15-minute smoke session.

---

## 20) crisp implementation notes

* **Time math:** store `last_tick_ts`; on loop, apply `int((now-last_tick)/60)` ticks to tolerate sleep/resume.
* **Cooldowns:** per item id; store `last_used_ts[item_id]`.
* **Input parsing:** if line begins `/`, it’s a command; else free-text. Empty lines ignored.
* **Vocab filter:** tokenization by simple `\w+` boundary; lowercase; if not in set, drop; if sentence ends empty, use fallback phrase “hm?”
* **Animations:** pre-load frames to memory; render with `Textual` timers.
* **Safety:** never exec code, no file writes outside the save folder, no network.

---

## 21) tiny bits of starter content

**Sample deterministic replies**

* Neutral: `["hi!", "happy now", "wiggle!", "friend here", "play soon?"]`
* Hungry (<20): `["hungry now…", "kibble please", "tummy empty"]`
* Dirty (<30): `["wash please", "soap time", "messy… sorry"]`
* Sleepy (energy<20): `["nap now", "sleep soon", "eyes heavy"]`
* Loved (after `/pet`): `["love you", "thank you", "heart heart"]`

**Default stats**: hunger 70, hygiene 70, mood 70, energy 70, affection 50, health 100.

---

## 22) pricing & go-to-market (minimum viable)

* **$9 Early Access**: binaries + read-only repo access.
* **$19 Supporter**: LM mode assets, early theme packs, priority bug fixes.
* **$39 Founder**: name in credits, “Founder’s Collar” cosmetic animation.
* **Refund policy**: 7-day no-questions.
* **Roadmap teaser** on landing page: VSCode pane, Apple Watch glance, MCP “workday mood”.

---

## 23) release checklist

* [ ] Run `ruff`/`mypy`
* [ ] `pytest -q` green
* [ ] Demo GIF & 30s video
* [ ] PyPI publish + `pipx install` test
* [ ] GitHub Release with binaries
* [ ] Landing page live with buy flow
* [ ] Onboarding email (text + GIF) for buyers with quick tips

---

## 24) copy-paste prompt for your Nuxt landing page hero

> **terminal-tama** — a cozy terminal pet with a tiny brain and a big heart.
> Feed it, clean it, play a little. It chats back with a soft, simple voice and reacts with cute ASCII moves. 100% offline, fast, and yours.
> **Ship your new best friend in 30 seconds: `pipx install terminal-tama`.**

CTA: *Get Early Access – $9*

---

## 25) founder notes (what makes this scalable later)

* The **action-enum + vocab** contract is portable to any surface (web, native, watch).
* The **state/decay engine** can read *signals* (git commits, tests passing, email count) to make the pet responsive to your work life without being “smart”.
* The **deterministic core** guarantees fun without GPU/LLM; LM just adds flavor.

---

if you want, I can spin up:

* a ready-to-commit `pyproject.toml`,
* a `cli.py` Typer entrypoint,
* a tiny `state.py` with decay + save,
* and 10 starter ASCII animations.

say the word and I’ll drop those files exactly how you need them.
