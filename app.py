# app5.py – Interactive Bedtime Stories with Poster 🖼️ and TTS 🔊
# ------------------------------------------------------------------
# After the final scene (Scene 3) we automatically generate a DALL·E-3
# poster summarising the whole story, and you can listen to any scene
# via OpenAI TTS (streaming, synchronous – no asyncio required).
# ------------------------------------------------------------------

from __future__ import annotations

import os
import re
import textwrap
import tempfile
from pathlib import Path
from typing import List
import base64
import hashlib

import openai
import gradio as gr
from openai import OpenAI, OpenAIError

# ---------- CONFIG ---------------------------------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"
TTS_MODEL = "tts-1"              # correct OpenAI TTS model
TEMPERATURE = 0.4

# Voice options for narration
VOICE_OPTIONS = {
    "fable": "👨 Dad (Default)",
    "shimmer": "👩 Mom", 
    "nova": "👧 Sister",
    "onyx": "👴 Grandad"
}
DEFAULT_VOICE = "fable"

# TTS narration instructions for bedtime story atmosphere
TTS_INSTRUCTIONS = (
    "Speak slowly and softly, like a bedtime storyteller. "
    "Put a tiny pause after each sentence. "
    "Smile in your voice; sound friendly and reassuring. "
    "Keep overall volume low so it won't startle a sleepy child."
)

# Seven core genres
CATEGORIES = [
    "Animal Adventures",
    "Fantasy & Magic",
    "Friendship & Emotional Growth",
    "Mystery & Problem-Solving",
    "Humor & Silly Situations",
    "Science & Space Exploration",
    "Values & Morals (Fables)",
]
DEFAULT_CATEGORY = CATEGORIES[0]

# ---------- PROMPT TEMPLATES ----------------------------------------------
SCENE_TEMPLATE = '''
You are a children's storyteller. Write **SCENE {scene_no}/3** of an
age-5-to-10 bedtime story (≈ 150 words).

**Category:** {category}
**Child's idea:** "{idea}"
👉 *Work the idea into the first two sentences.*

### Story-Arc Requirements
- **Scene 1** – introduce the main character and their WANT/PROBLEM.
- **Scene 2** – raise the stakes; a challenge appears.
- **Scene 3** – climax and satisfying resolution. No numbered choices.

### Style Rules
1. Use vivid language and **relevant emojis** (😀🐉🍪🌟🚀 …).
2. Keep sentences short and clear.
3. Leave a blank line between paragraphs.
4. **Scenes 1 & 2:** end with *exactly two* **bold** numbered choices ("1." & "2.").
5. **Scene 3:** wrap up the tale (no choices). Do **not** write "The end." before Scene 3.
6. Each scene should clearly advance the arc.

Story so far:
"""{story_so_far}"""

`last_choice` = "{last_choice}"
If `last_choice` == "N/A" this is the opening scene, otherwise nod to the child's choice in one friendly sentence before continuing.
'''

REVISION_TEMPLATE = '''
You previously wrote SCENE {scene_no}/3 …

Rewrite the scene so it satisfies the feedback below. **Change at least two sentences visibly** and keep to the style rules (including **bold** choice text).

Feedback: "{feedback}"

Original scene:
"""{original_scene}"""
'''

# ---------- LLM CORE -------------------------------------------------------

def _chat(prompt: str) -> str:
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
        max_tokens=600,
    )
    return resp.choices[0].message.content.strip()

# ---------- TTS (TEXT-TO-SPEECH) ------------------------------------------

_client = OpenAI()                       # uses OPENAI_API_KEY env-var
_audio_cache: dict[str, str] = {}        # md5(clean_text) ➜ data-URL

def _clean_for_tts(raw: str) -> str:
    """Remove markdown markers and numbered options; truncate at 4096 chars."""
    no_md = re.sub(r"[*_`#🌟]", "", raw)
    no_opts = "\n".join(
        ln for ln in no_md.splitlines() if not ln.strip().startswith(("1.", "2."))
    )
    return no_opts[:4096]


