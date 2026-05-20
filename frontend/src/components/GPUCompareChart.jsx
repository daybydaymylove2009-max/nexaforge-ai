import React, { useMemo } from 'react';
import { Activity, Cpu, Zap, TrendingUp } from 'lucide-react';

const GPUCompareChart = ({ gpuInfo, gpuInfo: { gpu_name, tflops_fp16, rankings } = {} }) => {
  const sortedGPUs = useMemo(() => {
    if (!rankings || !Array.isArray(rankings)) return [];
    return [...rankings]
      .sort((a, b) => b.tflops_fp16_tensor - a.tflops_fp16_tensor)
      .slice(0, 15);
  }, [rankings]);

  const currentIndex = useMemo(() => {
    if (!sortedGPUs.length || !gpu_name) return -1;
    return sortedGPUs.findIndex(g => g.name.toLowerCase().includes(gpu_name.toLowerCase().split(' ')[0]));
  }, [sortedGPUs, gpu_name]);

  const percentile = useMemo(() => {
    if (currentIndex < 0 || !sortedGPUs.length) return 0;
    return Math.round(((sortedGPUs.length - currentIndex) / sortedGPUs.length) * 100);
  }, [currentIndex, sortedGPUs.length]);

  const maxTflops = useMemo(() => {
    if (!sortedGPUs.length) return 100;
    return Math.max(...sortedGPUs.map(g => g.tflops_fp16_tensor), tflops_fp16 || 0);
  }, [sortedGPUs, tflops_fp16]);

  const getBarColor = (index) => {
    if (index === currentIndex) return 'linear-gradient(90deg, var(--primary-neon), #b347ff)';
    if (index < 5) return 'rgba(255, 179, 71, 0.6)';
    if (index < 10) return 'rgba(255, 255, 255, 0.3)';
    return 'rgba(255, 255, 255, 0.15)';
  };

  const getBarGlow = (index) => {
    if (index === currentIndex) return '0 0 20px rgba(0, 240, 255, 0.5)';
    return 'none';
  };

  if (!gpuInfo) {
    return (
      <div style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        正在加载GPU对比数据...
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Activity size={20} color="var(--primary-neon)" />
          <div>
            <h3 style={{ margin: 0, fontSize: '1rem', color: '#fff' }}>GPU性能排行榜</h3>
            <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              前 {sortedGPUs.length} 款GPU与当前系统对比
            </p>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>当前GPU</div>
          <div style={{ fontSize: '1.1rem', color: 'var(--primary-neon)', fontWeight: 'bold' }}>
            {tflops_fp16} TFLOPS
          </div>
        </div>
      </div>

      {currentIndex >= 0 && (
        <div style={{
          background: 'rgba(0, 240, 255, 0.1)',
          border: '1px solid rgba(0, 240, 255, 0.3)',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px'
        }}>
          <TrendingUp size={24} color="var(--primary-neon)" />
          <div>
            <div style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 'bold' }}>
              {gpu_name}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              排名 #{currentIndex + 1} / {sortedGPUs.length} (前 {percentile}%)
            </div>
          </div>
          <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
            <div style={{ fontSize: '1.5rem', color: 'var(--primary-neon)', fontWeight: 'bold' }}>
              {percentile}%
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>领先比例</div>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {sortedGPUs.map((gpu, idx) => {
          const widthPercent = (gpu.tflops_fp16_tensor / maxTflops) * 100;
          const isCurrent = idx === currentIndex;

          return (
            <div
              key={idx}
              style={{
                position: 'relative',
                padding: '10px 12px',
                background: isCurrent ? 'rgba(0, 240, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                borderRadius: '6px',
                border: isCurrent ? '1px solid rgba(0, 240, 255, 0.3)' : '1px solid transparent',
                transition: 'all 0.3s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{
                    fontSize: '0.7rem',
                    color: 'var(--text-muted)',
                    minWidth: '24px'
                  }}>
                    #{idx + 1}
                  </span>
                  <span style={{
                    fontSize: '0.85rem',
                    color: isCurrent ? 'var(--primary-neon)' : '#fff',
                    fontWeight: isCurrent ? 'bold' : '400'
                  }}>
                    {gpu.name}
                    {isCurrent && <span style={{ marginLeft: '8px', fontSize: '0.65rem', color: 'var(--primary-neon)' }}>[当前]</span>}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '16px', fontSize: '0.75rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{gpu.vram_gb}GB</span>
                  <span style={{ color: isCurrent ? 'var(--primary-neon)' : 'var(--text-muted)', fontWeight: isCurrent ? 'bold' : '400' }}>
                    {gpu.tflops_fp16_tensor} TFLOPS
                  </span>
                </div>
              </div>
              <div style={{
                height: '6px',
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '3px',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${widthPercent}%`,
                  background: getBarColor(idx),
                  boxShadow: getBarGlow(idx),
                  borderRadius: '3px',
                  transition: 'width 0.5s ease-out'
                }} />
              </div>
            </div>
          );
        })}
      </div>

      <div style={{
        marginTop: '20px',
        padding: '12px',
        background: 'rgba(0, 0, 0, 0.2)',
        borderRadius: '8px',
        border: '1px solid rgba(255, 255, 255, 0.05)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <Cpu size={14} color="var(--text-muted)" />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>GPU架构</span>
        </div>
        <div style={{ fontSize: '0.85rem', color: '#fff' }}>
          {gpuInfo.gpu_info?.architecture || '未知'} | 带宽: {gpuInfo.gpu_info?.bandwidth_gb_s || '--'} GB/s
        </div>
      </div>
    </div>
  );
};

export default GPUCompareChart;
