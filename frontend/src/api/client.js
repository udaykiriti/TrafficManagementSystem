const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const DEFAULT_TIMEOUT = 15000;

const withTimeoutSignal = (ms = DEFAULT_TIMEOUT) => {
  if (typeof AbortSignal !== 'undefined' && typeof AbortSignal.timeout === 'function') {
    return AbortSignal.timeout(ms);
  }
  if (typeof AbortController === 'undefined') return undefined;
  const controller = new AbortController();
  setTimeout(() => controller.abort(), ms);
  return controller.signal;
};

export const getApiBase = () => API_BASE;

export const fetchJson = async (path, options = {}) => {
  const { timeout, ...rest } = options;
  const signal = options.signal || withTimeoutSignal(timeout || DEFAULT_TIMEOUT);
  const res = await fetch(`${API_BASE}${path}`, { ...rest, signal });
  const data = await res.json();
  if (!res.ok) {
    const error = new Error(data?.error || 'Request failed');
    error.status = res.status;
    error.data = data;
    throw error;
  }
  return data;
};
