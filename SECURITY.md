# Security Policy

## Reporting a Vulnerability
Please email security@example.com with a description of the issue, reproduction steps, and any proof-of-concept material. We aim to acknowledge reports within 48 hours.

## Scope
This repository contains a **simulated** homomorphic encryption system intended for education. Do not use it to protect sensitive or production data. The decrypt endpoint is provided for demos and should be disabled via configuration for real deployments.

## Best Practices
- Keep dependencies updated.
- Disable `/decrypt` in production by setting `enable_simulated_decrypt` to `False` in `server/utils/config.py`.
- Place the service behind an authenticated gateway and enforce HTTPS.
- Rotate keys frequently; the in-memory key store is not persistent.
