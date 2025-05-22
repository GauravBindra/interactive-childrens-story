# Bedtime Story Generator - Implementation Plan

## Versions
- V1: GPT-4o mini for story generation and judging
- V2: GPT-4.1 with DALL-E image generation

## Core Components to Implement
1. User Interface - Command line interface
2. Prompt Builder - Convert requests to structured prompts
3. Story Generator - Generate initial story draft
4. Story Output Buffer - Hold draft for user and other modules
5. Judge/Evaluator - Critique story against evaluation criteria
6. Feedback Aggregator - Combine judge and user feedback
7. Revision Prompt Builder - Create prompt for story refinement
8. Loop Controller - Manage iteration process

## Supporting Components
- Config/Prompt Library - System prompts and parameters
- Illustration Generator - Create story illustrations (V2 only)

## Files to Create
- `main_v1.py` - GPT-4o mini implementation
- `main_v2.py` - GPT-4.1 with image generation
- `storyteller.py` - Story generation logic
- `judge.py` - Evaluation system
- `illustrator.py` - Image generation (V2)
- `templates.py` - Story patterns and prompts
- `utils.py` - Helper functions
- `config.py` - Configuration settings
- `block_diagram.md` - System flow visualization

## Implementation Priorities
1. Core story generation pipeline
2. Story evaluation and refinement
3. User interface with feedback mechanism
4. Image generation integration (V2)