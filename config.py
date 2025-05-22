"""
Configuration settings for the bedtime story generator.
"""

# API Model Configurations
MODELS = {
    "v1": {
        "name": "gpt-4o-mini",
        "max_tokens": 3000,
        "temperature": 0.7,
    },
    "v2": {
        "name": "gpt-4.1-preview",
        "max_tokens": 4000,
        "temperature": 0.7,
    }
}

# System Prompts

# Story Generator Prompt
STORYTELLER_PROMPT = """
You are a master storyteller for children ages 5-10. Create an engaging, age-appropriate bedtime story 
based on the user's request. The story should:

1. Use vocabulary appropriate for ages 5-10
2. Have a clear beginning, middle, and end
3. Include positive messages or gentle lessons
4. Be engaging and spark imagination
5. Be approximately 500-800 words in length
6. Use descriptive but simple language
7. Include dialog between characters when appropriate

Avoid:
1. Scary or disturbing content
2. Complex vocabulary beyond a 10-year-old's understanding
3. Violence or mature themes
4. Overly complex plotlines

Format the story with clear paragraphs and appropriate spacing. Include a title at the beginning.
"""

# Judge Evaluation Prompt
JUDGE_PROMPT = """
You are an expert in children's literature and child development for ages 5-10. Evaluate the provided story 
based on the following criteria:

1. Age-Appropriateness (1-10): Is the vocabulary, themes, and content suitable for ages 5-10?
2. Engagement (1-10): How captivating and interesting is the story for children?
3. Structure (1-10): Does the story have a clear beginning, middle, and end?
4. Educational Value (1-10): Does the story teach a positive lesson or contain educational elements?
5. Clarity (1-10): Is the story easy to follow and understand?

For each criterion, provide:
- A score (1-10)
- Brief justification (1-2 sentences)
- Specific suggestion for improvement

Then provide an overall assessment (1-10) with 2-3 specific recommendations for improving the story.
Format your response as a structured evaluation report.
"""

# Revision Prompt
REVISION_PROMPT = """
You are a children's story editor helping improve a bedtime story for ages 5-10. 
Review the original story and the feedback provided, then create an improved version that addresses the feedback.

Focus on:
1. Implementing the specific recommendations from the judge
2. Maintaining the core elements and characters of the original story
3. Keeping the story at an appropriate length (500-800 words)
4. Ensuring vocabulary and themes remain age-appropriate

Your revised story should be a complete, standalone story incorporating all improvements.
"""

# Evaluation Criteria Parameters
EVALUATION_CRITERIA = {
    "age_appropriateness": {
        "weight": 0.25,
        "description": "Vocabulary, themes, and content suitable for ages 5-10"
    },
    "engagement": {
        "weight": 0.25,
        "description": "Story is captivating and interesting for children"
    },
    "structure": {
        "weight": 0.15,
        "description": "Clear beginning, middle, and end with logical flow"
    },
    "educational_value": {
        "weight": 0.15,
        "description": "Contains positive lessons or educational elements"
    },
    "clarity": {
        "weight": 0.20,
        "description": "Easy to follow and understand for the target age group"
    }
}

# Story Structure Templates
STORY_STRUCTURES = {
    "hero_journey": {
        "description": "A character faces a challenge, goes on an adventure, and returns transformed",
        "elements": [
            "Introduction of main character and setting",
            "Call to adventure or problem to solve",
            "Challenges and obstacles",
            "Climax where character faces biggest challenge",
            "Resolution and return with new knowledge"
        ]
    },
    "problem_solution": {
        "description": "A character encounters a problem and finds a creative solution",
        "elements": [
            "Introduction of character and everyday setting",
            "Problem arises that disrupts normal life",
            "Character tries various approaches to solve problem",
            "Character has insight or receives help",
            "Problem is resolved and lesson is learned"
        ]
    },
    "friendship_tale": {
        "description": "Characters learn about friendship, cooperation, or kindness",
        "elements": [
            "Introduction of characters who are different from each other",
            "Situation that brings characters together",
            "Conflict or misunderstanding between characters",
            "Resolution through communication or cooperation",
            "Strengthened friendship and lesson about relationships"
        ]
    },
    # New template: Mystery/Discovery
    "mystery_discovery": {
        "description": "Characters discover something mysterious and learn through exploration",
        "elements": [
            "Introduction of curious characters in familiar setting",
            "Discovery of something unusual or mysterious",
            "Investigation and gathering clues or information",
            "Moment of realization or understanding",
            "Sharing of knowledge and reflection on what was learned"
        ]
    },
    # New template: Personal Growth
    "personal_growth": {
        "description": "A character learns to overcome a personal limitation or fear",
        "elements": [
            "Introduction of character with a specific limitation, fear, or insecurity",
            "Situation that forces character to confront their limitation",
            "Initial struggle or failure when attempting to overcome the challenge",
            "Moment of self-discovery or new perspective",
            "Success in overcoming limitation and reflection on personal growth"
        ]
    },
    # New template: Fantasy Adventure
    "fantasy_adventure": {
        "description": "Characters journey through a magical world with fantastical elements",
        "elements": [
            "Introduction of ordinary characters and the magical element/world",
            "Entry into the fantasy world or acquisition of magical ability",
            "Exploration and wonder at the magical elements",
            "Challenge that requires both magical and non-magical solutions",
            "Resolution and return to normal life with new appreciation"
        ]
    },
    # New template: Nature Connection
    "nature_connection": {
        "description": "Characters connect with nature and learn about the environment",
        "elements": [
            "Introduction of characters and natural setting",
            "Encounter with an animal, plant, or natural phenomenon",
            "Learning experience about how nature works",
            "Challenge related to preserving or understanding nature",
            "Resolution that emphasizes harmony with the natural world"
        ]
    }
}

# Age-Appropriate Vocabulary Guidelines
VOCABULARY_GUIDELINES = {
    "5-7": {
        "sentence_length": "5-8 words on average",
        "paragraph_length": "2-3 sentences",
        "words_to_use": [
            "big", "small", "happy", "sad", "friend", "help", "play", "share",
            "kind", "brave", "love", "family", "fun", "learn", "grow"
        ],
        "words_to_avoid": [
            "complex", "sophisticated", "extraordinary", "melancholy", "intricate",
            "convoluted", "exacerbate", "facilitate", "preliminary", "substantial"
        ]
    },
    "8-10": {
        "sentence_length": "8-12 words on average",
        "paragraph_length": "3-5 sentences",
        "words_to_use": [
            "adventure", "discover", "curious", "imagine", "wonder", "create",
            "challenge", "solve", "explore", "journey", "mystery", "courage", "teamwork"
        ],
        "words_to_avoid": [
            "existential", "philosophical", "inconsequential", "unprecedented",
            "unequivocally", "disenfranchised", "disillusionment", "quintessential"
        ]
    }
}

# Default Generation Parameters
GENERATION_PARAMS = {
    "storyteller": {
        "temperature": 0.7,
        "max_tokens": 2500,
        "top_p": 1.0,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.3
    },
    "judge": {
        "temperature": 0.4,
        "max_tokens": 1500,
        "top_p": 1.0,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.2
    },
    "revision": {
        "temperature": 0.6,
        "max_tokens": 2500,
        "top_p": 1.0,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.3
    }
}