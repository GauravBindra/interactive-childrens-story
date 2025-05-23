# Hippocratic AI Coding Assignment – Final Report *(app6.py, May 2025)*

## 1 · Goal of the project  
Create a prototype **Bedtime-Story Agent** that:

* accepts a child’s idea + category and writes a 3-scene interactive story (ages 5-10)  
* delivers each scene in text **and** streaming OpenAI TTS  
* lets the child pick choices, give feedback, and “learn something” extra  
* provides a mini **LLM Judge** to rate the finished story on key quality metrics  
* runs wholly in a single `app6.py` using Gradio + OpenAI Python SDK  

---

## 3 · Key implementation details  

| Aspect | Implementation snippet | Note |
|--------|-----------------------|------|
| **Prompting** | `SCENE_TEMPLATE` includes explicit style rules (<150 w, emojis, numbered choices). | Ensures short, vivid scenes. |
| **Category menu** | Seven categories hard-wired in left side-bar (`Animals`, `Space`, `Friendship`, etc.). | Selected value interpolated in prompt. |
| **Audio generation** | `async with client.audio.speech.with_streaming_response.create(..., response_format="pcm")` streamed into a `BytesIO` buffer, WAV header prepended, Base-64 → `<audio>` source. | Zero temp files; terminal no longer floods with PCM bytes. |
| **“Learn something” extractor** | Picks the *rarest lower-case* token not dominated by capitals; falls back to a one-line LLM request. | Avoids manual stop-list. |
| **Idea enrichment** | `generate_enriched_idea()` from `enrich_idea.py` expands terse prompts into 1–2 lively sentences before story generation. | Ensures the model receives rich, age-appropriate context even when the child provides only a few words. |
| **Judge reset** | `reset_judge()` hides table + button whenever a new story is launched. | Prevents stale scores on a new run. |
| **Caching** | Two dicts: `_audio_cache` & `_judge_cache`, keys = MD5 of cleaned text. | Saves tokens and latency. |

---

## 4 · Demo walk-through  

1. **Enter idea + choose category → Generate Scene 1**  
   * Story text appears with emojis and two numbered options.  
   * Audio auto-plays in selected voice (`fable`, `shimmer`, `nova`, `onyx`).  

2. **Child clicks choice 1 or 2 → Scene 2 / Scene 3**  
   * Agent nods to last choice in one sentence, continues.  

3. **After Scene 3:**  
   * **“Run LLM Judge”** button appears → returns 3-row score sheet.  
   * **“Learn Something”** button appears → 25-second fun-fact audio (e.g. *“Pollination is how flowers…”*).  

---

## 5 · Testing & results  

* Ten manual runs with varied categories: all stories < 155 words per scene; Judge average ≥ 8 / 10.  
* TTS latency ≈ 1 s per 20 words (24 kHz mono).  
* No leftover Judge tables between new stories; caches hit on 2nd playback.  

---

## 6 · What I would add with more time  

* **Profile onboarding** – child name, preferred voice, reading level (gates sentence length).  
* **Safety panel** – OpenAI Moderation results + flagged tokens.  
* **Reading-speed slider** – exposes TTS `rate` for accessibility.  
* **Printable PDF “Story Card”** with text, thumbnails, QR to audio.  

---

## 7 · Conclusion  

`app.py` demonstrates a complete miniature **conversation layer**:
* multi-step prompting, stateful branching, model-in-the-loop evaluation  
* real-time audio synthesis without terminal noise  
* educational add-ons (Learn Something)  
* clear, safety-aware scoring rubric  
