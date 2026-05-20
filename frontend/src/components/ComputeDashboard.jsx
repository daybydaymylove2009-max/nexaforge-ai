import React, { useState } from 'react';
import { Activity, Cpu, Zap, Brain, Layers, Gauge, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import GPUCompareChart from './GPUCompareChart';
import ModelCapabilityMatrix from './ModelCapabilityMatrix';
import SelfImprovementAssessment from './SelfImprovementAssessment';

const ComputeDashboard = ({ comprehensive, gpuInfo, models, loading, runBenchmark, fetchAll }) => {
  const [expanded, setExpanded] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [benchmarkDuration, setBenchmarkDuration] = useState(5);
  const [isRunningBenchmark, setIsRunningBenchmark] = useState(false);

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

  const tabs = [
    { id: 'overview', label: '总览', icon: <Activity size={12} /> },
    { id: 'gpu', label: 'GPU对比', icon: <Cpu size={12} /> },
    { id: 'models', label: '模型矩阵', icon: <Layers size={12} /> },
    { id: 'evolution', label: '进化评估', icon: <Brain size={12} /> },
  ];

  const StatBadge = ({ icon, label, value, sub, color }) => (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '6px 10px',
      background: `${color}11`,
      border: `1px solid ${color}33`,
      borderRadius: '6px',
      flex: 1,
      minWidth: 0
    }}>
      {icon}
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', lineHeight: 1.2 }}>{label}</div>
        <div style={{ fontSize: '0.95rem', color, fontWeight: 'bold', lineHeight: 1.3, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {value}
        </div>
        {sub && <div style={{ fontSize: '0.55rem', color: 'var(--text-muted)', lineHeight: 1.2 }}>{sub}</div>}
      </div>
    </div>
  );

  return (
    <div style={{
      background: 'rgba(0, 0, 0, 0.2)',
      borderRadius: '8px',
      border: '1px solid rgba(0, 240, 255, 0.15)',
      overflow: 'hidden'
    }}>
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 14px',
          cursor: 'pointer',
          background: expanded ? 'rgba(0, 240, 255, 0.05)' : 'transparent',
          transition: 'background 0.2s'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: 0 }}>
          <Gauge size={16} color="var(--primary-neon)" />
          <span style={{ fontSize: '0.82rem', color: '#fff', fontWeight: 600, whiteSpace: 'nowrap' }}>AI算力评估</span>
          <div style={{ display: 'flex', gap: '6px', flex: 1, minWidth: 0 }}>
            <StatBadge
              icon={<Zap size={12} color="var(--purple-neon)" />}
              label="GPU算力"
              value={`${gpuInfo?.tflops_fp16 || 0} TFLOPS`}
              color="var(--purple-neon)"
            />
            <StatBadge
              icon={<Layers size={12} color="var(--success-neon)" />}
              label="可训练"
              value={`${pretraining.capable_models?.length || 0} 模型`}
              color="var(--success-neon)"
            />
            <StatBadge
              icon={<Brain size={12} color="var(--warning-neon)" />}
              label="进化等级"
              value={selfImprove.capability_level || 0}
              sub={selfImprove.max_capability || ''}
              color="var(--warning-neon)"
            />
            <StatBadge
              icon={<Gauge size={12} color="var(--primary-neon)" />}
              label="评分"
              value={overallScore.grade || 'N/A'}
              sub={overallScore.description || ''}
              color="var(--primary-neon)"
            />
          </div>
        </div>
        {expanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
      </div>

      {expanded && (
        <div style={{ borderTop: '1px solid rgba(0, 240, 255, 0.1)' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '8px 14px',
            background: 'rgba(0, 0, 0, 0.15)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.05)'
          }}>
            <div style={{ display: 'flex', gap: '2px' }}>
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  style={{
                    padding: '5px 10px',
                    background: activeTab === tab.id ? 'rgba(0, 240, 255, 0.15)' : 'transparent',
                    border: '1px solid',
                    borderColor: activeTab === tab.id ? 'rgba(0, 240, 255, 0.3)' : 'transparent',
                    borderRadius: '4px',
                    color: activeTab === tab.id ? 'var(--primary-neon)' : 'var(--text-muted)',
                    fontSize: '0.7rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    transition: 'all 0.2s'
                  }}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
              <select
                value={benchmarkDuration}
                onChange={(e) => setBenchmarkDuration(Number(e.target.value))}
                onClick={(e) => e.stopPropagation()}
                style={{
                  padding: '3px 6px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '3px',
                  color: '#fff',
                  fontSize: '0.65rem'
                }}
              >
                <option value={3}>3秒</option>
                <option value={5}>5秒</option>
                <option value={10}>10秒</option>
              </select>
              <button
                onClick={(e) => { e.stopPropagation(); handleRunBenchmark(); }}
                disabled={isRunningBenchmark || loading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '4px 8px',
                  background: 'rgba(0, 240, 255, 0.15)',
                  border: '1px solid rgba(0, 240, 255, 0.25)',
                  borderRadius: '4px',
                  color: 'var(--primary-neon)',
                  fontSize: '0.65rem',
                  cursor: isRunningBenchmark ? 'not-allowed' : 'pointer'
                }}
              >
                <RefreshCw size={10} className={isRunningBenchmark ? 'spin' : ''} />
                {isRunningBenchmark ? '测试中' : '基准测试'}
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); fetchAll(); }}
                style={{
                  padding: '4px 6px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '3px',
                  color: 'var(--text-muted)',
                  cursor: 'pointer'
                }}
              >
                <RefreshCw size={10} />
              </button>
            </div>
          </div>

          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {activeTab === 'overview' && (
              <div style={{ padding: '12px 14px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>GPU型号:</span>
                    <span style={{ color: '#fff' }}>{gpuInfo?.gpu_name || '未知'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>显存:</span>
                    <span style={{ color: '#fff' }}>{gpuInfo?.vram_gb || 0} GB</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>预训练:</span>
                    <span style={{ color: pretraining.can_pretrain ? 'var(--success-neon)' : 'var(--danger-neon)' }}>
                      {pretraining.can_pretrain ? '可以' : '不足'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>最大微调:</span>
                    <span style={{ color: '#fff' }}>{finetuning.max_finetune_params || 0}B</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>自进化:</span>
                    <span style={{ color: selfImprove.capable ? 'var(--success-neon)' : 'var(--danger-neon)' }}>
                      {selfImprove.capable ? '具备' : '不足'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>模型库:</span>
                    <span style={{ color: '#fff' }}>{models?.total_models || 0} 个</span>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'gpu' && <GPUCompareChart gpuInfo={gpuInfo} />}
            {activeTab === 'models' && <ModelCapabilityMatrix comprehensive={comprehensive} models={models} />}
            {activeTab === 'evolution' && <SelfImprovementAssessment comprehensive={comprehensive} fetchSelfImprovement={null} />}
          </div>
        </div>
      )}
    </div>
  );
};

export default ComputeDashboard;