def _generate_audio(text: str) -> str:
    """Return a base-64 data-URL (audio/mp3) for Gradio's <audio> component."""
    clean = _clean_for_tts(text)
    h = hashlib.md5(clean.encode()).hexdigest()
    if h in _audio_cache:
        return _audio_cache[h]

    try:
        # 1. Stream TTS to a temporary mp3 file ----------------------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = Path(tmp.name)

        with _client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL,
            voice=DEFAULT_VOICE,  # Use default voice for the cached version
            input=clean,
            speed=0.9  # Slightly slower for bedtime stories
        ) as resp:
            resp.stream_to_file(tmp_path)

        # 2. Read, encode, cache ------------------------------------------
        mp3_bytes = tmp_path.read_bytes()
        data_url = "data:audio/mp3;base64," + base64.b64encode(mp3_bytes).decode()
        _audio_cache[h] = data_url
        tmp_path.unlink(missing_ok=True)
        return data_url

    except OpenAIError as e:
        print("[TTS] error:", e)
        return ""  # silent failure keeps UI responsive

# ---------- IMAGE GENERATION ----------------------------------------------

def _generate_poster(scenes: List[str]) -> str:
    """Return a DALL·E-3 image URL representing the whole story."""
    story_text = " ".join(scenes)
    story_essence = textwrap.shorten(story_text, width=200, placeholder="…")

    prompt = (
        f"A fantasy scene with {story_essence}\n\n"
        "Medium: Digital painting\n"
        "Style: Soft, dreamlike, no text\n\n"
        "Rule: Image only. Zero text. No words. No letters. No writing. No labels. No captions. Visual only."
    )

    img_resp = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="url",
    )
    return img_resp.data[0].url

# ---------- LLM JUDGE MODULE ----------------------------------------------

# Judge evaluation prompt
JUDGE_PROMPT = """
You are an expert in children's literature and child development. Evaluate this bedtime story for ages 5-10.

Story to evaluate:
\"\"\"
{story}
\"\"\"

Please evaluate the story on these 3 key criteria (score 1-10 for each):

1. **Age Appropriateness**: Is the vocabulary, themes, and content suitable for ages 5-10?
2. **Ease of Reading**: How easy is it for children to follow and understand?
3. **Clarity of Moral/Takeaway**: Is there a clear, positive lesson or message?

For each criterion:
- Give a score (1-10)
- Provide a brief explanation (1-2 sentences)

End with:
- Overall Score (average of the 3 scores)
- Final Verdict (2-3 sentences summarizing the story's quality as a bedtime story)

Format your response clearly with scores and explanations.
"""

def judge_story(state: dict):
    """Evaluate the completed story using LLM judge"""
    if not state.get("scenes") or len(state["scenes"]) < 3:
        return gr.update(value="⚠️ Please complete the story first!", visible=True)
    
    # Get the full story
    full_story = "\n\n".join(state["scenes"])
    
    # Get judge evaluation
    try:
        response = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert evaluator of children's bedtime stories."},
                {"role": "user", "content": JUDGE_PROMPT.format(story=full_story)}
            ],
            temperature=0.3,  # Lower temperature for more consistent evaluation
            max_tokens=500
        )
        
        evaluation = response.choices[0].message.content.strip()
        
        # Format the evaluation nicely
        formatted_eval = f"""## 📊 Story Evaluation Report

{evaluation}

---
*Evaluated for ages 5-10 bedtime story standards*
"""
        
        return gr.update(value=formatted_eval, visible=True)
        
    except Exception as e:
        print(f"[Judge Error]: {e}")
        return gr.update(value="⚠️ Error evaluating story. Please try again.", visible=True)

# ---------- LEARN SOMETHING MODULE -----------------------------------------

import collections
import string

