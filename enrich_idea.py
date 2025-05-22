"""
enrich_idea.py – minimal helper to enrich a child's story idea
------------------------------------------------------------
Usage
-----

from enrich_idea import generate_enriched_idea

rich_idea = generate_enriched_idea("mom")
# ➜ "A courageous mom who discovers she can talk to animals
#    and sets off on a jungle adventure with her kids."

Feed `rich_idea` into your story prompt as the {idea} placeholder.
"""

import os
import openai

# Feel free to change the default model
_MODEL = "gpt-3.5-turbo"  # Changed to match the base.py model


def generate_enriched_idea(raw_idea: str, *, model: str | None = None) -> str:
    """
    Expand a terse or ambiguous idea into 1–2 lively, age-appropriate sentences.

    Parameters
    ----------
    raw_idea : str
        The child's original prompt (e.g. "dog", "space adventure with mom").
    model : str | None
        Override the default OpenAI chat-model if desired.

    Returns
    -------
    str
        An enriched premise **without** any prefix or quotes, ready for use in
        your story template.
    """
    raw_idea = raw_idea.strip()
    if not raw_idea:
        raise ValueError("The idea cannot be empty.")

    openai.api_key = os.getenv("OPENAI_API_KEY")
    chosen_model = model or _MODEL

    prompt = f"""
You are a children's creative-writing assistant.
The child's idea is: "{raw_idea}"

Expand it into ONE or TWO sentences that:
• keep the core topic intact,
• add colourful, child-friendly details (who, where, why),
• remain suitable for a 5-10-year-old,
• end with a period.

Return ONLY the enriched idea – no bullet points, prefixes, or quotes.
"""

    try:
        response = openai.chat.completions.create(
            model=chosen_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        # Return a simple enriched version as fallback
        return f"A magical adventure about {raw_idea} that teaches children about friendship and courage."
