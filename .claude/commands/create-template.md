---
description: Create a new project template with Claude Code configuration (interactive or expert mode)
argument-hint: [template-name] [framework-type]
allowed-tools: Read(*), Write(*), Bash(*), Grep(*), Task(*)
---

Create a comprehensive project template with Claude Code configuration. Supports both beginner-friendly interactive mode and expert direct mode.

## Usage Modes

### Beginner Mode (Interactive) - RECOMMENDED

```
/create-template
```

Launches the template-wizard agent which will:
- Ask beginner-friendly questions about your project
- Recommend appropriate frameworks based on your needs
- Explain concepts and trade-offs
- Guide you through all decisions
- Show preview of what will be created
- Hand off to template-creator with full context

**Perfect for**:
- First-time template creators
- Uncertain about framework choice
- Want to understand options
- Need guidance on features

### Expert Mode (Direct)

```
/create-template <template-name> <framework-type>
```

**Arguments**:
- $1: Template name (e.g., "react-template", "fastapi-template")
- $2: Framework/technology type (e.g., "React", "FastAPI", "Vue", "Node/Express")

Skips interactive wizard and proceeds directly to creation.

**Perfect for**:
- Experienced template creators
- Know exactly what you want
- Creating similar templates quickly

## Related Commands

### For Python Projects: `/new-python-project`

If you're specifically working with **Python**, consider using `/new-python-project` instead:

```
/new-python-project [project-description]
```

This specialized command:
- ✅ Focuses exclusively on Python frameworks
- ✅ Provides intelligent framework recommendations
- ✅ Considers project complexity, performance needs, and your experience
- ✅ Recommends from: Django, Flask, FastAPI, Streamlit, Scrapy, Jupyter ML
- ✅ Asks targeted questions about Python-specific requirements
- ✅ Can automatically hand off to create the recommended template

**Use `/new-python-project` when**:
- Building any Python-based project
- Unsure which Python framework to choose
- Want framework recommendation before template creation

**Use `/create-template` when**:
- Working with non-Python frameworks (React, Vue, Node, etc.)
- You already know the exact framework you want
- Creating templates for any technology stack

## Process Flow

### Interactive Mode Process

1. **Launch template-wizard agent**
   - User answers beginner-friendly questions
   - Wizard recommends frameworks
   - Wizard gathers all requirements
   - Wizard shows preview
   - User confirms

2. **Wizard hands off to template-creator**
   - Provides comprehensive context
   - Includes all user preferences
   - Specifies template depth (minimal/standard/comprehensive)
   - Lists required features

3. **Template creation proceeds automatically**
   - See Expert Mode Process below

### Expert Mode Process

When arguments are provided OR after wizard handoff:

1. **Gather Requirements** (if not from wizard)

Ask the user for details:
- Framework version to target
- Key features to include (API, auth, testing, etc.)
- Development tools preferred
- Package manager (npm, pip, cargo, etc.)
- Template depth (minimal/standard/comprehensive)

2. **Research Framework Best Practices**

Use the framework-researcher agent to:
- Research current best practices for the framework
- Identify common project structures
- Find popular packages and tools
- Understand security considerations
- Learn testing patterns
- **NEW**: Get framework recommendations if comparing options

3. **Learn from Existing Templates**

Use template-blueprints skill to:
- Analyze similar existing templates
- Extract relevant patterns
- Identify common command structures
- Reference agent templates
- Use documentation templates

4. **Create Template Structure**

Use the template-creator agent to:
- Create directory structure following template-structure pattern
- Generate template-specific CLAUDE.md using documentation templates
- Create README.md with usage instructions
- Set up .gitignore for the framework
- Create setup_instructions.md

5. **Generate Claude Code Configuration**

Use common-commands.json and common-agents.json patterns:

**Commands** (based on template depth):
- Minimal: 5-6 essential commands
- Standard: 10-12 comprehensive commands
- Comprehensive: 12-15 commands including CI/CD

**Agents** (based on template depth):
- Minimal: 3 core agents (security, expert, test)
- Standard: 5-6 specialized agents
- Comprehensive: 6-8 agents with advanced roles

**Skills** (based on template depth):
- Minimal: 1-2 basic skills
- Standard: 3-4 pattern libraries
- Comprehensive: 4-5 complete skills

6. **Create Framework Files**

Generate:
- Package/dependency file (package.json, requirements.txt, etc.)
- Environment variable template (.env.example)
- Configuration files (tsconfig.json, pytest.ini, etc.)
- Setup instructions (setup_instructions.md)
- Claude Code settings.json with appropriate hooks

7. **Validate Template**

Use template-validator agent to ensure:
- All required files present
- Claude Code configuration valid
- Documentation complete
- Structure follows standards
- Commands have proper frontmatter
- Agents have activation triggers
- Skills have clear descriptions

8. **Update Repository**

- Add template to main README.md
- Update CLAUDE.md if needed
- Display summary of created template
- Provide next steps

## Decision Logic

```
IF no arguments provided:
    → Launch template-wizard agent (interactive mode)
    → Wizard gathers all requirements
    → Wizard hands off to template-creator with context
    → Proceed with expert flow using wizard context

ELSE IF both arguments provided:
    → Skip wizard
    → Proceed directly with expert mode
    → Ask for additional details as needed

ENDIF
```

## Example Usage

### Beginner Example

```bash
# Launch interactive wizard
/create-template

# Wizard asks questions...
> What type of project are you building?
  → REST API / Backend

> I recommend FastAPI or Flask. FastAPI is modern...
  → FastAPI sounds good

> Do you need database, auth, real-time?
  → Database: Yes, Auth: Yes, Real-time: No

> How comprehensive should the template be?
  → Standard template

# Wizard shows preview...
# User confirms...
# Template is created automatically!
```

### Expert Example

```bash
# Create directly if you know what you want
/create-template vue-template Vue

# You'll be asked for:
# - Version (Vue 3)
# - Key features (routing, state management)
# - Template depth (standard)
# Then creation proceeds automatically
```

## New Features

✅ **Interactive wizard** for beginners
✅ **Framework recommendations** based on requirements
✅ **Template depth selection** (minimal/standard/comprehensive)
✅ **Pattern reuse** from existing templates
✅ **Preview before creation**
✅ **Educational explanations** throughout
✅ **Preset configurations** for quick starts
✅ **Template quality validation** built-in

## Resources Used

This command leverages:
- **template-wizard** agent (NEW) - Interactive guidance
- **framework-researcher** agent - Framework research
- **template-creator** agent - Template construction
- **template-validator** agent - Quality assurance
- **template-blueprints** skill (NEW) - Pattern library
- **claude-config-generator** skill - Config generation
- **template-structure** skill - Directory organization

## Notes

- **Recommendation**: Use interactive mode (`/create-template`) for best experience
- Reference `claude_code_best_practices` memory for detailed patterns
- Follow the structure established in django-template, react-template, flask-template
- Ensure comprehensive documentation for all three docs (README, CLAUDE, setup)
- Test all commands and agents work correctly
- Use presets from template-blueprints for guidance on scope

## Tips

- **First template?** Use interactive mode
- **Similar to existing?** Check template-blueprints reference.md for patterns
- **Unsure about scope?** Choose "Standard template" - it matches existing quality templates
- **Need minimal starter?** Select "Minimal" in wizard or specify when asked
- **Want everything?** Choose "Comprehensive" for CI/CD, monitoring, advanced features
