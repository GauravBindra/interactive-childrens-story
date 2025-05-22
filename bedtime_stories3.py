"""
bedtime_stories_gradio.py · three-part interactive story with Gradio UI
"""

import os
import openai
import gradio as gr

# Optional prompt-enricher (uncomment if you added enrich_idea.py)
# from enrich_idea import generate_enriched_idea

# ---------- CONFIG ---------------------------------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

SCENE_TEMPLATE = """
You are a children’s storyteller. Write **SCENE {scene_no}/3** of an
age-5-to-10 bedtime story (≈ 150 words).

**The child asked for a story about “{idea}”. Make sure this idea is
central to the scene and appears within the first two sentences.**

• For scenes 1 & 2, end with **exactly two numbered choices** (“1.” and “2.”).  
• Scene 3 should finish the tale (no choices).

Story so far:
\"\"\"{story_so_far}\"\"\"

last_choice = "{last_choice}"
If last_choice == "N/A", this is the opening scene;
otherwise, briefly acknowledge the child’s last choice before continuing.
"""

# ---------- LLM HELPERS ----------------------------------------------------
def call_llm(prompt: str) -> str:
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=350,
    )
    return response.choices[0].message.content.strip()


def generate_scene(
    scene_no: int,
    story_so_far: str,
    last_choice: str,
    idea: str,
) -> str:
    prompt = SCENE_TEMPLATE.format(
        scene_no=scene_no,
        story_so_far=story_so_far,
        last_choice=last_choice,
        idea=idea,
    )
    return call_llm(prompt)


# ---------- GRADIO LOGIC ---------------------------------------------------
def start_story(child_prompt, state):
    """Handle the first “Start Story” click."""
    raw = child_prompt.strip()
    if not raw:
        return (
            gr.update(value="🌙 Please describe the story you want first!"),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            state,
        )

    # --- optional enrichment ---------------------------------------------
    # idea = generate_enriched_idea(raw) if len(raw.split()) < 4 else raw
    idea = raw  # use this line if you don’t want automatic enrichment

    scene1 = generate_scene(1, "", "N/A", idea)

    state = {
        "scene_no": 1,
        "story": scene1,
        "last_choice": None,
        "idea": idea,
    }

    opt1, opt2 = _extract_options(scene1)

    return (
        gr.update(value=scene1),
        gr.update(value=opt1, visible=True),
        gr.update(value=opt2, visible=True),
        gr.update(visible=False),  # restart hidden
        state,
    )


def choose(option_text, state):
    """Handle choice buttons for scenes 1 & 2."""
    scene_no = state["scene_no"] + 1
    story_so_far = state["story"]

    scene = generate_scene(scene_no, story_so_far, option_text, state["idea"])

    story_combined = (
        story_so_far + f"\n\nChild chose: {option_text}\n\n" + scene
    )
    state.update({"scene_no": scene_no, "story": story_combined})

    if scene_no < 3:
        opt1, opt2 = _extract_options(scene)
        return (
            gr.update(value=story_combined),
            gr.update(value=opt1, visible=True),
            gr.update(value=opt2, visible=True),
            gr.update(visible=False),
            state,
        )
    else:  # scene 3 finished
        ending = story_combined + "\n\n⭐ The End!"
        return (
            gr.update(value=ending),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),  # show restart
            state,
        )


def new_story(state):
    state = {"scene_no": 0, "story": "", "last_choice": "N/A", "idea": ""}
    return (
        gr.update(value=""),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        state,
    )


def _extract_options(scene_text: str):
    """Return the two numbered choices; fallback if model misbehaves."""
    lines = [ln.strip() for ln in scene_text.splitlines()]
    opts = [ln for ln in lines if ln.startswith(("1.", "2."))]
    if len(opts) != 2:
        opts = ["1. Continue bravely", "2. Take a quiet turn"]
    return opts[0], opts[1]


# ---------- GRADIO UI ------------------------------------------------------
with gr.Blocks(title="Interactive Bedtime Stories 🌙") as demo:
    gr.Markdown("## 🌙 Interactive Bedtime Stories\n"
                "Tell me what adventure you’d like, then choose where it goes!")

    story_state = gr.State(
        {"scene_no": 0, "story": "", "last_choice": "N/A", "idea": ""}
    )

    with gr.Row():
        prompt_box = gr.Textbox(
            label="Story idea",
            placeholder="e.g. A brave kitten exploring space…",
            lines=1,
        )
        start_btn = gr.Button("Start Story", variant="primary")

    story_display = gr.Markdown()

    with gr.Row():
        choice_btn1 = gr.Button(visible=False)
        choice_btn2 = gr.Button(visible=False)

    restart_btn = gr.Button("Tell me another story!", visible=False)

    # -- wiring --
    start_btn.click(
        start_story,
        inputs=[prompt_box, story_state],
        outputs=[story_display, choice_btn1, choice_btn2, restart_btn, story_state],
    )
    choice_btn1.click(
        choose,
        inputs=[choice_btn1, story_state],
        outputs=[story_display, choice_btn1, choice_btn2, restart_btn, story_state],
    )
    choice_btn2.click(
        choose,
        inputs=[choice_btn2, story_state],
        outputs=[story_display, choice_btn1, choice_btn2, restart_btn, story_state],
    )
    restart_btn.click(
        new_story,
        inputs=[story_state],
        outputs=[story_display, choice_btn1, choice_btn2, restart_btn, story_state],
    )

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo.launch()
