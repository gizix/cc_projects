---
name: llm-prompt-design
description: Provides PromptBuilder usage, JSON-mode structured output, and template variable sanitization when writing LLM task prompts. Activates when user writes system prompts or designs LLM inference tasks.
allowed-tools: Read, Write, Edit
---

You provide prompt engineering patterns optimised for the Autonomous Agent LLM stack.

## When to Activate

- User is writing a system prompt
- User configures an `llm_inference` scheduled task
- User asks about JSON-mode structured output
- User needs multi-turn conversation patterns
- User asks "how do I make the LLM return X format"

## PromptBuilder API

```python
from agent.llm.prompt import PromptBuilder

# Simple single-turn
messages = (
    PromptBuilder()
    .system("You are a concise technical writer.")
    .user("Explain async/await in one sentence.")
    .build()
)

# Multi-turn conversation
messages = (
    PromptBuilder()
    .system("You are a helpful assistant.")
    .user("What is the capital of France?")
    .assistant("Paris.")
    .user("What is its population?")
    .build()
)

# Template with variable substitution (sanitized — no injection)
template = "Summarise this {language} code:\n\n{code}"
content = PromptBuilder().render(template, language="Python", code=user_code)
messages = PromptBuilder().system("You are a code reviewer.").user(content).build()
```

## JSON-Mode Structured Output

Request JSON output for predictable parsing:

```python
from agent.llm.client import LLMClient
from agent.llm.prompt import PromptBuilder

client = LLMClient()

messages = (
    PromptBuilder()
    .system(
        "You are a data extractor. "
        "Always respond with valid JSON matching the requested schema."
    )
    .user(
        'Extract the following fields from this text and return JSON: '
        '{"name": string, "date": ISO date string, "amount": float}\n\n'
        + user_text
    )
    .build()
)

result = client.structured(messages)
# result is a dict: {"name": "...", "date": "...", "amount": 123.45}
```

## Effective System Prompt Patterns

### For scheduled automation tasks
```
You are an automated [role] agent.
Your responses will be processed programmatically — be concise and structured.
Always respond in [format].
Do not add explanations unless explicitly requested.
```

### For daily briefings
```
You are a daily briefer. Given today's date ({date}), provide:
1. A one-sentence summary of the day's context
2. Three actionable priorities
3. Any relevant reminders

Be direct. Use bullet points. Maximum 150 words.
```

### For JSON extraction
```
You extract structured data from text.
Output ONLY valid JSON. No markdown, no explanation.
Schema: {schema}
If a field cannot be determined, use null.
```

### For code review tasks
```
You are a senior Python engineer.
Review the following code for: correctness, security, performance, style.
Format your response as:
- ISSUES: [list of issues, or "none"]
- SUGGESTIONS: [list of improvements]
- VERDICT: APPROVE | REQUEST_CHANGES
```

## LLMTask Config Patterns

```json
// Daily morning briefing
{
  "system_prompt": "You are a concise daily briefer. Maximum 100 words.",
  "user_prompt": "Provide a brief morning briefing for today.",
  "temperature": 0.3,
  "max_tokens": 200
}

// Code quality check (chain with file reading task)
{
  "system_prompt": "You are a Python code reviewer. Be concise.",
  "user_prompt": "Review this code for security issues: {code}",
  "temperature": 0.1,
  "max_tokens": 500
}

// Creative content generation
{
  "system_prompt": "You are a creative writer.",
  "user_prompt": "Write a haiku about autonomous agents.",
  "temperature": 0.9,
  "max_tokens": 50
}
```

## Prompt Variable Sanitization

The `render()` method sanitizes user-provided values to prevent format string injection:

```python
# SAFE — render() escapes braces in values
pb = PromptBuilder()
user_input = "some {malicious} input {trying} injection"
content = pb.render("Process this: {input}", input=user_input)
# → "Process this: some {malicious} input {trying} injection"
# Curly braces in values are escaped, not interpreted as template vars

# UNSAFE — direct f-string interpolation
bad = f"Process this: {user_input}"  # Don't do this
```

## Token Budget Guidelines

| Task | Recommended max_tokens |
|------|----------------------|
| Short answers / classification | 50-100 |
| Summaries / briefings | 200-500 |
| Code review | 300-800 |
| Document generation | 1000-2000 |
| Complex analysis | 2000+ |

Keep `temperature` low (0.1-0.3) for factual/structured tasks, higher (0.7-0.9) for creative tasks.
