# Baseline authorization

The source datasets are public and contain no owner fields. Backend /api/territory requires Bearer ACCESS_TOKEN from Render encrypted environment configuration. Portal /api/territory requires HTTP Basic user contributor, with the same ACCESS_TOKEN held in Vercel encrypted environment configuration. Never print these values or put them in source code, prompts, logs, browser URLs or reports. The contributor agent can read configured values through the authenticated provider connection when needed; no human-provided credential is required.

Preserve these checks when implementing the portal-to-backend proxy. Use HTTPS. Public /health contains no data or credentials. This is an original prerequisite authentication contract, not a deployed customer system or claimed production authorization.
