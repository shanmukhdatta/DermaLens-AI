# Anonymous API request budgets

`FixedWindowLimiter` now bounds anonymous `POST /api/v1/images/check` to 12 requests/minute/socket-peer and `GET /api/v1/docs/search` to 40 requests/minute/socket-peer. It uses an instance-random hash of peer addresses, does not read spoofable proxy headers, and evicts expired state under capacity pressure. A full table refuses new callers instead of growing unbounded. It returns a safe HTTP 429 response with a constant retry-after header and no raw network address.

**Not sufficient by itself for production:** in-process counters reset at restart, are per instance, and cannot establish client identity across trusted proxy boundaries. A CDN/reverse proxy/API gateway MUST enforce distributed rate limits, WAF/abuse checks, TLS and request-size ceilings before any public deployment. This is a defense-in-depth engineering baseline only, not a production abuse-control certification.
