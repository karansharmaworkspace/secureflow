# Zeek Configuration

Configuration files for the Zeek network sensor's HTTP metadata extraction. Defines the custom log format that captures only metadata (method, path, status, UA, host, referrer, response size) — no payload or PII.

## Files

### local.zeek — Main Config Loader (9 lines)

Loads Zeek base frameworks: `logging`, `conn`, `http`. Loads custom `zeek-http-log` script. **Disables** default `Conn::LOG` and `HTTP::LOG` (which capture full connection/HTTP details). **Enables** custom `HTTPLog::LOG` — only the minimal metadata fields defined in `zeek-http-log.zeek`.

### zeek-http-log.zeek — HTTP Metadata Extraction (49 lines)

Defines a custom Zeek `HTTPLog` module that extends `Conn::Info` with 7 metadata-only fields:
- `http_method` (string) — GET/POST/PUT/DELETE/etc.
- `http_path` (string) — The request URI path
- `http_status` (string) — HTTP response status code
- `http_user_agent` (string) — Client User-Agent header
- `http_host` (string) — Host header from request
- `http_referrer` (string) — Referrer header
- `http_response_size` (count) — Response body length in bytes

Hooks 4 Zeek events:
- `http_request` — Captures HTTP method + original URI at request time
- `http_reply` — Captures status code + reason phrase
- `http_header` — Captures `user-agent`, `host`, and `referer` headers (case-insensitive via `to_lower()`)
- `http_endpoint` — Captures response body size at end of HTTP session

All fields are marked `&log &optional` — only present when available, no forced defaults.
