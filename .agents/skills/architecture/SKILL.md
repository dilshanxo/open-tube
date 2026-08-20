---
name: architecture
description: Architecture principles for OpenTube (layered design, dependencies, boundaries)
---
# Architecture Skill

## Principles
- **Layered Architecture**: Strict boundaries between UI, Application, Domain, Services, and Infrastructure.
- **Dependency Direction**: UI depends on Application. Application depends on Services/Domain. Services depend on Infrastructure and Domain.
- **Service Boundaries**: Isolate external dependencies (yt-dlp, FFmpeg, Filesystem) behind clear interfaces or service boundaries.
- **Anti-patterns**: Avoid god classes, tightly coupled UI and logic, hardcoded paths.
