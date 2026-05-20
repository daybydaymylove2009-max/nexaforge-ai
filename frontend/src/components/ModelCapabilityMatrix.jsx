import React, { useMemo, useState } from 'react';
import { Layers, CheckCircle, XCircle, AlertCircle, Filter, Search } from 'lucide-react';

const ModelCapabilityMatrix = ({ comprehensive, models }) => {
  const [filterProvider, setFilterProvider] = useState('all');
  const [filterSize, setFilterSize] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const sizeCategories = {
    'all': '全部大小',
    'micro': '微型 (< 1B)',
    'small': '小型 (1-3B)',
    'medium': '中型 (3-7B)',
    'large': '大型 (7-13B)',
    'xlarge': '超大 (13-70B)',
    'super': '超级 (70B+)'
  };

  const getSizeCategory = (paramsB) => {
    if (paramsB < 1) return 'micro';
    if (paramsB < 3) return 'small';
    if (paramsB < 7) return 'medium';
    if (paramsB < 13) return 'large';
    if (paramsB < 70) return 'xlarge';
    return 'super';
  };

  const filteredModels = useMemo(() => {
    if (!models?.models) return [];
    return models.models.filter(model => {
      const sizeCategory = getSizeCategory(model.params_b);
      const matchesSize = filterSize === 'all' || sizeCategory === filterSize;
      const matchesProvider = filterProvider === 'all' || model.provider.toLowerCase().includes(filterProvider.toLowerCase());
      const matchesSearch = !searchTerm || 
        model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        model.architecture.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesSize && matchesProvider && matchesSearch;
    }).sort((a, b) => a.params_b - b.params_b);
  }, [models, filterSize, filterProvider, searchTerm]);

  const modelCounts = useMemo(() => {
    if (!models?.models) return {};
    const counts = { micro: 0, small: 0, medium: 0, large: 0, xlarge: 0, super: 0 };
    models.models.forEach(m => {
      const cat = getSizeCategory(m.params_b);
      counts[cat]++;
    });
    return counts;
  }, [models]);

  const pretraining = comprehensive?.pretraining_assessment || {};
  const finetuning = comprehensive?.finetuning_assessment || {};
  const capableModels = pretraining.capable_models || [];

  const getCapabilityStatus = (model) => {
    const capable = capableModels.find(m => m.model_name === model.name);
    if (!capable) return { status: 'unable', text: '不可行', color: 'var(--danger-neon)' };
    
    if (capable.estimated_days < 1) return { status: 'fast', text: '< 1天', color: 'var(--success-neon)' };
    if (capable.estimated_days < 7) return { status: 'good', text: `${capable.estimated_days}天`, color: 'var(--primary-neon)' };
    if (capable.estimated_days < 30) return { status: 'moderate', text: `${capable.estimated_days}天`, color: 'var(--warning-neon)' };
    return { status: 'slow', text: `${capable.estimated_days}天+`, color: 'var(--text-muted)' };
  };

  const getVRAMStatus = (required, available) => {
    if (available >= required) return { status: 'ok', color: 'var(--success-neon)' };
    if (available >= required * 0.7) return { status: 'partial', color: 'var(--warning-neon)' };
    return { status: 'insufficient', color: 'var(--danger-neon)' };
  };

  if (!models) {
    return (
      <div style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        正在加载模型数据库...
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Layers size={20} color="var(--primary-neon)" />
          <div>
            <h3 style={{ margin: 0, fontSize: '1rem', color: '#fff' }}>模型训练能力矩阵</h3>
            <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              已收录 {models.total_models} 个模型 | 参数范围 0.5B - 140B
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <div style={{ flex: '1 1 200px', position: 'relative' }}>
          <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="搜索模型..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 10px 8px 32px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '6px',
              color: '#fff',
              fontSize: '0.8rem',
              outline: 'none'
            }}
          />
        </div>
        <select
          value={filterSize}
          onChange={(e) => setFilterSize(e.target.value)}
          style={{
            padding: '8px 12px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '6px',
            color: '#fff',
            fontSize: '0.8rem',
            cursor: 'pointer'
          }}
        >
          {Object.entries(sizeCategories).map(([key, label]) => (
            <option key={key} value={key} style={{ background: '#1a1a2e' }}>
              {label} {modelCounts[key] ? `(${modelCounts[key]})` : ''}
            </option>
          ))}
        </select>
        <select
          value={filterProvider}
          onChange={(e) => setFilterProvider(e.target.value)}
          style={{
            padding: '8px 12px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '6px',
            color: '#fff',
            fontSize: '0.8rem',
            cursor: 'pointer'
          }}
        >
          <option value="all" style={{ background: '#1a1a2e' }}>全部厂商</option>
          <option value="Meta" style={{ background: '#1a1a2e' }}>Meta (Llama)</option>
          <option value="Mistral" style={{ background: '#1a1a2e' }}>Mistral AI</option>
          <option value="Qwen" style={{ background: '#1a1a2e' }}>Qwen (阿里)</option>
          <option value="Google" style={{ background: '#1a1a2e' }}>Google (Gemma)</option>
          <option value="Microsoft" style={{ background: '#1a1a2e' }}>微软 (Phi)</option>
          <option value="Stability" style={{ background: '#1a1a2e' }}>Stability AI</option>
        </select>
      </div>

      {pretraining.gpu_tflops_fp16 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '12px',
          marginBottom: '20px'
        }}>
          <div style={{
            background: 'rgba(0, 240, 255, 0.1)',
            border: '1px solid rgba(0, 240, 255, 0.2)',
            borderRadius: '8px',
            padding: '12px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>当前GPU算力</div>
            <div style={{ fontSize: '1.2rem', color: 'var(--primary-neon)', fontWeight: 'bold' }}>
              {pretraining.gpu_tflops_fp16} TFLOPS
            </div>
          </div>
          <div style={{
            background: 'rgba(0, 255, 102, 0.1)',
            border: '1px solid rgba(0, 255, 102, 0.2)',
            borderRadius: '8px',
            padding: '12px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>可预训练模型</div>
            <div style={{ fontSize: '1.2rem', color: 'var(--success-neon)', fontWeight: 'bold' }}>
              {capableModels.length} 个
            </div>
          </div>
          <div style={{
            background: 'rgba(179, 71, 255, 0.1)',
            border: '1px solid rgba(179, 71, 255, 0.2)',
            borderRadius: '8px',
            padding: '12px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>微调范围</div>
            <div style={{ fontSize: '1.2rem', color: 'var(--purple-neon)', fontWeight: 'bold' }}>
              最大 {finetuning.max_finetune_params || 0}B
            </div>
          </div>
        </div>
      )}

      <div style={{
        maxHeight: '500px',
        overflowY: 'auto',
        borderRadius: '8px',
        border: '1px solid var(--border-dim)'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
          <thead style={{ position: 'sticky', top: 0, background: 'rgba(26, 26, 46, 0.95)', zIndex: 1 }}>
            <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: '600' }}>模型</th>
              <th style={{ padding: '12px', textAlign: 'center', color: 'var(--text-muted)', fontWeight: '600' }}>参数量</th>
              <th style={{ padding: '12px', textAlign: 'center', color: 'var(--text-muted)', fontWeight: '600' }}>QLoRA</th>
              <th style={{ padding: '12px', textAlign: 'center', color: 'var(--text-muted)', fontWeight: '600' }}>LoRA</th>
              <th style={{ padding: '12px', textAlign: 'center', color: 'var(--text-muted)', fontWeight: '600' }}>全参微调</th>
              <th style={{ padding: '12px', textAlign: 'center', color: 'var(--text-muted)', fontWeight: '600' }}>预训练</th>
            </tr>
          </thead>
          <tbody>
            {filteredModels.map((model, idx) => {
              const capability = getCapabilityStatus(model);
              const vramStatus = getVRAMStatus(model.qlora_vram_gb, pretraining.available_vram_gb || 0);

              return (
                <tr
                  key={idx}
                  style={{
                    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                    background: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.02)'
                  }}
                >
                  <td style={{ padding: '10px' }}>
                    <div style={{ fontWeight: 'bold', color: '#fff' }}>{model.name}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{model.architecture}</div>
                  </td>
                  <td style={{ padding: '10px', textAlign: 'center', color: 'var(--primary-neon)', fontWeight: 'bold' }}>
                    {model.params_b}B
                  </td>
                  <td style={{ padding: '10px', textAlign: 'center' }}>
                    <span style={{ color: vramStatus.color, fontSize: '0.75rem' }}>
                      {model.qlora_vram_gb}GB
                    </span>
                  </td>
                  <td style={{ padding: '10px', textAlign: 'center' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                      {model.lora_vram_gb}GB
                    </span>
                  </td>
                  <td style={{ padding: '10px', textAlign: 'center' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                      {model.finetune_vram_gb}GB
                    </span>
                  </td>
                  <td style={{ padding: '10px', textAlign: 'center' }}>
                    {capability.status === 'unable' ? (
                      <XCircle size={16} color="var(--danger-neon)" />
                    ) : (
                      <div style={{ color: capability.color, fontSize: '0.75rem', fontWeight: 'bold' }}>
                        {capability.text}
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: '12px', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>
        显示 {filteredModels.length} / {models.total_models} 个模型
      </div>
    </div>
  );
};

export default ModelCapabilityMatrix;