def extract_learning_term(story: str) -> str:
    """
    Extract an educational term using smart heuristics:
    - Pick rare (interesting) terms over common ones
    - Avoid proper nouns by checking capitalization patterns
    - Filter out adverbs and past-tense verbs
    - Use LLM fallback if needed
    """
    # 1️⃣  Tokenise (letters/apostrophes only), keep case info
    tokens = re.findall(r"\b[A-Za-z']{4,}\b", story)
    lc_tokens = [t.lower() for t in tokens]

    # 2️⃣  Build frequency table
    counts = collections.Counter(lc_tokens)

    # 3️⃣  Candidate filter:
    #     - appears mostly in lower-case form (prob not a proper noun)
    #     - not an adverb (-ly) or past-tense (-ed)  → kids find actions/objects easier
    cands = []
    for tok in set(lc_tokens):
        if tok.endswith(("ly", "ed")):
            continue
        # how many times was it capitalised?
        caps = sum(1 for t in tokens if t.lower() == tok and t[0].isupper())
        if caps / counts[tok] > 0.5:      # >50 % caps ⇒ likely a name
            continue
        cands.append(tok)

    if cands:
        # Pick the **rarest**, breaking ties by longest length
        cands.sort(key=lambda w: (counts[w], -len(w)))
        return cands[0]

    # 4️⃣  Fallback mini-LLM: ask for ONE teachable term
    prompt = (
        "From the story below, name ONE interesting action, object, or animal "
        "that a 7-year-old could learn about (just the single word, no quotes):\n"
        f"\"\"\"\n{story[:1200]}\n\"\"\""
    )
    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0,
        max_tokens=3,
        messages=[{"role": "user", "content": prompt}],
    )
    term = resp.choices[0].message.content.strip(string.punctuation + " ""\"'")
    return term or "rainbow"

# Keep the old function name for compatibility
def extract_key_noun(story: str) -> str:
    """Wrapper for backward compatibility"""
    return extract_learning_term(story)

# Helper: Get child-friendly fact
_FACT_PROMPT = """Explain "{term}" to a 7-year-old in **three short lines**.
Use friendly language and finish with a question to make them curious."""

def fetch_child_fact(term: str) -> str:
    """Get a kid-friendly fact about the given term"""
    prompt = _FACT_PROMPT.format(term=term)
    resp = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=120,
    )
    return resp.choices[0].message.content.strip()

# Callback for Learn Something button
def learn_something(state: dict):
    """Extract key noun from story, get fact, and generate audio"""
    if not state.get("scenes"):
        return gr.update(visible=False)
    
    # Get the full story so far
    story_text = "\n\n".join(state["scenes"])
    
    # Extract interesting noun and get fact
    term = extract_key_noun(story_text)
    fact = fetch_child_fact(term)
    
    # Generate TTS for the fact using Mom's voice
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name
        
        response = _client.audio.speech.create(
            model=TTS_MODEL,
            voice="shimmer",  # Mom's voice for educational content
            input=fact,
            speed=0.95  # Slightly slower for clarity
        )
        
        with open(tmp_path, 'wb') as f:
            for chunk in response.iter_bytes(1024):
                f.write(chunk)
        
        return gr.update(value=tmp_path, visible=True)
    except Exception as e:
        print(f"[Learn TTS Error]: {e}")
        return gr.update(visible=False)

# ---------- UTILS ----------------------------------------------------------

def _strip_early_ending(text: str, scene_no: int) -> str:
    if scene_no < 3:
        text = re.sub(r"^\s*(The\s+end\.?)(\s*)$", "", text, flags=re.I | re.M)
    return text


def _extract_options(scene_text: str) -> List[str]:
    """Return exactly two **clean** numbered options, or fall back."""
    opts: List[str] = []
    for ln in scene_text.splitlines():
        stripped = ln.strip()
        clean = re.sub(r"[*_`]+", "", stripped)
        if clean.startswith("1.") or clean.startswith("2."):
            opts.append(clean)
    if len(opts) == 2:
        return opts
    return [
        "1. Continue bravely 🌟",
        "2. Take a quiet turn 💤",
    ]

# ---------- STATE STRUCTURE ------------------------------------------------
# state = {scene_no:int, scenes:List[str], idea:str, category:str}

