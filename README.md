# 🌙 Interactive Bedtime Stories

An AI-powered storytelling playground for children aged **5-10**.  
Describe any adventure, guide the plot with on-screen choices, then listen to a narrated ending and view a DALL·E-generated poster of your tale.


[▶️ Watch the demo video](https://drive.google.com/file/d/1fWaqwoZ10Ddna2wdaBhEQVGa9LLtnL3i/view?usp=sharing)
[▶️ Alternate demo video](https://drive.google.com/file/d/1W55_Ww8nEvP7qraw9fTsh6rSy186S3vN/view?usp=drive_link)

---

## Features

| Module | Description |
|--------|-------------|
| **Story Generator** | 3-scene branching stories written by GPT-4o-mini. Scenes 1–2 finish with two bold numbered choices; scene 3 wraps up the arc. |
| **Category Menu** | Choose among 7 kid-friendly genres (Fantasy & Magic, Animal Adventures …). |
| **Live Feedback** | Rewrite any scene by entering feedback; the model revises that scene in-place. |
| **Poster** | After scene 3, generate a **1024×1024** DALL·E-3 illustration that captures the whole story. |
| **Narration (TTS)** | Listen to any scene with selectable voices (Dad, Mom, Sister, Grandad). Uses the new `tts-1` model and streams audio into Gradio. |
| **Learn Something** | Extracts an interesting noun from the story, fetches a kid-friendly fact, and narrates it. |
| **LLM Judge** | Rates the finished story on Age-Appropriateness, Ease of Reading, and Moral Clarity. |
| **CLI fallback** | `base.py` lets you generate a one-shot story from the terminal if you can’t run the web UI. |

---

## Quick Start

```bash
# 1 · Install deps (Python 3.9+)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2 · Add your key
cp .env.example .env  # then edit and set OPENAI_API_KEY=<your-key>

# 3 · Run the app
python app.py  # opens http://127.0.0.1:7860/ in your browser
```

> ⚠️  The app calls newer OpenAI endpoints: **images.generate** (DALL-E-3) and **audio.speech** (`tts-1`).
> Make sure your account has access or swap to older models in `app.py`.

---

## Project Structure

```
hippocratic_ai/
├── app.py           # Gradio UI, all interactive features
├── base.py          # Simple CLI fallback
├── enrich_idea.py   # Expands terse prompts into vivid premises
├── config.py        # Prompt templates & evaluation criteria
├── requirements.txt # Pinned runtime dependencies
├── README.md        # ← you are here
└── .env.example     # Skeleton for environment variables
```

### Key Files

* **app.py** – Orchestrates the user session, maintains `state` dict with scenes and metadata, and wires all Gradio components.
* **enrich_idea.py** – Optional helper that pads very short ideas into a couple of lively sentences.
* **config.py** – Central place for model names, advanced prompt templates, and story structure definitions.
* **base.py** – Minimal illustration of using the same chat prompt from a terminal.

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Your secret API key (required). |
| `OPENAI_API_BASE` | Custom endpoint (optional, for Azure/OpenRouter, etc.). |

Place them in `.env` or export in your shell.

---

## Planned Roadmap

1. **V1 (current)** – Story + Judge + CLI.  
2. **V2** – Add DALL-E poster generation (✓).  
3. **V3** – “Learn Something” educational side-kick and multi-voice TTS (✓).  
Future ideas: multiplayer co-authoring, progress-adaptive vocabulary, saving stories to PDF.

---

## License

MIT.  Use freely, but please keep it friendly for kids. ❤
