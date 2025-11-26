# Architecture Overview

```mermaid
graph TD
  ClientSDK[Client SDKs (Python/JS)] -->|REST| API[FastAPI Service]
  API -->|Routes| ComputeRoutes[Compute Router]
  API -->|Routes| KeyRoutes[Keys & Encrypt Router]
  API -->|Routes| DebugRoutes[Debug/Health]
  ComputeRoutes --> Engine[Simulated FHE Engine]
  KeyRoutes --> Engine
  Engine --> KeyStore[In-memory Key Store]
  API --> Audit[Audit Logger]
  API --> Dashboard[Static Dashboard]
```

## Components
- **server/main.py** – FastAPI application setup, middleware, rate limiting, and router registration.
- **server/he_engine.py** – Simulated FHE engine supporting arithmetic, polynomial evaluation, and a linear model over ciphertext payloads.
- **server/routes/** – API endpoints for encryption/decryption, computations, and health.
- **server/security/** – Mock key store and audit logging utilities.
- **client/python, client/js** – Lightweight SDKs to simplify encrypt → compute → decrypt flows.
- **dashboard/** – Static HTML dashboard with sample charts for latency and ciphertext sizes.
- **tests/** – Unit and integration tests covering the engine and HTTP surface.

## Data Flow
1. Client generates or receives public key metadata.
2. Client encrypts plaintext values into simulated ciphertext and sends to `/compute/*` endpoints.
3. Server performs homomorphic-style operations without accessing plaintext.
4. Results are returned as ciphertext. Optional `/decrypt` endpoint can reveal plaintext only for demonstrations.

## Security Notes
- Encryption is simulated; do not use for real secrets.
- Keys are stored in-memory; plug in HSM/KMS for production.
- Rate limiting and audit logging are present but should be augmented with authentication and TLS termination in real deployments.
- The engine validates inputs (non-empty payloads, matching vector sizes) and will return HTTP 400 on misuse.
- Ciphertexts are validated against the active key to avoid cross-key operations.
- The `/decrypt` endpoint is gated behind `enable_simulated_decrypt` for safer defaults.
