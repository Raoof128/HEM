# API Reference

Base URL: `http://localhost:8000`

## Key Management
### `POST /keys/generate`
Generate simulated keypair.
- Response: `{ "key_id": "...", "public_key": "..." }`

### `GET /keys/public`
Return current public context.
- Response: `{ "key_id": "...", "public_key": "SIMULATED_PUBLIC" }`

## Encryption
### `POST /encrypt`
Encrypt numeric values.
- Request: `{ "values": [1.2, 2.3] }`
- Response: `{ "ciphertext": "..." }`

### `POST /decrypt` (demo only)
Decrypt ciphertext when enabled.
- Request: `{ "ciphertext": "..." }`
- Response: `{ "values": [1.2, 2.3] }`

## Computation
All compute endpoints accept ciphertexts serialized as strings produced by `/encrypt`.

- `POST /compute/add` – `{ "a": "...", "b": "..." }`
- `POST /compute/mul` – `{ "a": "...", "b": "..." }`
- `POST /compute/dot` – `{ "a": "...", "b": "..." }`
- `POST /compute/polynomial` – `{ "ciphertext": "...", "coefficients": [0.5, 1.0] }`
- `POST /compute/mean` – `{ "ciphertext": "..." }`
- `POST /compute/linear` – `{ "ciphertext": "...", "weights": [0.2, 0.5], "bias": 0.1 }`

## Health
`GET /health` → `{ "status": "ok" }`
