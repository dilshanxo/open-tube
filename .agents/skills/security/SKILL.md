---
name: security
description: Safe subprocess execution, filesystem validation, input sanitization
---
# Security Skill

## Principles
- **Safe Execution**: Never construct unsafe shell commands from user input.
- **Filesystem**: Sanitize filenames, prevent path traversal. Validate output paths.
- **Logging**: Do not log sensitive data (tokens, personal paths).
