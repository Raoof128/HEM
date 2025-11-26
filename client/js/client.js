// JavaScript SDK for the Homomorphic Encryption Microservice (simulated FHE)
class HEMClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async _request(path, options = {}) {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`Request failed: ${response.status} ${detail}`);
    }
    return response.json();
  }

  health() {
    return this._request('/health');
  }

  generateKeys() {
    return this._request('/keys/generate', { method: 'POST' });
  }

  encrypt(values) {
    return this._request('/encrypt', { method: 'POST', body: JSON.stringify({ values }) });
  }

  decrypt(ciphertext) {
    return this._request('/decrypt', { method: 'POST', body: JSON.stringify({ ciphertext }) });
  }

  add(a, b) {
    return this._request('/compute/add', { method: 'POST', body: JSON.stringify({ a, b }) });
  }

  mul(a, b) {
    return this._request('/compute/mul', { method: 'POST', body: JSON.stringify({ a, b }) });
  }

  dot(a, b) {
    return this._request('/compute/dot', { method: 'POST', body: JSON.stringify({ a, b }) });
  }

  polynomial(ciphertext, coefficients) {
    return this._request('/compute/polynomial', {
      method: 'POST',
      body: JSON.stringify({ ciphertext, coefficients }),
    });
  }

  mean(ciphertext) {
    return this._request('/compute/mean', { method: 'POST', body: JSON.stringify({ ciphertext }) });
  }

  linearModel(ciphertext, weights, bias = 0.0) {
    return this._request('/compute/linear', {
      method: 'POST',
      body: JSON.stringify({ ciphertext, weights, bias }),
    });
  }
}

export default HEMClient;
