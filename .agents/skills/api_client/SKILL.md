---
name: api_client
description: Guidelines for designing and interfacing with external APIs (rate limiting, configurations)
---

# API Client Interfacing Skills

## Procedure for Designing API Clients
When building or interfacing with external APIs, adhere to these procedural guidelines:
- **Rate Limiting & Backoff:** Ensure clients implement robust rate limiting and exponential backoff retry strategies (using jitter) for HTTP requests to prevent 429 errors.
- **Client Configuration:** Consolidate client instances, session headers, base URLs, and timeout configurations into centralized settings or setup hooks.
