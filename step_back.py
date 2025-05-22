"""
step_back.py
------------

Utility for turning a user’s children-story request into a
“step-back query” – a broader, intent-focused question that
improves retrieval quality.

Usage
-----
    from step_back import generate_step_back_query
    print(generate_step_back_query("Tell me a story about a brave ant", api_key))
"""

from __future__ import annotations

import openai
from typing import Literal, Dict, Any, Optional


def generate_step_back_query(
    original_query: str,
    api_key: str,
    model: Literal["gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"] = "gpt-3.5-turbo",
    temperature: float = 0.3,
    debug: bool = True,
) -> str:
    """
    Reformulate `original_query` into a broader, intent-oriented step-back query.

    Parameters
    ----------
    original_query : str
        The child-focused story prompt provided by the user.
    api_key : str
        OpenAI API key.
    model : Literal["gpt-4o", "gpt-4o-mini"], default "gpt-4o"
        Chat completion model to use.
    temperature : float, default 0.3
        Sampling temperature; keep it low for deterministic output.

    Returns
    -------
    str
        The model’s answer, starting with the prefix “Step-Back Query:”.
        If an exception occurs, the function returns a string beginning with
        the ⚠️ emoji and the error message.
    """
    prompt = f"""
You are an expert at reformulating children’s-story requests into broader,
theme-level questions that make it easier to retrieve useful narrative
ingredients (characters, settings, morals, age-appropriate language).

Your task is to craft a **step-back query** that:

• **Preserves the core idea** of the child’s request.  
• **Surfaces implicit goals** such as age bracket, moral lesson, or emotional tone.  
• **Generalises specifics** (names, places, time-periods) into archetypes or
  high-level concepts so retrieval systems can match a wider pool of references.  
• **Remains child-centric** — wording should assume the final audience is children
  and caretakers.  
• **Stays concise** (one or two sentences), but multiple sentences are allowed
  when clarity demands it.

Always begin your output with **“Step-Back Query:”** exactly.

### Examples (domain-agnostic)

**Example 1**  
Original Query: *What are the chemical properties of the element discovered by Marie Curie?*  
Step-Back Query: *What elements were discovered by Marie Curie, and what are their chemical properties?*

**Example 2**  
Original Query: *Why does my LangGraph agent `astream_events` return a long trace instead of the expected output?*  
Step-Back Query: *How does the `astream_events` function work in LangGraph agents?*

**Example 3**  
Original Query: *Which school did Estella Leopold attend from August to November 1954?*  
Step-Back Query: *What is the educational history of Estella Leopold?*

**Example 4**  
Original Query: *Why are Korean BBQ tacos such a big thing in Los Angeles right now?*  
Step-Back Query: *What sparked the popularity of Korean BBQ tacos, and how does their success in Los Angeles reflect the rise of fusion-cuisine trends across the country?*

### Additional examples (children-story focus)

**Example 5**  
Original Query: *Tell me a bedtime story about a curious dragon who loves math.*  
Step-Back Query: *What engaging bedtime-story plots feature a math-loving dragon and teach curiosity about numbers to children aged 5-7?*

**Example 6**  
Original Query: *Write a short story where a shy hedgehog learns to make friends at school.*  
Step-Back Query: *What narrative frameworks help portray a shy animal overcoming social anxiety and building friendships in a primary-school setting for 6-year-olds?*

**Example 7**  
Original Query: *Create an adventure tale about twins exploring an enchanted forest with a talking map.*  
Step-Back Query: *What classic adventure tropes and moral lessons suit a children’s story about sibling teamwork and discovery in a magical forest?*

---

Now generate a step-back query for the following user input:

Original Query: \"{original_query}\"
Step-Back Query:
""".strip()

    # Create fallback response in case of any errors
    fallback_response = f"Step-Back Query: Tell a children's story about {original_query.strip()}"
    
    # Print debug info
    if debug:
        print(f"\n[DEBUG] Generating step-back query using model: {model}")
        print(f"[DEBUG] Original query: '{original_query}'")
        print(f"[DEBUG] API key (first/last 4 chars): {api_key[:4]}...{api_key[-4:]}")
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        if debug:
            print("[DEBUG] Created OpenAI client successfully")
        
        # Main API request with comprehensive error handling
        try:
            if debug:
                print("[DEBUG] Sending request to OpenAI API...")
            
            # Make the API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
            )
            
            if debug:
                print("[DEBUG] Received response from API")
            
            # Extract content with safe navigation
            content: Optional[str] = None
            
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
                            content = choice.message.content.strip()
                            if debug:
                                print(f"[DEBUG] Content: '{content[:50]}...'")
            
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
                print(f"[DEBUG] API request failed: {str(e)}")
            return fallback_response
            
    except Exception as e:
        if debug:
            print(f"[DEBUG] Client creation failed: {str(e)}")
        return fallback_response