# ---------- CALLBACKS ------------------------------------------------------

def start_story(idea: str, category: str, state: dict):
    idea = idea.strip()
    if not idea:
        return (
            gr.update(value="🌜 *Please type a story idea first!*"),
            *(gr.update(visible=False),) * 11,
            gr.update(value="", visible=False),  # judge_output - clear
            gr.update(visible=False),  # learn_audio - hide
            state,
        )

    scene1 = _chat(
        SCENE_TEMPLATE.format(
            scene_no=1,
            story_so_far="",
            last_choice="N/A",
            idea=idea,
            category=category,
        )
    )
    scene1 = _strip_early_ending(scene1, 1)

    state.clear()
    state.update({"scene_no": 1, "scenes": [scene1], "idea": idea, "category": category})

    opt1, opt2 = _extract_options(scene1)
    return (
        gr.update(value=scene1),
        gr.update(value=opt1, visible=True),
        gr.update(value=opt2, visible=True),
        gr.update(visible=True),   # feedback box
        gr.update(visible=True),   # feedback button
        gr.update(visible=False),  # poster img
        gr.update(visible=False),  # poster btn
        gr.update(visible=True),   # voice dropdown
        gr.update(visible=True),   # narrate btn
        gr.update(visible=False),  # audio player
        gr.update(visible=True),   # learn btn
        gr.update(visible=False),  # judge btn
        gr.update(value="", visible=False),  # judge_output - clear
        gr.update(visible=False),  # learn_audio - hide
        state,
    )


def choose(option_text: str, state: dict):
    scene_no = state["scene_no"] + 1
    combined_story = state["scenes"][-1] + f"\n\n🎲 **You chose:** {option_text}\n\n"

    new_scene = _chat(
        SCENE_TEMPLATE.format(
            scene_no=scene_no,
            story_so_far="\n\n".join(state["scenes"]),
            last_choice=option_text,
            idea=state["idea"],
            category=state["category"],
        )
    )
    new_scene = _strip_early_ending(new_scene, scene_no)
    state["scenes"].append(new_scene)
    state["scene_no"] = scene_no

    if scene_no < 3:
        opt1, opt2 = _extract_options(new_scene)
        display = "\n\n".join(state["scenes"])
        return (
            gr.update(value=display),
            gr.update(value=opt1, visible=True),
            gr.update(value=opt2, visible=True),
            gr.update(visible=True),   # feedback box
            gr.update(visible=True),   # feedback btn
            gr.update(visible=False),  # poster img
            gr.update(visible=False),  # poster btn
            gr.update(visible=True),   # voice dropdown
            gr.update(visible=True),   # narrate btn
            gr.update(visible=False),  # audio
            gr.update(visible=True),   # learn btn
            gr.update(visible=False),  # judge btn
            state,
        )
    else:
        ending = "\n\n".join(state["scenes"]) + "\n\n🌟 **The End!** 🌟"
        return (
            gr.update(value=ending),
            *(gr.update(visible=False),) * 2,     # choice buttons
            gr.update(visible=False),              # feedback box
            gr.update(visible=False),              # feedback btn
            gr.update(visible=False),              # poster img (hidden until click)
            gr.update(visible=True),               # poster btn
            gr.update(visible=True),               # voice dropdown
            gr.update(visible=True),               # narrate btn
            gr.update(visible=False),              # audio
            gr.update(visible=True),               # learn btn
            gr.update(visible=True),               # judge btn - show after story ends
            state,
        )


