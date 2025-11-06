# Claude Code Project Templates

A curated collection of ready-to-use VSCode project templates optimized for Claude Code. Each template comes pre-configured with project-specific context, custom commands, specialized agents, and skills to accelerate development workflows.

## What is This Repository?

This repository provides production-ready project scaffolding with comprehensive Claude Code configurations for different frameworks and project types. Instead of configuring Claude Code from scratch for every new project, simply clone a template and start building immediately.

## How to Use These Templates

1. **Choose a Template**: Browse the available templates below and select one matching your project type
2. **Download**: Clone this repository or download a specific template folder
3. **Open in VSCode**: Navigate to the template directory and open it in VSCode
4. **Start Claude Code**: Launch Claude Code within the project directory
5. **Begin Development**: All commands, agents, and context are pre-configured and ready to use

### Quick Start Example

```bash
# Clone the repository
git clone https://github.com/yourusername/cc-templates.git
cd cc-templates

# Use the Django template
cd django-template

# Open in VSCode (Windows)
code .

# Follow the template's README.md for framework-specific setup
```

## Available Templates

### Django Web Development Template

**Location**: `django-template/`

A comprehensive Django project template with:
- Pre-configured CLAUDE.md with Django best practices and conventions
- 10 custom slash commands for common Django tasks (migrations, testing, app creation)
- 5 specialized subagents (security review, ORM optimization, test writing, DRF, migrations)
- 3 skills for Django patterns, DRF serializers, and model validation
- Starter framework files (requirements.txt, .env.example, .gitignore)
- Detailed setup and usage documentation

**Best For**: Django REST APIs, full-stack Django applications, Django + HTMX projects

See `django-template/README.md` for detailed usage instructions.

---

### React + Vite + TypeScript Template

**Location**: `react-template/`

A modern React development template featuring:
- Vite 6 for lightning-fast dev server and optimized builds
- React 18 with TypeScript 5 for type-safe development
- TanStack Query (React Query) for powerful data fetching and caching
- Zustand for lightweight, flexible state management
- Vitest + React Testing Library for comprehensive testing
- ESLint + Prettier for code quality and consistent formatting
- 12 custom slash commands (/dev, /build, /test, /lint, /create-component, etc.)
- 6 specialized agents (security, performance, testing, React expert, Query expert, accessibility)
- 3 skills for custom hooks, component patterns, and data fetching patterns
- Complete TypeScript configurations and build tooling
- Comprehensive documentation and setup instructions

**Best For**: Modern React SPAs, React + REST API projects, TypeScript-first applications

See `react-template/README.md` for detailed usage instructions.

---

### Flask REST API Template

**Location**: `flask-template/`

A production-ready Flask backend template featuring:
- Flask 3.x with Application Factory pattern and Blueprint-based architecture
- JWT authentication with Flask-JWT-Extended for secure API access
- SQLAlchemy ORM with Flask-Migrate for database management
- Marshmallow schemas for request/response serialization and validation
- Service Layer pattern for clean business logic separation
- Pytest testing framework with comprehensive fixtures
- Docker support with docker-compose for easy deployment
- Code quality tools: Black, flake8, isort, mypy
- 11 custom slash commands (/run, /test, /db-migrate, /create-blueprint, etc.)
- 6 specialized agents (security, API optimization, testing, schema expert, migrations, blueprints)
- 4 skills for Flask patterns, REST API generation, auth systems, and database validation
- Complete example implementation with User auth system and CRUD operations
- Comprehensive configuration and environment templates

**Best For**: REST APIs, microservices, backend services, API-first applications

See `flask-template/README.md` for detailed usage instructions.

---

### Tkinter Desktop Application Template

**Location**: `tkinter-template/`

A modern Python desktop application template with:
- Python 3.13+ with modern type hints and async support
- ttkbootstrap for modern UI themes (20+ professional themes available)
- MVC architecture with observer pattern for clean separation of concerns
- uv package manager for lightning-fast dependency management
- PyInstaller for building standalone executables (Windows, macOS, Linux)
- Pytest with GUI testing utilities for comprehensive test coverage
- Code quality tools: ruff (linting/formatting), mypy (type checking)
- Form validation utilities with real-time feedback
- Config management with JSON persistence
- Thread-safe background operations for responsive UIs
- 10 custom slash commands (/dev, /test, /build, /new-view, /new-dialog, etc.)
- 5 specialized agents (Tkinter expert, GUI security, performance, testing, threading)
- 3 skills for MVC scaffolding, dialog generation, and form validation
- Complete example implementation with Todo list app demonstrating best practices
- Detailed setup and architecture documentation

**Best For**: Desktop applications, GUI tools, standalone utilities, cross-platform applications

See `tkinter-template/README.md` for detailed usage instructions.

---

### Streamlit Data Application Template

**Location**: `streamlit-template/`

