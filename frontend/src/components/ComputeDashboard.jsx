import React, { useState } from 'react';
import { Activity, Cpu, Zap, Brain, Layers, Gauge, X, RefreshCw } from 'lucide-react';
import GPUCompareChart from './GPUCompareChart';
import ModelCapabilityMatrix from './ModelCapabilityMatrix';
import SelfImprovementAssessment from './SelfImprovementAssessment';

const ComputeDashboard = ({ comprehensive, gpuInfo, models, loading, runBenchmark, fetchAll }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [benchmarkDuration, setBenchmarkDuration] = useState(5);
  const [isRunningBenchmark, setIsRunningBenchmark] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Activity size={14} /> },
    { id: 'gpu', label: 'GPU Comparison', icon: <Cpu size={14} /> },
    { id: 'models', label: 'Model Matrix', icon: <Layers size={14} /> },
    { id: 'evolution', label: 'Evolution', icon: <Brain size={14} /> },
  ];

  const handleRunBenchmark = async () => {
    setIsRunningBenchmark(true);
    try {
      await runBenchmark(benchmarkDuration);
    } catch (err) {
      console.error('Benchmark failed:', err);
    } finally {
      setIsRunningBenchmark(false);
    }
  };

  const overallScore = comprehensive?.overall_score || {};
  const pretraining = comprehensive?.pretraining_assessment || {};
  const finetuning = comprehensive?.finetuning_assessment || {};
  const selfImprove = comprehensive?.self_improvement_assessment || {};

  return (
    <div style={{
      background: 'rgba(0, 0, 0, 0.3)',
      borderRadius: '12px',
      border: '1px solid rgba(0, 240, 255, 0.2)',
      overflow: 'hidden'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 20px',
        background: 'rgba(0, 240, 255, 0.05)',
        borderBottom: '1px solid rgba(0, 240, 255, 0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Gauge size={20} color="var(--primary-neon)" />
          <div>
            <h3 style={{ margin: 0, fontSize: '1rem', color: '#fff' }}>AI Compute Evaluation Dashboard</h3>
            <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Enterprise-grade GPU Benchmarking & Model Capability Assessment
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Benchmark:</label>
            <select
              value={benchmarkDuration}
              onChange={(e) => setBenchmarkDuration(Number(e.target.value))}
              style={{
                padding: '6px 10px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '4px',
                color: '#fff',
                fontSize: '0.75rem'
              }}
            >
              <option value={3}>3s</option>
              <option value={5}>5s</option>
              <option value={10}>10s</option>
              <option value={20}>20s</option>
            </select>
          </div>
          <button
            onClick={handleRunBenchmark}
            disabled={isRunningBenchmark || loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              background: isRunningBenchmark ? 'rgba(0, 240, 255, 0.3)' : 'rgba(0, 240, 255, 0.2)',
              border: '1px solid rgba(0, 240, 255, 0.3)',
              borderRadius: '6px',
              color: 'var(--primary-neon)',
              fontSize: '0.8rem',
              cursor: isRunningBenchmark ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
            <RefreshCw size={14} className={isRunningBenchmark ? 'spin' : ''} />
            {isRunningBenchmark ? 'Running...' : 'Run Benchmark'}
          </button>
          <button
            onClick={fetchAll}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '6px',
              color: '#fff',
              fontSize: '0.8rem',
              cursor: 'pointer'
            }}
          >
            <RefreshCw size={14} />
            Refresh
          </button>
        </div>
      </div>

      <div style={{
        display: 'flex',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        background: 'rgba(0, 0, 0, 0.2)'
      }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: 1,
              padding: '12px 16px',
              background: activeTab === tab.id ? 'rgba(0, 240, 255, 0.1)' : 'transparent',
              border: 'none',
              borderBottom: activeTab === tab.id ? '2px solid var(--primary-neon)' : '2px solid transparent',
              color: activeTab === tab.id ? 'var(--primary-neon)' : 'var(--text-muted)',
              fontSize: '0.8rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              transition: 'all 0.3s ease'
            }}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      <div style={{ padding: '20px', maxHeight: '600px', overflowY: 'auto' }}>
        {activeTab === 'overview' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
              <div style={{
                background: 'rgba(0, 240, 255, 0.08)',
                border: '1px solid rgba(0, 240, 255, 0.2)',
                borderRadius: '8px',
                padding: '16px',
                textAlign: 'center'
              }}>
                <Gauge size={20} color="var(--primary-neon)" style={{ marginBottom: '8px' }} />
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Overall Score</div>
                <div style={{ fontSize: '1.5rem', color: overallScore.grade === 'S' ? 'var(--success-neon)' : '#fff', fontWeight: 'bold' }}>
                  {overallScore.grade || 'N/A'}
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {overallScore.description || 'Analyzing...'}
                </div>
              </div>

              <div style={{
                background: 'rgba(179, 71, 255, 0.08)',
                border: '1px solid rgba(179, 71, 255, 0.2)',
                borderRadius: '8px',
                padding: '16px',
                textAlign: 'center'
              }}>
                <Zap size={20} color="var(--purple-neon)" style={{ marginBottom: '8px' }} />
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>GPU TFLOPS</div>
                <div style={{ fontSize: '1.5rem', color: 'var(--purple-neon)', fontWeight: 'bold' }}>
                  {gpuInfo?.tflops_fp16 || 0}
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  FP16 Tensor
                </div>
              </div>

              <div style={{
                background: 'rgba(0, 255, 102, 0.08)',
                border: '1px solid rgba(0, 255, 102, 0.2)',
                borderRadius: '8px',
                padding: '16px',
                textAlign: 'center'
              }}>
                <Layers size={20} color="var(--success-neon)" style={{ marginBottom: '8px' }} />
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Models Trainable</div>
                <div style={{ fontSize: '1.5rem', color: 'var(--success-neon)', fontWeight: 'bold' }}>
                  {pretraining.capable_models?.length || 0}
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Pre-training capable
                </div>
              </div>

              <div style={{
                background: 'rgba(255, 179, 71, 0.08)',
                border: '1px solid rgba(255, 179, 71, 0.2)',
                borderRadius: '8px',
                padding: '16px',
                textAlign: 'center'
              }}>
                <Brain size={20} color="var(--warning-neon)" style={{ marginBottom: '8px' }} />
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Evolution Level</div>
                <div style={{ fontSize: '1.5rem', color: 'var(--warning-neon)', fontWeight: 'bold' }}>
                  {selfImprove.capability_level || 0}
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {selfImprove.max_capability || 'None'}
                </div>
              </div>
            </div>

            <div style={{
              background: 'rgba(0, 0, 0, 0.2)',
              borderRadius: '8px',
              padding: '16px',
              border: '1px solid rgba(255, 255, 255, 0.05)'
            }}>
              <h4 style={{ fontSize: '0.9rem', color: '#fff', marginBottom: '16px' }}>Quick Summary</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '0.8rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>GPU Model:</span>
                  <span style={{ color: '#fff' }}>{gpuInfo?.gpu_name || 'Unknown'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>VRAM:</span>
                  <span style={{ color: '#fff' }}>{gpuInfo?.vram_gb || 0} GB</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Pretrain Capability:</span>
                  <span style={{ color: pretraining.can_pretrain ? 'var(--success-neon)' : 'var(--danger-neon)' }}>
                    {pretraining.can_pretrain ? 'Yes' : 'No'}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Max Finetune:</span>
                  <span style={{ color: '#fff' }}>{finetuning.max_finetune_params || 0}B params</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Self-Improve:</span>
                  <span style={{ color: selfImprove.capable ? 'var(--success-neon)' : 'var(--danger-neon)' }}>
                    {selfImprove.capable ? 'Capable' : 'Unable'}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Models in DB:</span>
                  <span style={{ color: '#fff' }}>{models?.total_models || 0}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'gpu' && <GPUCompareChart gpuInfo={gpuInfo} />}
        {activeTab === 'models' && <ModelCapabilityMatrix comprehensive={comprehensive} models={models} />}
        {activeTab === 'evolution' && (
          <SelfImprovementAssessment comprehensive={comprehensive} fetchSelfImprovement={null} />
        )}
      </div>
    </div>
  );
};

export default ComputeDashboard;
