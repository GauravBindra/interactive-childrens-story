"""
ui_test6.py – Interactive Children's Story playground with fixed Gradio progress handling
"""

from pathlib import Path
import sys, os
import time
import traceback
import gradio as gr
from openai import OpenAI

# ------------ OpenAI client (v1 interface) ------------
client = OpenAI()  # relies on OPENAI_API_KEY env var
STORY_MODEL = "gpt-3.5-turbo"  # Using the model from base.py

# ------------ Helper functions ------------
def update_progress(progress_obj, value, desc=None):
    """Safely update progress without triggering boolean evaluation"""
    if progress_obj is not None:
        try:
            progress_obj(value, desc=desc)
            print(f"[DEBUG] Progress updated to {value*100}%: {desc}")
        except Exception as e:
            print(f"[DEBUG] Progress update failed: {e}")


def generate_step_back_query(original_query: str, api_key: str, debug=True):
    """
    A simplified version that's guaranteed not to throw index errors
    """
    # Very basic prompt for testing
    prompt = f"Reformulate this into a step-back query for a children's story: '{original_query}'"
    
    if debug:
        print(f"\n[DEBUG] Original query: '{original_query}'")
        print(f"[DEBUG] API key (first/last 4 chars): {api_key[:4]}...{api_key[-4:]}")
    
    # Use fallback in case of any errors
    fallback_response = f"Step-Back Query: Tell a children's story about {original_query}"
    
    try:
        # Initialize the client
        client = OpenAI(api_key=api_key)
        if debug:
            print("[DEBUG] Created OpenAI client")
        
        # Create chat completion with error handling
        try:
            if debug:
                print("[DEBUG] Sending request to OpenAI API...")
            
            # Use gpt-3.5-turbo as that's what's in base.py
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            
            if debug:
                print("[DEBUG] Received response from API")
            
            # Get content with safe navigation
            content = None
            
            # Try to access nested properties safely
            if hasattr(response, 'choices') and response.choices:
                if debug:
                    print(f"[DEBUG] Response has {len(response.choices)} choices")
                
                if len(response.choices) > 0:
                    choice = response.choices[0]
                    
                    if hasattr(choice, 'message') and choice.message:
                        if debug:
                            print("[DEBUG] First choice has message")
                        
                        if hasattr(choice.message, 'content'):
                            if debug:
                                print("[DEBUG] Message has content")
                            content = choice.message.content.strip() if choice.message.content else ""
                            if debug:
                                print(f"[DEBUG] Content: '{content[:30]}...'")
            
            # Return content if we got it, otherwise fallback
            if content:
                # Make sure it has the Step-Back Query prefix
                if "Step-Back Query:" not in content:
                    content = f"Step-Back Query: {content}"
                return content
            else:
                if debug:
                    print("[DEBUG] Couldn't extract content, using fallback")
                return fallback_response
                
        except Exception as e:
            if debug:
                print(f"[DEBUG] API request failed: {e}")
                print(traceback.format_exc())
            return fallback_response
            
    except Exception as e:
        if debug:
            print(f"[DEBUG] Client creation failed: {e}")
            print(traceback.format_exc())
        return fallback_response