def apply_feedback(feedback: str, state: dict):
    feedback = feedback.strip()
    if not feedback:
        return gr.update(value="⚠️ Please type feedback."), *(gr.update(visible=False),) * 10, gr.update(visible=False), state

    idx = state["scene_no"] - 1
    revised = _chat(
        REVISION_TEMPLATE.format(
            scene_no=state["scene_no"],
            feedback=feedback,
            original_scene=state["scenes"][idx],
        )
    )
    revised = _strip_early_ending(revised, state["scene_no"])
    state["scenes"][idx] = revised

    display = "\n\n".join(state["scenes"])
    if state["scene_no"] < 3:
        opt1, opt2 = _extract_options(revised)
        return (
            gr.update(value=display),
            gr.update(value=opt1, visible=True),
            gr.update(value=opt2, visible=True),
            gr.update(value="", visible=True),
            gr.update(visible=True),
            gr.update(visible=False),  # poster img
            gr.update(visible=False),  # poster btn
            gr.update(visible=True),   # voice dropdown
            gr.update(visible=True),   # narrate btn
            gr.update(visible=False),  # audio
            gr.update(visible=True),   # learn btn
            gr.update(visible=False),  # judge btn
            state,
        )
    else:
        ending = display + "\n\n🌟 **The End!** 🌟"
        return (
            gr.update(value=ending),
            *(gr.update(visible=False),) * 2,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),  # poster img
            gr.update(visible=True),   # poster btn
            gr.update(visible=True),   # voice dropdown
            gr.update(visible=True),   # narrate btn
            gr.update(visible=False),  # audio
            gr.update(visible=True),   # learn btn
            gr.update(visible=True),   # judge btn
            state,
        )


def generate_poster_clicked(state: dict):
    if state.get("scenes") and len(state["scenes"]) >= 3:
        poster_url = _generate_poster(state["scenes"])
        return gr.update(value=poster_url, visible=True), gr.update(visible=False)
    return gr.update(visible=False), gr.update(visible=True)


def narrate_scene(voice_choice: str, state: dict):
    if state.get("scenes") and state.get("scene_no", 0) > 0:
        latest_scene = state["scenes"][-1]
        
        # Clean text for TTS
        clean_text = _clean_for_tts(latest_scene)
        
        # Use selected voice or default
        selected_voice = voice_choice if voice_choice else DEFAULT_VOICE
        
        # Set speed based on voice
        voice_speeds = {
            "fable": 0.9,     # Dad - slightly slower
            "shimmer": 0.9,   # Mom - slightly slower
            "nova": 1.1,      # Sister - slightly faster
            "onyx": 0.8       # Grandad - slowest
        }
        speed = voice_speeds.get(selected_voice, 0.9)
        
        try:
            # Generate speech and save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp_path = tmp.name
            
            response = _client.audio.speech.create(
                model=TTS_MODEL,
                voice=selected_voice,
                input=clean_text,
                speed=speed
            )
            
            # Write response content to file
            with open(tmp_path, 'wb') as f:
                for chunk in response.iter_bytes(1024):
                    f.write(chunk)
            
            # Return file path instead of data URL
            return gr.update(value=tmp_path, visible=True)
        except Exception as e:
            print(f"[TTS] Error: {e}")
            return gr.update(visible=False)
    return gr.update(visible=False)


def reset(state: dict):
    state.clear()
    return (
        gr.update(value=""),                    # story text
        *(gr.update(visible=False),) * 11,      # all other components
        gr.update(value="", visible=False),     # judge_output - clear and hide
        state,
    )

# ---------- CUSTOM CSS -----------------------------------------------------
CUSTOM_CSS = """
.story-text {
  font-size: 20px;
  line-height: 1.6;
}
.story-text strong {
  font-weight: 700;
}
.choice-btn {
  font-size: 18px !important;
  font-weight: 600;
}
"""