A production-ready Streamlit application template featuring:
- Streamlit 1.51.0+ with modern Python 3.13.9+ for interactive data applications
- SQLAlchemy ORM with Alembic migrations for database management
- streamlit-authenticator for user authentication and session management
- httpx for async API integration with retry logic and error handling
- Plotly and Altair for interactive data visualizations
- Pytest with Streamlit AppTest for comprehensive component testing
- Code quality tools: Ruff (linting/formatting), Black, isort, mypy
- Pre-commit hooks for automated code quality checks
- Docker and docker-compose for development and production deployment
- 12 custom slash commands (/run, /test, /lint, /create-page, /create-component, etc.)
- 6 specialized agents (Streamlit expert, data viz optimizer, security reviewer, database architect, test generator, API integrator)
- 4 skills for Streamlit patterns, caching optimization, authentication systems, and database operations
- Complete example implementation with multi-page app structure
- Comprehensive configuration templates for secrets, environment variables, and deployment

**Best For**: Data dashboards, ML model interfaces, analytics applications, interactive data tools

See `streamlit-template/README.md` for detailed usage instructions.

---

### FastAPI REST API Template

**Location**: `fastapi-template/`

A production-ready FastAPI backend template featuring:
- FastAPI 0.115.x with modern async patterns and automatic OpenAPI documentation
- Async SQLAlchemy 2.0 with Alembic migrations for database management
- JWT authentication with OAuth2 password flow for secure API access
- Repository pattern with service layer for clean architecture and testability
- Pydantic v2 for request/response validation and settings management
- Pytest with async support and in-memory SQLite for fast testing
- Docker with multi-stage builds and docker-compose for PostgreSQL
- uv package manager for ultra-fast dependency management
- Code quality tools: Ruff (linting/formatting), MyPy (strict type checking), pre-commit hooks
- 10 custom slash commands (/dev, /test, /migrate, /format, /docker-up, etc.)
- Complete example implementation with User authentication and CRUD operations
- Comprehensive type hints with MyPy strict mode throughout
- Health check endpoints and proper error handling
- CORS middleware configuration for frontend integration

**Best For**: REST APIs, microservices, async backends, high-performance APIs, modern Python web services

See `fastapi-template/README.md` for detailed usage instructions.

---

*More templates coming soon! Check back for Node/Express, Vue.js, Next.js, and other frameworks.*

## Template Structure

Each template follows this consistent structure:

```
template-name/
├── README.md                   # Template-specific usage guide
├── CLAUDE.md                   # Framework context and best practices
├── .claude/
│   ├── settings.json          # Project-level Claude Code settings
│   ├── commands/              # Custom slash commands
│   │   ├── command1.md
│   │   ├── command2.md
│   │   └── ...
│   ├── agents/                # Specialized subagents
│   │   ├── agent1.md
│   │   ├── agent2.md
│   │   └── ...
│   └── skills/                # Agent skills
│       ├── skill1/
│       │   └── SKILL.md
│       └── skill2/
│           └── SKILL.md
├── .gitignore                 # Framework-specific gitignore
├── .env.example              # Environment variables template
└── [framework files]         # Minimal starter files
```

## What's Included in Each Template

### CLAUDE.md

- Framework-specific best practices and conventions
- Common commands and workflows
- Architecture patterns
- Testing strategies
- Security guidelines
- Links to official documentation

### Slash Commands

Quick-access commands for frequent operations:
- Running tests
- Database migrations
- Creating new components/modules
- Starting development servers
- Running linters and formatters

### Subagents

Specialized AI assistants for:
- Code review and security auditing
- Performance optimization
- Test generation
- Framework-specific expertise
- Debugging assistance

### Skills

Modular capabilities for:
- Design pattern implementation
- Code generation
- Analysis and validation
- Framework-specific workflows

### Framework Files

- Dependency configuration (requirements.txt, package.json)
- Environment templates (.env.example)
- Framework-appropriate .gitignore
- Setup instructions

## Customizing Templates

Each template is designed to be a starting point. You can:

1. **Extend CLAUDE.md**: Add project-specific conventions and guidelines
2. **Add Commands**: Create new slash commands in `.claude/commands/`
3. **Customize Agents**: Modify agent behavior or add new specialized agents
4. **Add Skills**: Develop custom skills for your workflow
5. **Adjust Settings**: Modify `.claude/settings.json` for team preferences

For detailed guidance on extending configurations, ask Claude Code about best practices or check the Claude Code documentation.

## Using These Templates

These templates are provided **as-is** for your own use and modification. Feel free to:

- Download and use any template for your projects
- Fork this repository and customize templates for your needs
- Adapt the configurations to match your workflow

**Note**: This is a solo project and I don't have time to review pull requests or implement feature requests. The templates are shared in the hope they'll be useful, but without active maintenance or support.

## Requirements

- VSCode (latest stable version recommended)
- Claude Code extension (v1.0 or later)
- Git (for cloning templates)
- Framework-specific requirements (see individual template READMEs)

## License

MIT License - See LICENSE file for details

## Support

These templates are provided as-is without active support. For help:

- **Claude Code Documentation**: Check the [Claude Code docs](https://docs.claude.com/claude-code) for configuration guidance
- **Template Issues**: You're welcome to open GitHub Issues to report problems, but responses may be limited or delayed
- **Your Own Modifications**: Feel free to fork and customize these templates to better suit your needs

---

**Note**: These templates include Claude Code configuration files (`.claude/`) that should be committed to version control. Personal overrides can be made in `.claude/settings.local.json` (git-ignored).
