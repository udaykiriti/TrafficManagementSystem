import { useEffect, useState, useCallback } from 'react';
import { fetchJson } from '../api/client';

const POLL_MS = 30000;

export default function useHealth() {
  const [health, setHealth] = useState({ status: 'checking', components: {} });

  const checkHealth = useCallback(async () => {
    try {
      const data = await fetchJson('/health', { method: 'GET', timeout: 5000 });
      setHealth(data);
    } catch (err) {
      setHealth({ status: 'offline', components: {} });
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const id = setInterval(checkHealth, POLL_MS);
    return () => clearInterval(id);
  }, [checkHealth]);

  return { health, checkHealth };
}
