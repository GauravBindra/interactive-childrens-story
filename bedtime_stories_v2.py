"""
bedtime_stories_v2.py - Children's story generator using enrich_idea.py
"""

import os
import time
import sys
from pathlib import Path
import gradio as gr
from openai import OpenAI

# ------------ Ensure enrich_idea.py is importable ------------
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.append(str(CURRENT_DIR))

# Import the enriched idea generator
from enrich_idea import generate_enriched_idea

# ------------ OpenAI client setup ------------
client = OpenAI()
STORY_MODEL = "gpt-4o-mini"  # Updated to use GPT-4o mini

# ------------ Story template ------------
STORY_TEMPLATE = """
You are a friendly storyteller for children (ages 5-10).
Create an engaging, wholesome tale about the following enriched idea:

"{enriched_idea}"

Your story should:
- Be written in simple, age-appropriate language
- Include colorful descriptions and dialogue
- Contain a gentle moral lesson
- End with a question that encourages the child to reflect
- Be approximately 400-500 words in length

Make the story lively and magical!
"""

# ------------ Helper function for progress updates ------------
def update_progress(progress_obj, value, desc=None):
    """Safely update progress without triggering boolean evaluation"""
    if progress_obj is not None:
        try:
            progress_obj(value, desc=desc)
        except Exception as e:
            print(f"[DEBUG] Progress error: {e}")


def generate_story_with_updates(child_prompt, progress=None):
    """Generate a story with progress updates"""
    child_prompt = child_prompt.strip()
    if not child_prompt:
        return "⚠️ Please enter a prompt first."

    try:
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "⚠️ Error: OPENAI_API_KEY environment variable not set."

        # Step 1: Enrich the idea (with safe progress update)
        update_progress(progress, 0.2, desc="Enriching your idea...")
        
        # Use the imported enrich_idea function
        try:
            enriched_idea = generate_enriched_idea(child_prompt)
            print(f"[INFO] Enriched idea: '{enriched_idea}'")
        except Exception as e:
            print(f"[DEBUG] Idea enrichment error: {e}")
            enriched_idea = f"A magical adventure about {child_prompt} that teaches children about friendship and courage."

        # Update progress safely
        update_progress(progress, 0.5, desc="Crafting your story...")

        # Step 2: Generate the story
        try:
            response = client.chat.completions.create(
                model=STORY_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a friendly storyteller for children."
                    },
                    {
                        "role": "user", 
                        "content": STORY_TEMPLATE.format(enriched_idea=enriched_idea)
                    },
                ],
                temperature=0.7,
            )
            
            # Extract story text safely
            story_text = "Once upon a time..."  # Default fallback
            
            if hasattr(response, 'choices') and response.choices:
                if len(response.choices) > 0:
                    choice = response.choices[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        story_text = choice.message.content.strip()
                        
        except Exception as e:
            print(f"[DEBUG] Story generation error: {e}")
            story_text = f"""
Once upon a time, there was {enriched_idea}
            
The story continues with adventures and lessons, but we'll have to imagine them today.
What do you think happened next?
            """

        # Final progress update
        update_progress(progress, 1.0, desc="Done!")
        
        return story_text

    except Exception as e:
        return f"⚠️ Error: {e}"


def generate_story(child_prompt, progress=gr.Progress()):
    """Wrapper function for the UI"""
    return generate_story_with_updates(child_prompt, progress)


# ------------ UI Interface ------------
with gr.Blocks(title="Bedtime Stories") as demo:
    gr.Markdown("## 📚 Bedtime Stories\nType your idea and press **Tell Story**.")
    
    with gr.Row():
        with gr.Column(scale=3):
            child_inp = gr.Textbox(
                label="Your idea", 
                placeholder="Tell me a story about...",
                lines=2
            )
    
    with gr.Row():
        with gr.Column(scale=3):
            story_out = gr.Textbox(
                label="Your story", 
                lines=15, 
                interactive=False
            )
    
    with gr.Row():
        tell_btn = gr.Button("Tell Story", variant="primary")
        clear_btn = gr.ClearButton([child_inp, story_out], value="New Story")
    
    tell_btn.click(
        generate_story, 
        inputs=child_inp, 
        outputs=story_out
    )

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")
    
    print("[INFO] Starting Bedtime Stories app...")
    demo.launch()
