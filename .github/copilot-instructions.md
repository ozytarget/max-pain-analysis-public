# Copilot Instructions for AI Coding Agents

## Project Overview
This repository is a Python-based system for user management, code analysis, and auditing, with a focus on security and automation. The main application and utilities are in the `max-pain-analysis-public/` directory.

## Architecture & Key Components
- **app.py**: Main entry point for the application.
- **user_management.py**: Handles user creation, authentication, and session management. Uses `auth_data/active_sessions.json` for session persistence.
- **audit_*.py**: Scripts for auditing users and cleaning up user data.
- **code_analyzer.py, code_generator.py, code_validator.py**: Tools for static code analysis, code generation, and validation.
- **migrate_users.py**: Handles migration of user data, likely between formats or systems.
- **pre_commit_validator.py**: Ensures code quality before commits.
- **verify_system.py**: Performs system integrity checks.
- **auth_data/**: Stores authentication/session data and backups.
- **data/**, **logs/**: Store application data and logs, respectively.

## Developer Workflows
- **Run the app**: Use `python app.py` from the `max-pain-analysis-public/` directory.
- **Testing/auditing**: Run scripts directly, e.g., `python audit_users.py` or `python code_analyzer.py`.
- **Pre-commit validation**: Run `python pre_commit_validator.py` before committing changes.
- **Docker**: Use the provided `Dockerfile` and `entrypoint.sh` for containerized deployment. The `Procfile` and `railway.json` support deployment to platforms like Railway.

## Project-Specific Conventions
- **Session and user data**: Persisted in JSON files under `auth_data/`.
- **Backups**: Located in `auth_data/backups/`.
- **No central test runner**: Scripts are run individually for their respective tasks.
- **Security**: Emphasis on auditing, validation, and system verification scripts.

## Integration & Dependencies
- **requirements.txt**: Lists all Python dependencies.
- **Dockerfile**: Defines the build for containerized environments.
- **entrypoint.sh**: Used as the entry point for Docker containers.

## Patterns & Examples
- To add a new audit or validation script, follow the pattern in `audit_users.py` or `code_validator.py`.
- For user/session management, see `user_management.py` and `auth_data/active_sessions.json`.
- For deployment, ensure changes are reflected in `Dockerfile`, `Procfile`, and `railway.json` as needed.

## References
- Main logic: `max-pain-analysis-public/app.py`
- User/session: `max-pain-analysis-public/user_management.py`, `auth_data/`
- Auditing: `max-pain-analysis-public/audit_*.py`
- Validation: `max-pain-analysis-public/code_validator.py`, `pre_commit_validator.py`
- Deployment: `max-pain-analysis-public/Dockerfile`, `entrypoint.sh`, `Procfile`, `railway.json`

---

Update this file as the project evolves. For questions, review the referenced files for implementation details and patterns.
