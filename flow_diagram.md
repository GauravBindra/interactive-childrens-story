# Interactive Bedtime Stories - Flow Diagram

## System Overview
```
┌─────────────────────────────────────────────────────────────────────┐
│                    INTERACTIVE BEDTIME STORIES                      │
│                         Main Features:                              │
│  • 3-Scene Story Generation  • Voice Narration (4 voices)         │
│  • Story Evaluation (Judge)  • Educational Facts (Learn)           │
│  • Story Poster Generation   • Feedback & Revision                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Main Flow Diagram

```mermaid
graph TD
    Start([User Opens App]) --> Input[Enter Story Idea]
    Input --> Category[Select Category<br/>7 Options]
    Category --> StartBtn{Click Start Story}
    
    StartBtn -->|Empty Input| Warning[Show Warning Message]
    Warning --> Input
    
    StartBtn -->|Valid Input| Scene1[Generate Scene 1<br/>~150 words]
    Scene1 --> Display1[Display Scene 1<br/>with Emojis]
    Display1 --> Options1[Show 2 Choice Buttons]
    Display1 --> Features1[Enable Features:<br/>• Narrate<br/>• Learn Something<br/>• Feedback]
    
    Options1 --> Choice1{User Chooses<br/>Option 1 or 2}
    Features1 --> SideFeatures1{Optional Actions}
    
    Choice1 --> Scene2[Generate Scene 2<br/>Based on Choice]
    Scene2 --> Display2[Display Scenes 1+2]
    Display2 --> Options2[Show 2 New Choices]
    Display2 --> Features2[Features Still Available]
    
    Options2 --> Choice2{User Chooses<br/>Option 1 or 2}
    Features2 --> SideFeatures2{Optional Actions}
    
    Choice2 --> Scene3[Generate Scene 3<br/>Story Conclusion]
    Scene3 --> Display3[Display Complete Story<br/>with 'The End!']
    Display3 --> FinalFeatures[Enable Final Features:<br/>• Judge Story<br/>• Display Poster<br/>• Narrate<br/>• Learn Something]
    
    FinalFeatures --> EndActions{User Actions}
    EndActions -->|Judge| JudgeStory[Evaluate Story<br/>3 Metrics]
    EndActions -->|Poster| GeneratePoster[Create DALL-E 3<br/>Story Illustration]
    EndActions -->|New Story| Reset[Clear Everything<br/>Start Over]
    
    Reset --> Input
```

## Feature Flows

### 1. Narration Feature Flow
```mermaid
graph LR
    NarrateBtn[Click Listen to Scene] --> VoiceSelect[Select Voice:<br/>• Dad (fable)<br/>• Mom (shimmer)<br/>• Sister (nova)<br/>• Grandad (onyx)]
    VoiceSelect --> GenerateTTS[Generate Audio<br/>with Selected Voice]
    GenerateTTS --> PlayAudio[Auto-play Narration<br/>with Speed Adjustment]
    
    subgraph Speed Settings
        Dad[Dad: 0.9x]
        Mom[Mom: 0.9x]
        Sister[Sister: 1.1x]
        Grandad[Grandad: 0.8x]
    end
```

### 2. Learn Something Feature Flow
```mermaid
graph LR
    LearnBtn[Click Learn Something] --> ExtractTerm[Extract Educational Term<br/>Using Smart Heuristics]
    ExtractTerm --> RareWord{Found Rare<br/>Non-Name Word?}
    RareWord -->|Yes| GetFact[Generate Child-Friendly<br/>3-Line Fact]
    RareWord -->|No| LLMFallback[Ask LLM for<br/>Educational Term]
    LLMFallback --> GetFact
    GetFact --> TTSFact[Convert to Audio<br/>Mom's Voice @ 0.95x]
    TTSFact --> PlayFact[Auto-play Educational Fact]
```

### 3. Story Judge Feature Flow
```mermaid
graph LR
    JudgeBtn[Click Judge Story<br/>Available After Scene 3] --> Evaluate[Evaluate on 3 Metrics:<br/>1. Age Appropriateness<br/>2. Ease of Reading<br/>3. Clarity of Moral]
    Evaluate --> Scores[Generate Scores 1-10<br/>with Explanations]
    Scores --> Report[Display Evaluation Report<br/>with Overall Score]
```

### 4. Feedback Feature Flow
```mermaid
graph LR
    FeedbackBox[Enter Feedback] --> ApplyBtn[Click Apply Feedback]
    ApplyBtn --> Revise[Regenerate Current Scene<br/>with Feedback Applied]
    Revise --> UpdateDisplay[Update Story Display]
    UpdateDisplay --> SameOptions{Scene < 3?}
    SameOptions -->|Yes| ShowChoices[Show Updated Choices]
    SameOptions -->|No| ShowEnd[Show Story End<br/>Enable Final Features]
```

### 5. Poster Generation Flow
```mermaid
graph LR
    PosterBtn[Click Display Poster<br/>After Story Complete] --> Extract[Extract Story Essence<br/>200 chars max]
    Extract --> GenerateImage[DALL-E 3 API Call<br/>1024x1024px]
    GenerateImage --> NoText[Prompt Includes:<br/>'No text, visual only']
    NoText --> Display[Display Story Poster]
```

## State Management
```
State Object = {
    scene_no: 1-3,              // Current scene number
    scenes: [scene1, scene2...], // Array of generated scenes
    idea: "user's input",        // Original story idea
    category: "selected category" // Story category
}
```

## Component Visibility Rules

| Component | Scene 1 | Scene 2 | Scene 3 | After Reset |
|-----------|---------|---------|---------|-------------|
| Choice Buttons | ✓ | ✓ | ✗ | ✗ |
| Feedback | ✓ | ✓ | ✓ | ✗ |
| Narrate | ✓ | ✓ | ✓ | ✗ |
| Learn | ✓ | ✓ | ✓ | ✗ |
| Judge | ✗ | ✗ | ✓ | ✗ |
| Poster | ✗ | ✗ | ✓ | ✗ |
| Voice Selector | ✓ | ✓ | ✓ | ✗ |

## Story Generation Parameters
- Model: GPT-4o-mini
- Temperature: 0.4
- Max tokens: 600 per scene
- Scene length: ~150 words each
- Total story: ~450-500 words

## Categories Available
1. Animal Adventures
2. Fantasy & Magic
3. Friendship & Emotional Growth
4. Mystery & Problem-Solving
5. Humor & Silly Situations
6. Science & Space Exploration
7. Values & Morals (Fables)

## Audio/Visual Features
- **TTS Voices**: 4 character options with different speeds
- **Image Generation**: DALL-E 3, no text in images
- **Audio Formats**: MP3 for narration and facts
- **Auto-play**: Enabled for both narration and educational facts