"""
bedtime_stories_gradio.py · interactive 3-scene bedtime stories with emojis 🎉
"""

import os, re
import openai
import gradio as gr
from enrich_idea import generate_enriched_idea   # prompt-enricher

# ---------- CONFIG ---------------------------------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

SCENE_TEMPLATE = """
You are a children’s storyteller. Write **SCENE {scene_no}/3** of an
age-5-to-10 bedtime story (≈ 150 words).

The child’s idea is: **“{idea}”**.  
👉 *Make sure this idea is central to the scene and appears within the first two sentences.*

### Style rules
1. Use vivid, friendly language and **plenty of relevant emojis** (😀🐉🍪🌟🚀 etc.).  
2. Keep sentences short and clear.  
3. Leave a blank line between paragraphs.  
4. **Scenes 1 & 2:** end with *exactly two* numbered choices (“1.” and “2.”).  
5. **Scene 3:** wrap up the tale (no choices). Do **not** write “The end.” in scenes 1 or 2.

Story so far:
\"\"\"{story_so_far}\"\"\"

`last_choice` = "{last_choice}"  
If `last_choice` == "N/A", this is the opening scene; otherwise, nod to the child’s last choice in one friendly sentence before continuing.
"""

# ---------- LLM HELPERS ----------------------------------------------------
def call_llm(prompt: str) -> str:
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=350,
    )
    return resp.choices[0].message.content.strip()


def generate_scene(scene_no: int,
                   story_so_far: str,
                   last_choice: str,
                   idea: str) -> str:
    prompt = SCENE_TEMPLATE.format(
        scene_no=scene_no,
        story_so_far=story_so_far,
        last_choice=last_choice,
        idea=idea,
    )
    return call_llm(prompt)

# ---------- UTILS ----------------------------------------------------------
def _strip_early_ending(text: str, scene_no: int) -> str:
    if scene_no < 3:
        text = re.sub(r"^\s*(The\s+end\.?)\s*$", "", text, flags=re.I | re.M)
    return text

def _extract_options(scene_text: str):
    lines = [ln.strip() for ln in scene_text.splitlines()]
    opts = [ln for ln in lines if ln.startswith(("1.", "2."))]
    return opts if len(opts) == 2 else ["1. Continue bravely 🌟", "2. Take a quiet turn 💤"]

def _maybe_enrich(raw: str) -> str:
    if len(raw.split()) < 4:
        try:
            return generate_enriched_idea(raw)
        except Exception as e:
            print("Enrich failed:", e)
            return raw
    return raw

# ---------- GRADIO CALLBACKS ----------------------------------------------
def start_story(child_prompt, state):
    raw = child_prompt.strip()
    if not raw:
        return (gr.update(value="🌜 *Please type a story idea first!*"),
                *(gr.update(visible=False),)*3, state)

    idea = _maybe_enrich(raw)
    scene1 = generate_scene(1, "", "N/A", idea)
    scene1 = _strip_early_ending(scene1, 1)

    state = {"scene_no": 1, "story": scene1, "idea": idea}

    opt1, opt2 = _extract_options(scene1)
    return (gr.update(value=scene1),
            gr.update(value=opt1, visible=True),
            gr.update(value=opt2, visible=True),
            gr.update(visible=False), state)

def choose(option_text, state):
    scene_no = state["scene_no"] + 1
    combined_story = (state["story"] +
                      f"\n\n🎲 **You chose:** {option_text}\n\n")
    new_scene = generate_scene(scene_no, state["story"], option_text, state["idea"])
    new_scene = _strip_early_ending(new_scene, scene_no)
    combined_story += new_scene
    state.update({"scene_no": scene_no, "story": combined_story})

    if scene_no < 3:
        opt1, opt2 = _extract_options(new_scene)
        return (gr.update(value=combined_story),
                gr.update(value=opt1, visible=True),
                gr.update(value=opt2, visible=True),
                gr.update(visible=False), state)
    else:
        ending = combined_story + "\n\n🌟 **The End!** 🌟"
        return (gr.update(value=ending),
                *(gr.update(visible=False),)*2,
                gr.update(visible=True), state)

def new_story(state):
    state = {"scene_no": 0, "story": "", "idea": ""}
    return (gr.update(value=""),
            *(gr.update(visible=False),)*3, state)

# ---------- UI -------------------------------------------------------------
with gr.Blocks(title="🌙 Interactive Bedtime Stories") as demo:
    gr.Markdown("## 🌙 **Interactive Bedtime Stories**\n"
                "Describe an adventure, then guide the tale with your choices!")

    story_state = gr.State({"scene_no": 0, "story": "", "idea": ""})

    with gr.Row():
        prompt_box = gr.Textbox(
            label="✨ Your story idea",
            placeholder="e.g. A friendly dragon who loves cookies...",
            lines=1,
        )
        start_btn = gr.Button("🚀 Start Story", variant="primary")

    story_display = gr.Markdown()

    with gr.Row():
        choice_btn1 = gr.Button(visible=False)
        choice_btn2 = gr.Button(visible=False)

    restart_btn = gr.Button("🔄 Tell me another story!", visible=False)

    start_btn.click(start_story,
                    inputs=[prompt_box, story_state],
                    outputs=[story_display, choice_btn1, choice_btn2, restart_btn, story_state])

    choice_btn1.click(choose,
                      inputs=[choice_btn1, story_state],
                      outputs=[story_display, choice_btn1, choice_btn2, restart_btn, story_state])

    choice_btn2.click(choose,
                      inputs=[choice_btn2, story_state],
                      outputs=[story_display, choice_btn1, choice_btn2, restart_btn, story_state])

    restart_btn.click(new_story,
                      inputs=[story_state],
                      outputs=[story_display, choice_btn1, choice_btn2, restart_btn, story_state])

# --------------------------------------------------------------------------
if __name__ == "__main__":
    demo.launch()
