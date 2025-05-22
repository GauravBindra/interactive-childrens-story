"""
bedtime_stories.py - Minimal children's story generator using step_back.py
"""

import os
import time
import sys
from pathlib import Path
import gradio as gr
from openai import OpenAI

# ------------ Ensure step_back.py is importable ------------
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.append(str(CURRENT_DIR))

# Import the existing step_back functionality
from step_back import generate_step_back_query

# ------------ OpenAI client setup ------------
client = OpenAI()
STORY_MODEL = "gpt-3.5-turbo"

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

        # Step 1: Generate step-back query (with safe progress update)
        update_progress(progress, 0.2, desc="Creating step-back query...")
        
        # Use the imported step_back function
        sbq_response = generate_step_back_query(child_prompt, api_key, model="gpt-3.5-turbo")
        
        # Extract the query
        if sbq_response.startswith("⚠️"):
            # If there's an error, use a simple fallback
            sbq_str = f"Tell a children's story about {child_prompt}"
        else:
            # Extract the query part if it has the prefix
            if "Step-Back Query:" in sbq_response:
                sbq_str = sbq_response.split("Step-Back Query:", 1)[1].strip()
            else:
                # Use as-is if no prefix
                sbq_str = sbq_response.strip()

        # Update progress safely
        update_progress(progress, 0.5, desc="Crafting your story...")

        # Step 2: Generate the story
        try:
            response = client.chat.completions.create(
                model=STORY_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly storyteller for children (ages 5-10). "
                            "Create engaging, wholesome tales in simple language and "
                            "end with a gentle question to encourage interaction."
                        ),
                    },
                    {"role": "user", "content": sbq_str},
                ],
                temperature=0.8,
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
            story_text = f"Once upon a time, there was a {child_prompt}... (Error occurred, but I'll tell you a story anyway)"

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
