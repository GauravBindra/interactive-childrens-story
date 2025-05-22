"""
Simple test script to diagnose OpenAI API issues
"""
import os
import sys
from openai import OpenAI

def test_openai_call():
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
        
    print(f"\n[DEBUG] Using API key: {api_key[:5]}...{api_key[-4:]}")
    print("[DEBUG] Initializing OpenAI client")
    
    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        
        # Test simple completion
        print("[DEBUG] Sending test request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use this specific model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello world."},
            ],
            temperature=0.7,
        )
        
        # Debug response structure
        print("\n[DEBUG] Response received")
        print(f"[DEBUG] Response type: {type(response)}")
        print(f"[DEBUG] Response dir: {dir(response)}")
        print(f"[DEBUG] Has 'choices' attribute: {hasattr(response, 'choices')}")
        
        if hasattr(response, 'choices'):
            print(f"[DEBUG] Choices type: {type(response.choices)}")
            print(f"[DEBUG] Number of choices: {len(response.choices)}")
            
            if len(response.choices) > 0:
                print(f"[DEBUG] First choice type: {type(response.choices[0])}")
                print(f"[DEBUG] First choice dir: {dir(response.choices[0])}")
                print(f"[DEBUG] First choice has 'message': {hasattr(response.choices[0], 'message')}")
                
                if hasattr(response.choices[0], 'message'):
                    print(f"[DEBUG] Message type: {type(response.choices[0].message)}")
                    print(f"[DEBUG] Message dir: {dir(response.choices[0].message)}")
                    print(f"[DEBUG] Message has 'content': {hasattr(response.choices[0].message, 'content')}")
                    
                    if hasattr(response.choices[0].message, 'content'):
                        content = response.choices[0].message.content
                        print(f"[DEBUG] Content: {content}")
                    else:
                        print("[DEBUG] No content attribute found!")
                else:
                    print("[DEBUG] No message attribute found!")
            else:
                print("[DEBUG] Choices list is empty!")
        else:
            print("[DEBUG] No choices attribute found!")
            
        print("\nTest completed successfully")
        
    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {e}")
        print(f"[ERROR] Exception type: {type(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_openai_call()
