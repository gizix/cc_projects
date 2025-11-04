# Claude Code Project Templates Repository

## Repository Purpose

This repository contains ready-to-use VSCode project templates optimized for Claude Code. Each template includes:

- Pre-configured CLAUDE.md files with framework-specific context and best practices
- Custom slash commands for common operations
- Specialized subagents for framework-specific tasks
- Agent skills for automated workflows
- Minimal framework scaffolding and setup instructions

## Working with This Repository

### When Creating New Templates

1. **Reference the knowledge base**: Review the saved memory `claude_code_best_practices` for comprehensive guidance on:
   - CLAUDE.md file structure and best practices
   - Slash command creation and syntax
   - Subagent design patterns
   - Skills development guidelines
   - Settings and hooks configuration

2. **Follow the template structure**:
   ```
   template-name/
   ├── README.md
   ├── CLAUDE.md
   ├── .claude/
   │   ├── settings.json
   │   ├── commands/
   │   ├── agents/
   │   └── skills/
   ├── .gitignore
   ├── .env.example
   └── [framework files]
   ```

3. **Ensure comprehensive coverage**:
   - 8-12 slash commands for common operations
   - 4-6 specialized subagents with single responsibilities
   - 2-4 skills for complex patterns
   - Detailed CLAUDE.md with framework conventions
   - Clear setup instructions in template README.md

4. **Test thoroughly**:
   - Open template in VSCode
   - Launch Claude Code
   - Test all commands, verify agents activate appropriately
   - Ensure skills trigger correctly
   - Validate all documentation is clear

### When Using Templates

Users will:
1. Download/clone the template folder
2. Open it in VSCode
3. Launch Claude Code
4. Follow the template's README.md for framework-specific setup

All Claude Code configurations are pre-loaded and ready to use.

## Repository Structure

- `README.md` - Main repository documentation for users
- `CLAUDE.md` - This file, context for working on this repository
- `.claude/` - Repository-level Claude Code configuration (if needed)
- `django-template/` - Django web development template
- `react-template/` - React + Vite + TypeScript frontend template
- `flask-template/` - Flask REST API backend template
- `tkinter-template/` - Tkinter desktop application template
- *(More templates to be added)*

## Code Style and Conventions

### For Template Creation

- **CLAUDE.md files**: Use clear markdown structure with descriptive headings
- **Slash commands**:
  - Use lowercase-with-hyphens for filenames
  - Always include `description` field in frontmatter
  - Document expected arguments in `argument-hint`
  - Use `$ARGUMENTS` or `$1`, `$2`, etc. for parameter substitution

- **Subagents**:
  - Use lowercase-with-hyphens for names
  - Write detailed, instruction-rich system prompts
  - Include "PROACTIVELY" in descriptions for automatic delegation
  - Restrict tools to only necessary capabilities

- **Skills**:
  - Directory-based structure with SKILL.md
  - Specific descriptions that include trigger scenarios
  - Optional supporting files (reference.md, examples/, templates/)
  - Use `allowed-tools` to restrict access appropriately

### Documentation Standards

- All templates must have comprehensive README.md files
- Include setup instructions with step-by-step procedures
- Provide examples of using commands, agents, and skills
- Link to official framework documentation
- Document any prerequisites or dependencies

## Available Knowledge

The following memories are available for reference:

- **claude_code_best_practices**: Comprehensive guide to Claude Code configuration including:
  - CLAUDE.md hierarchy and structure
  - Slash command syntax and patterns
  - Subagent design and configuration
  - Skills development guidelines
  - Settings files and hooks
  - Framework-specific template patterns

Access this knowledge by asking Claude Code questions about configuration patterns or by using the read_memory tool.

## Development Workflow

### Adding a New Template

1. Create template directory: `template-name/`
2. Create comprehensive CLAUDE.md with framework context
3. Add slash commands in `.claude/commands/`
4. Create specialized subagents in `.claude/agents/`
5. Develop skills in `.claude/skills/`
6. Add framework files (requirements, config, .gitignore)
7. Write detailed README.md with setup instructions
8. Test thoroughly with Claude Code
9. Update main repository README.md with new template listing

### Updating Existing Templates

1. Review framework updates and best practices
2. Update CLAUDE.md with new patterns or conventions
3. Add new commands/agents/skills as needed
4. Update framework files and dependencies
5. Test all configurations still work
6. Update template README.md if needed
7. Document changes in commit messages

## Quality Standards

All templates must:
- Work immediately upon opening in VSCode with Claude Code
- Have clear, comprehensive documentation
- Follow the standard template structure
- Include appropriate gitignore for framework
- Provide environment variable templates
- Test successfully with Claude Code
- Follow security best practices

## Future Templates

Planned templates:
- FastAPI (Python async APIs)
- Node/Express (JavaScript backend)
- Vue.js (frontend development)
- Next.js (React framework)
- Electron (cross-platform desktop apps)
- And more based on community requests

## Support and Contributions

- Issues: Report problems or request new templates via GitHub Issues
- Contributions: Follow standard structure and test thoroughly before submitting PRs
- Documentation: Keep all docs updated with template changes

---

**Note**: This repository is designed to make Claude Code immediately productive for common project types. Focus on practical, real-world configurations that developers will actually use.
