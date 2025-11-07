---
description: Create a new Python project with intelligent framework recommendation
argument-hint: [project-description]
allowed-tools: Read(*), Write(*), Bash(*), Grep(*), Task(*)
---

# New Python Project Command

This command helps you start a new Python project by intelligently recommending the best framework based on your project requirements.

## Usage Modes

### Interactive Mode (Recommended for New Users)
```
/new-python-project
```
Launches the interactive Python Framework Advisor that will:
1. Ask about your project goals
2. Gather requirements through conversation
3. Recommend the optimal Python framework
4. Optionally create the template for you

### Semi-Guided Mode (Quick Start)
```
/new-python-project Build a REST API for managing tasks
```
Start with a project description, then answer follow-up questions to refine the recommendation.

## How It Works

The command uses the **python-framework-advisor** agent to:
- Analyze your project requirements
- Consider project complexity, performance needs, your experience, and required features
- Recommend from existing templates: Django, Flask, FastAPI, Streamlit, Scrapy, Jupyter ML
- Suggest alternatives if a better framework exists (even without a template)
- Optionally hand off to template-creator to build your project

## Current Template Availability

Available Python templates:
- **Django**: Full-featured web framework with admin, ORM, auth
- **Flask**: Lightweight, flexible web framework
- **FastAPI**: Modern, fast async API framework
- **Streamlit**: Interactive data apps and dashboards
- **Scrapy**: Web scraping framework
- **Jupyter ML**: Machine learning experiments

## Command Execution

Based on how the user invoked this command:

- **If no arguments provided**: Launch the python-framework-advisor agent in full interactive mode to gather requirements from scratch.

- **If project description provided**: Launch the python-framework-advisor agent with the initial project description "$ARGUMENTS" and proceed with targeted follow-up questions.

---

You should now launch the **python-framework-advisor** agent to help the user with their Python project.

If the user provided a project description in `$ARGUMENTS`, include it when launching the agent:
- "Help the user create a Python project. Their initial description: $ARGUMENTS"

If no arguments were provided:
- "Help the user create a Python project by gathering their requirements interactively."
