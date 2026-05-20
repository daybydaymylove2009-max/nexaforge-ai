import React, { useEffect, useState } from 'react';
import { Brain, Zap, Layers, Target, TrendingUp, Clock, CheckCircle, AlertTriangle } from 'lucide-react';

const SelfImprovementAssessment = ({ comprehensive, fetchSelfImprovement }) => {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  const assessment = comprehensive?.self_improvement_assessment || {};
  const finetuning = comprehensive?.finetuning_assessment || {};

  useEffect(() => {
    if (fetchSelfImprovement && !details) {
      setLoading(true);
      fetchSelfImprovement().then(data => {
        setDetails(data);
        setLoading(false);
      });
    }
  }, [fetchSelfImprovement, details]);

  const capabilityLevels = [
    { id: 'inference', label: '仅推理', tier: 1, color: 'var(--text-muted)' },
    { id: 'qlora', label: 'QLoRA微调', tier: 2, color: 'var(--warning-neon)' },
    { id: 'lora', label: 'LoRA微调', tier: 3, color: 'var(--primary-neon)' },
    { id: 'full_ft', label: '全参微调', tier: 4, color: '#b347ff' },
    { id: 'rlhf', label: 'RLHF训练', tier: 5, color: '#ff6b6b' },
    { id: 'distillation', label: '知识蒸馏', tier: 6, color: '#ffd93d' },
    { id: 'self_improve', label: '自进化', tier: 7, color: 'var(--success-neon)' },
  ];

  const getCurrentTier = () => {
    if (!assessment.capable) return 0;
    return Math.min(assessment.max_capability_level || 7, 7);
  };

  const currentTier = getCurrentTier();
  const currentLevel = capabilityLevels.find(l => l.tier === currentTier) || capabilityLevels[0];

  const evolutionRoadmap = [
    {
      phase: 1,
      name: '推理阶段',
      description: '部署预训练模型进行推理',
      requirements: '低显存，无需训练',
      achievable: true,
      icon: '🎯'
    },
    {
      phase: 2,
      name: 'QLoRA微调',
      description: '4-bit量化高效微调',
      requirements: `${finetuning.max_qlora_params || 0}B参数, ${finetuning.qlora_vram_estimate || 0}GB显存`,
      achievable: currentTier >= 2,
      icon: '⚡'
    },
    {
      phase: 3,
      name: 'RLHF训练',
      description: '基于人类反馈的强化学习',
      requirements: `${assessment.rlhf_vram_estimate || 0}GB显存, 批次${assessment.rlhf_batch_size || 0}`,
      achievable: currentTier >= 5,
      icon: '🧠'
    },
    {
      phase: 4,
      name: '自进化',
      description: '模型自主生成数据并学习优化',
      requirements: `${assessment.self_improve_vram_estimate || 0}GB显存, 建议多GPU`,
      achievable: currentTier >= 7,
      icon: '🚀'
    }
  ];

  const skillMatrix = [
    { skill: '文本生成', level: currentTier >= 1 ? 100 : 0, max: 100 },
    { skill: '代码生成', level: currentTier >= 1 ? 85 : 0, max: 100 },
    { skill: '数学推理', level: currentTier >= 2 ? 70 : 0, max: 100 },
    { skill: '指令遵循', level: currentTier >= 2 ? 80 : 0, max: 100 },
    { skill: '多模态理解', level: currentTier >= 3 ? 60 : 0, max: 100 },
    { skill: '长上下文', level: currentTier >= 3 ? 75 : 0, max: 100 },
    { skill: '自我纠错', level: currentTier >= 5 ? 50 : 0, max: 100 },
    { skill: '抽象推理', level: currentTier >= 6 ? 40 : 0, max: 100 },
  ];

  if (loading) {
    return (
      <div style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        正在分析进化能力...
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <Brain size={20} color="var(--primary-neon)" />
        <div>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#fff' }}>自进化能力评估</h3>
          <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            AI训练进化深度分析
          </p>
        </div>
      </div>

      <div style={{
        background: 'rgba(0, 240, 255, 0.08)',
        border: '1px solid rgba(0, 240, 255, 0.2)',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>当前进化等级</div>
            <div style={{ fontSize: '1.5rem', color: currentLevel.color, fontWeight: 'bold' }}>
              {currentLevel.label}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>能力评分</div>
            <div style={{ fontSize: '1.5rem', color: '#fff', fontWeight: 'bold' }}>
              {assessment.capability_score || 0}/100
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '4px', marginTop: '12px' }}>
          {capabilityLevels.map((level, idx) => (
            <div
              key={idx}
              style={{
                flex: 1,
                height: '8px',
                borderRadius: '4px',
                background: level.tier <= currentTier
                  ? `linear-gradient(90deg, ${level.color}, ${level.color}88)`
                  : 'rgba(255, 255, 255, 0.1)',
                boxShadow: level.tier === currentTier ? `0 0 10px ${level.color}` : 'none',
                transition: 'all 0.3s ease'
              }}
              title={level.label}
            />
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
          <span>推理</span>
          <span>自进化</span>
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <h4 style={{ fontSize: '0.9rem', color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Target size={16} color="var(--primary-neon)" />
          进化路线图
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {evolutionRoadmap.map((phase, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                gap: '16px',
                padding: '16px',
                background: phase.achievable ? 'rgba(0, 255, 102, 0.05)' : 'rgba(255, 255, 255, 0.02)',
                border: `1px solid ${phase.achievable ? 'rgba(0, 255, 102, 0.2)' : 'rgba(255, 255, 255, 0.05)'}`,
                borderRadius: '8px',
                transition: 'all 0.3s ease'
              }}
            >
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: phase.achievable ? 'rgba(0, 255, 102, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                flexShrink: 0
              }}>
                {phase.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ fontSize: '0.9rem', color: '#fff', fontWeight: 'bold' }}>{phase.name}</span>
                  {phase.achievable ? (
                    <CheckCircle size={14} color="var(--success-neon)" />
                  ) : (
                    <AlertTriangle size={14} color="var(--warning-neon)" />
                  )}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  {phase.description}
                </div>
                <div style={{ fontSize: '0.75rem', color: phase.achievable ? 'var(--success-neon)' : 'var(--warning-neon)' }}>
                  需求: {phase.requirements}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h4 style={{ fontSize: '0.9rem', color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TrendingUp size={16} color="var(--primary-neon)" />
          技能发展矩阵
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {skillMatrix.map((skill, idx) => (
            <div key={idx}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', color: '#fff' }}>{skill.skill}</span>
                <span style={{ fontSize: '0.8rem', color: skill.level > 0 ? 'var(--primary-neon)' : 'var(--text-muted)' }}>
                  {skill.level}%
                </span>
              </div>
              <div style={{
                height: '6px',
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '3px',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${skill.level}%`,
                  background: skill.level > 0
                    ? 'linear-gradient(90deg, var(--primary-neon), var(--purple-neon))'
                    : 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '3px',
                  transition: 'width 0.5s ease-out'
                }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {assessment.limitations && assessment.limitations.length > 0 && (
        <div style={{
          marginTop: '20px',
          padding: '12px',
          background: 'rgba(255, 179, 71, 0.1)',
          border: '1px solid rgba(255, 179, 71, 0.2)',
          borderRadius: '8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <AlertTriangle size={14} color="var(--warning-neon)" />
            <span style={{ fontSize: '0.8rem', color: 'var(--warning-neon)', fontWeight: 'bold' }}>
              当前限制
            </span>
          </div>
          <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {assessment.limitations.map((limitation, idx) => (
              <li key={idx} style={{ marginBottom: '4px' }}>{limitation}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SelfImprovementAssessment;
