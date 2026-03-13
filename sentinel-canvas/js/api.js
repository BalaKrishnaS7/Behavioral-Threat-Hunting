/* ══════════════════════════════════════════════
   SENTINEL CANVAS — API CLIENT
   ══════════════════════════════════════════════ */

const API = (() => {
  const _cache = {};
  const _inFlight = {};
  const CACHE_TTL = 10000; // 10s cache to avoid hammering API
  const REQUEST_TIMEOUT_MS = 12000;
  const RETRY_DELAY_MS = 450;

  function _isTransient(err) {
    const msg = String(err?.message || '').toLowerCase();
    const name = String(err?.name || '').toLowerCase();
    return (
      name.includes('abort') ||
      name.includes('timeout') ||
      msg.includes('timed out') ||
      msg.includes('failed to fetch') ||
      msg.includes('networkerror')
    );
  }

  async function fetch_(endpoint) {
    const url = `${App.getApiBase()}${endpoint}`;
    const now = Date.now();
    if (_cache[url] && (now - _cache[url].ts) < CACHE_TTL) {
      return _cache[url].data;
    }
    if (_inFlight[url]) {
      return _inFlight[url];
    }

    _inFlight[url] = (async () => {
      let lastErr;
      for (let attempt = 0; attempt < 2; attempt++) {
        try {
          const res = await fetch(url, { signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS) });
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          const data = await res.json();
          _cache[url] = { ts: Date.now(), data };
          return data;
        } catch (err) {
          lastErr = err;
          if (!_isTransient(err) || attempt === 1) {
            throw err;
          }
          await new Promise(r => setTimeout(r, RETRY_DELAY_MS));
        }
      }
      throw lastErr;
    })();

    try {
      return await _inFlight[url];
    } finally {
      delete _inFlight[url];
    }
  }

  function invalidate() {
    Object.keys(_cache).forEach(k => delete _cache[k]);
  }

  async function checkStatus() {
    const dot  = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    dot.className = 'status-dot checking';
    text.textContent = 'checking…';
    try {
      // Bypass the in-flight/cache layer — we need a real network hit to check liveness.
      const url = `${App.getApiBase()}/api/stats`;
      const res = await fetch(url, { signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      // Warm the cache with the fresh response so the next widget load is instant.
      const data = await res.json();
      _cache[url] = { ts: Date.now(), data };
      const host = App.getApiBase().replace(/^https?:\/\//, '');
      dot.className  = 'status-dot online';
      text.textContent = `${host} — online`;
      return true;
    } catch {
      dot.className  = 'status-dot offline';
      text.textContent = 'API offline';
      return false;
    }
  }

  async function getStats()     { return fetch_('/api/stats'); }
  async function getAlerts()    { return fetch_('/api/alerts'); }
  async function getIncidents() { return fetch_('/api/incidents'); }

  return { fetch: fetch_, invalidate, checkStatus, getStats, getAlerts, getIncidents };
})();