def generate_story_with_updates(child_prompt: str, progress=None):
    """Generate a story with progress updates."""
    print(f"\n[DEBUG] Starting generate_story_with_updates with prompt: '{child_prompt}'")
    
    child_prompt = child_prompt.strip()
    if not child_prompt:
        return "⚠️ Please enter a prompt first."

    try:
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "⚠️ Error: OPENAI_API_KEY environment variable not set."
        print(f"[DEBUG] Got API key: {api_key[:4]}...{api_key[-4:]}")

        # FIXED: Use the safe update_progress function instead of directly checking 'if progress'
        update_progress(progress, 0, desc="Starting…")

        # Step 1: step-back reformulation
        update_progress(progress, 0.2, desc="Creating step-back query…")

        # Call with api_key parameter using our embedded function
        print(f"[INFO] Starting step-back query generation for: '{child_prompt}'")
        sbq_response = generate_step_back_query(child_prompt, api_key, debug=True)
        print(f"[DEBUG] Step-back query response: '{sbq_response}'")
        
        # Check for errors in step-back response
        if sbq_response.startswith("⚠️"):
            # If there's an error, use a simple fallback
            sbq_str = f"Tell a children's story about {child_prompt}"
            print(f"[DEBUG] Using fallback query: '{sbq_str}'")
        else:
            # Extract the query part if it has the prefix
            if "Step-Back Query:" in sbq_response:
                sbq_str = sbq_response.split("Step-Back Query:", 1)[1].strip()
                print(f"[DEBUG] Extracted query: '{sbq_str}'")
            else:
                # Use as-is if no prefix
                sbq_str = sbq_response.strip()
                print(f"[DEBUG] Using response as-is: '{sbq_str}'")

        update_progress(progress, 0.4, desc="Analyzing theme…")
        time.sleep(0.2)  # Reduced sleep time
        update_progress(progress, 0.6, desc="Crafting your story…")

        # Step 2: story generation
        print(f"[INFO] Generating story using model: {STORY_MODEL}")
        print(f"[INFO] Using step-back query: '{sbq_str}'")
        
        story_text = "Once upon a time..."  # Default fallback
        
        try:
            print("[DEBUG] Creating story completion request")
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
            print("[DEBUG] Story completion request successful")
            
            # Extremely defensive extraction
            if hasattr(response, 'choices') and response.choices:
                print(f"[DEBUG] Response has 'choices' attribute with {len(response.choices)} items")
                
                # Safe access to the first choice
                choices = response.choices
                if choices and len(choices) > 0:
                    choice = choices[0]
                    
                    if hasattr(choice, 'message'):
                        message = choice.message
                        
                        if hasattr(message, 'content'):
                            content = message.content
                            story_text = content.strip() if content else story_text
                            print(f"[DEBUG] Story text (first 50 chars): '{story_text[:50]}...'")
            else:
                print("[DEBUG] Response missing 'choices' attribute or empty")
                
        except Exception as e:
            print(f"[ERROR] Story generation failed: {e}")
            print(traceback.format_exc())
            # Continue with fallback story_text

        update_progress(progress, 0.9, desc="Finalising…")
        time.sleep(0.2)  # Reduced sleep time
        update_progress(progress, 1.0, desc="Done!")

        print(f"[DEBUG] Returning story of length: {len(story_text)}")
        return story_text

    except Exception as e:
        # Show the exact exception so the user knows what went wrong
        print(f"[ERROR] Exception in story generation: {e}")
        print(traceback.format_exc())
        return f"⚠️ Error: {e}"


def generate_story(child_prompt: str, progress=gr.Progress()):
    """
    Wrapper function for story generation with progress updates.
    
    Parameters
    ----------
    child_prompt : str
        The user's story request
    progress : gr.Progress
        Gradio progress indicator
        
    Returns
    -------
    str
        The generated story or error message
    """
    print(f"[DEBUG] generate_story called with prompt: '{child_prompt}'")
    try:
        result = generate_story_with_updates(child_prompt, progress)
        print(f"[DEBUG] generate_story completed successfully, result length: {len(result)}")
        return result
    except Exception as e:
        print(f"[ERROR] Exception in generate_story wrapper: {e}")
        print(traceback.format_exc())
        return f"⚠️ Error in story generation: {e}"


with gr.Blocks(title="Interactive Children's Story") as demo:
    gr.Markdown("## 📚 Interactive Children's Story\nType your idea and press **Tell Story**.")
    
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
    
    # Information about the process
    with gr.Accordion("What's happening behind the scenes?", open=False):
        gr.Markdown("""
        When you press **Tell Story**, the following happens:
        
        1. **Step-back query**: Your request is transformed into a broader theme
        2. **Story crafting**: The AI creates a custom story based on your theme
        3. **Final touches**: The story is formatted for readability
        
        The entire process takes about 10-20 seconds depending on the complexity.
        """)
    
    # Function to handle button click with error handling
    def safe_generate_story(prompt):
        try:
            print(f"[DEBUG] safe_generate_story called with: '{prompt}'")
            return generate_story(prompt)
        except Exception as e:
            print(f"[ERROR] Exception in button handler: {e}")
            print(traceback.format_exc())
            return f"⚠️ Error occurred: {e}"
    
    tell_btn.click(
        safe_generate_story, 
        inputs=child_inp, 
        outputs=story_out
    )

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")
    
    print("[INFO] Starting Gradio interface...")
    demo.launch()
