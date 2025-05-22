"""
simplified_step_back.py - Fixed version that avoids list index errors completely
"""

import os
import openai
from typing import Dict, Any

def generate_step_back_query(original_query: str, api_key: str) -> str:
    """
    A simplified version that's guaranteed not to throw index errors
    """
    # Very basic prompt for testing
    prompt = f"Please reformulate this query: '{original_query}'"
    
    print(f"\n[DEBUG] Original query: '{original_query}'")
    print(f"[DEBUG] API key (first/last 4 chars): {api_key[:4]}...{api_key[-4:]}")
    
    # Use fallback in case of any errors
    fallback_response = f"Tell a children's story about {original_query}"
    
    try:
        # Initialize the client
        client = openai.OpenAI(api_key=api_key)
        print("[DEBUG] Created OpenAI client")
        
        # Create chat completion with error handling
        try:
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
            
            print("[DEBUG] Received response from API")
            
            # Get content with safe navigation
            content = None
            
            # Try to access nested properties safely
            if hasattr(response, 'choices') and response.choices:
                print(f"[DEBUG] Response has {len(response.choices)} choices")
                
                choice = response.choices[0]
                if hasattr(choice, 'message') and choice.message:
                    print("[DEBUG] First choice has message")
                    
                    if hasattr(choice.message, 'content'):
                        print("[DEBUG] Message has content")
                        content = choice.message.content.strip()
                        print(f"[DEBUG] Content: '{content[:30]}...'")
            
            # Return content if we got it, otherwise fallback
            if content:
                return content
            else:
                print("[DEBUG] Couldn't extract content, using fallback")
                return fallback_response
                
        except Exception as e:
            print(f"[DEBUG] API request failed: {e}")
            return fallback_response
            
    except Exception as e:
        print(f"[DEBUG] Client creation failed: {e}")
        return fallback_response

# Simple test function
if __name__ == "__main__":
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        exit(1)
        
    # Test the function
    result = generate_step_back_query("a brave little mouse", api_key)
    print(f"\nResult: {result}")
