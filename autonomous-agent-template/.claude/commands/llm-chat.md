---
description: Interactive streaming LLM chat (Azure OpenAI / OpenAI-compatible)
argument-hint: "[--model gpt-4o] [--system-prompt 'You are...']"
---

Launch an interactive streaming LLM chat session in the terminal.

```bash
uv run agent llm chat $ARGUMENTS
```

**Options:**
- `--model <name>`: Override the default model
- `--system-prompt <text>`: Set a custom system prompt

**Provider selection (automatic):**
1. Azure OpenAI (if `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` set)
2. OpenAI (if `OPENAI_API_KEY` set)
3. Local/custom (if `OPENAI_BASE_URL` set, e.g. Ollama or LM Studio)

**Examples:**
```bash
# Basic chat
uv run agent llm chat

# Custom system prompt
uv run agent llm chat --system-prompt "You are a Python code reviewer. Be concise."

# Use Ollama local model
OPENAI_BASE_URL=http://localhost:11434/v1 uv run agent llm chat --model llama3.2
```

Type `exit` or press `Ctrl+C` to quit.

**Web UI chat:** `/ui` then navigate to LLM Chat for streaming browser-based interface.