# ---------- UI -------------------------------------------------------------
with gr.Blocks(title="🌙 Interactive Bedtime Stories", css=CUSTOM_CSS) as demo:
    gr.Markdown(
        "## 🌙 **Interactive Bedtime Stories**\n"
        "Describe an adventure, pick a category, then guide the tale – and see a poster of your story!"
    )

    state = gr.State({})

    with gr.Row():
        idea_box = gr.Textbox(
            label="✨ Your story idea",
            placeholder="e.g. A friendly dragon who loves cookies…",
            lines=1,
        )
        cat_menu = gr.Dropdown(choices=CATEGORIES, value=DEFAULT_CATEGORY, label="📚 Category")
        start_btn = gr.Button("🚀 Start Story", variant="primary")

    story_md = gr.Markdown(elem_classes="story-text")

    with gr.Row():
        btn1 = gr.Button(elem_classes="choice-btn", visible=False)
        btn2 = gr.Button(elem_classes="choice-btn", visible=False)

    fb_box = gr.Textbox(label="📝 Request a change", lines=1, visible=False)
    fb_btn = gr.Button("🔄 Apply Feedback", visible=False)

    poster_img = gr.Image(label="🎨 Story Poster", visible=False)
    poster_btn = gr.Button("🎨 Display Poster", variant="primary", visible=False)

    with gr.Row():
        voice_dropdown = gr.Dropdown(
            choices=[(label, voice) for voice, label in VOICE_OPTIONS.items()],
            value=DEFAULT_VOICE,
            label="Choose Narrator",
            visible=False,
            scale=1
        )
        narrate_btn = gr.Button("🔊 Listen to Scene", variant="secondary", visible=False, scale=2)
    
    audio_player = gr.Audio(label="Story Narration", visible=False, autoplay=True)
    
    # Learn Something feature
    with gr.Row():
        learn_btn = gr.Button("🐾 Learn Something", variant="secondary", visible=False)
        learn_audio = gr.Audio(label="Fun Fact", visible=False, autoplay=True)
    
    # Judge feature
    judge_btn = gr.Button("⚖️ Judge Story", variant="secondary", visible=False)
    judge_output = gr.Markdown(visible=False)

    reset_btn = gr.Button("🔄 New Story", visible=False)

    # ---------- Wiring ----------
    start_btn.click(
        start_story,
        inputs=[idea_box, cat_menu, state],
        outputs=[
            story_md,
            btn1,
            btn2,
            fb_box,
            fb_btn,
            poster_img,
            poster_btn,
            voice_dropdown,
            narrate_btn,
            audio_player,
            learn_btn,
            judge_btn,
            judge_output,
            state,
        ],
    )

    btn1.click(
        choose,
        inputs=[btn1, state],
        outputs=[
            story_md,
            btn1,
            btn2,
            fb_box,
            fb_btn,
            poster_img,
            poster_btn,
            voice_dropdown,
            narrate_btn,
            audio_player,
            learn_btn,
            judge_btn,
            state,
        ],
    )
    btn2.click(
        choose,
        inputs=[btn2, state],
        outputs=[
            story_md,
            btn1,
            btn2,
            fb_box,
            fb_btn,
            poster_img,
            poster_btn,
            voice_dropdown,
            narrate_btn,
            audio_player,
            learn_btn,
            judge_btn,
            state,
        ],
    )

    fb_btn.click(
        apply_feedback,
        inputs=[fb_box, state],
        outputs=[
            story_md,
            btn1,
            btn2,
            fb_box,
            fb_btn,
            poster_img,
            poster_btn,
            voice_dropdown,
            narrate_btn,
            audio_player,
            learn_btn,
            judge_btn,
            state,
        ],
    )

    poster_btn.click(
        generate_poster_clicked,
        inputs=[state],
        outputs=[poster_img, poster_btn],
    )

    narrate_btn.click(
        narrate_scene,
        inputs=[voice_dropdown, state],
        outputs=[audio_player],
    )
    
    learn_btn.click(
        learn_something,
        inputs=[state],
        outputs=[learn_audio],
    )
    
    judge_btn.click(
        judge_story,
        inputs=[state],
        outputs=[judge_output],
    )

    reset_btn.click(
        reset,
        inputs=[state],
        outputs=[
            story_md,
            btn1,
            btn2,
            fb_box,
            fb_btn,
            poster_img,
            poster_btn,
            voice_dropdown,
            narrate_btn,
            audio_player,
            learn_btn,
            judge_btn,
            judge_output,
            state,
        ],
    )

    story_md.change(
        lambda x: gr.update(visible=bool(x)),
        inputs=[story_md],
        outputs=[reset_btn],
    )

# --------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")

    demo.launch()
