import { useState, useEffect, useCallback } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
const API_KEY = 'NEXA-PRO-2026';

export function useComputeEvaluation() {
  const [comprehensive, setComprehensive] = useState(null);
  const [gpuInfo, setGpuInfo] = useState(null);
  const [models, setModels] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchComprehensive = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/compute/evaluation/comprehensive?api_key=${API_KEY}`);
      const json = await res.json();
      if (json.code === 200) {
        setComprehensive(json.data);
      }
    } catch (err) {
      console.error('Fetch comprehensive evaluation failed:', err);
    }
  }, []);

  const fetchGpuInfo = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/compute/gpu/info?api_key=${API_KEY}`);
      const json = await res.json();
      if (json.code === 200) {
        setGpuInfo(json.data);
      }
    } catch (err) {
      console.error('Fetch GPU info failed:', err);
    }
  }, []);

  const fetchModels = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/compute/models?api_key=${API_KEY}`);
      const json = await res.json();
      if (json.code === 200) {
        setModels(json.data);
      }
    } catch (err) {
      console.error('Fetch models failed:', err);
    }
  }, []);

  const runBenchmark = useCallback(async (duration = 5) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/compute/gpu/benchmark?duration=${duration}&api_key=${API_KEY}`);
      const json = await res.json();
      setLoading(false);
      if (json.code === 200) {
        await fetchComprehensive();
        return json.data;
      }
      throw new Error(json.message);
    } catch (err) {
      setLoading(false);
      setError(err.message);
      throw err;
    }
  }, [fetchComprehensive]);

  const fetchPretraining = useCallback(async (datasetTokens = 100_000_000_000) => {
    try {
      const res = await fetch(`${API_BASE}/api/compute/pretraining?dataset_tokens=${datasetTokens}&api_key=${API_KEY}`);
      const json = await res.json();
      if (json.code === 200) {
        return json.data;
      }
    } catch (err) {
      console.error('Fetch pretraining capability failed:', err);
    }
    return null;
  }, []);

  const fetchFinetuning = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/compute/finetuning?api_key=${API_KEY}`);
      const json = await res.json();
      if (json.code === 200) {
        return json.data;
      }
    } catch (err) {
      console.error('Fetch finetuning capability failed:', err);
    }
    return null;
  }, []);

  const fetchSelfImprovement = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/compute/self-improvement?api_key=${API_KEY}`);
      const json = await res.json();
      if (json.code === 200) {
        return json.data;
      }
    } catch (err) {
      console.error('Fetch self-improvement capability failed:', err);
    }
    return null;
  }, []);

  const fetchAll = useCallback(async () => {
    await Promise.all([fetchComprehensive(), fetchGpuInfo(), fetchModels()]);
  }, [fetchComprehensive, fetchGpuInfo, fetchModels]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return {
    comprehensive,
    gpuInfo,
    models,
    loading,
    error,
    fetchComprehensive,
    fetchGpuInfo,
    fetchModels,
    runBenchmark,
    fetchPretraining,
    fetchFinetuning,
    fetchSelfImprovement,
    fetchAll,
  };
}

export default useComputeEvaluation;
