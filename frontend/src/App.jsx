import React, { useState, useEffect, useMemo } from 'react';
import { useHardwareWebSocket } from './hooks/useHardwareWebSocket';
import { Brain, Cpu, HardDrive, Monitor, Server, Activity, Thermometer, Zap, Layers, Share2, ShieldAlert, FileText, X, ShieldCheck } from 'lucide-react';

const API_BASE = 'http://localhost:8000'; // Make sure this points to your backend

const locales = {
  en: {
    init: 'INITIALIZING NEXAFORGE...',
    connError: 'Connection Error',
    sysOnline: 'SYSTEM ONLINE',
    hwRating: 'HARDWARE RATING',
    analyzing: 'ANALYZING...',
    maxModel: 'Max Model: ',
    sysInfo: 'SYSTEM INFO',
    os: 'OS',
    arch: 'Architecture',
    uptime: 'Uptime',
    cpuProc: 'CPU PROCESSOR',
    cores: ' CORES',
    unknownCpu: 'Unknown CPU',
    totalLoad: 'Total Load',
    temp: 'TEMP',
    sysMem: 'SYSTEM MEMORY',
    ramUsage: 'RAM Usage',
    available: 'Available',
    swapUsed: 'Swap Used',
    gpu: 'GRAPHICS UNIT',
    online: 'ONLINE',
    offline: 'OFFLINE',
    vramUsage: 'VRAM Usage',
    noGpu: 'No dedicated GPU detected.',
    cudaEnv: 'CUDA ENV',
    ready: 'READY',
    na: 'N/A',
    cudaVer: 'CUDA Version',
    notInstalled: 'Not Installed',
    computeCap: 'Compute Capability',
    gpuUtil: 'GPU Utilization',
    pcieLink: 'PCIe Link',
    throttling: '⚠ THROTTLING',
    alloc: 'Allocated',
    reserved: 'Reserved',
    power: 'Power',
    aiReady: 'AI Readiness',
    packages: 'Key Packages',
    storageAdvice: 'Storage Profile',
    aiFrameworks: 'AI Frameworks',
    reportBtn: 'Generate Enterprise Report',
    reportTitle: 'Enterprise AI Diagnostic Report',
    close: 'Close',
    pkgOk: 'OK',
    pkgMissing: 'MISSING',
    currentTier: 'Your Hardware Tier',
    upgradeAdvice: 'Upgrade Path',
    targetTier: 'Target',
    modelLadder: 'Model Capability Ladder',
    loading: 'Loading diagnostic data...',
    achievable: 'Achievable',
    matrixTitle: 'Enterprise Hardware Recommendation Matrix',
    mFamily: 'Model Family',
    mParams: 'Params',
    mQlora: 'Min VRAM (QLoRA)',
    mFull: 'Min VRAM (Full FT)',
    mConsumer: 'Consumer GPU',
    mEnterprise: 'Enterprise GPU',
    mMobileTitle: 'Mobile & Edge Deployment Matrix',
    mQuant: 'Quantization',
    mRamReq: 'Min RAM',
    mDevice: 'Target Device / NPU',
    mFramework: 'Framework',
    enterpriseStorageIO: 'Enterprise Storage I/O',
    readSpeed: 'Read Speed',
    writeSpeed: 'Write Speed',
    diskUsage: 'Disk Space Usage',
    driveDetected: 'Drive Detected',
    suitableDataset: 'Suitable for dataset loading',
    checkRandomIO: 'Warning: Check random I/O speed',
    storageUnknown: 'Storage type unknown',
    computeLadderTitle: 'Compute Capability Ladder (H100 Baseline)',
    relativeCompute: 'Relative Performance'
  },
  zh: {
    init: '正在初始化 NEXAFORGE...',
    connError: '连接错误',
    sysOnline: '系统在线',
    hwRating: '硬件综合评分',
    analyzing: '正在分析...',
    maxModel: '最高支持模型: ',
    sysInfo: '系统信息',
    os: '操作系统',
    arch: '系统架构',
    uptime: '运行时间',
    cpuProc: 'CPU 处理器',
    cores: ' 核心',
    unknownCpu: '未知 CPU',
    totalLoad: '整体负载',
    temp: '温度',
    sysMem: '系统内存',
    ramUsage: '内存使用',
    available: '可用空间',
    swapUsed: '交换区使用',
    gpu: '图形处理器',
    online: '在线',
    offline: '离线',
    vramUsage: '显存使用',
    noGpu: '未检测到独立显卡。',
    cudaEnv: 'CUDA 运行环境',
    ready: '就绪',
    na: '不可用',
    cudaVer: 'CUDA 版本',
    notInstalled: '未安装',
    computeCap: '计算能力',
    gpuUtil: 'GPU 利用率',
    pcieLink: 'PCIe 总线',
    throttling: '⚠ 触发降频',
    alloc: '已分配',
    reserved: '已保留(碎片)',
    power: '功耗',
    aiReady: 'AI 训练就绪度',
    packages: '核心加速库',
    storageAdvice: '存储环境评估',
    aiFrameworks: 'AI 软件栈',
    reportBtn: '生成企业级 AI 诊断报告',
    reportTitle: '企业级 AI 大模型训练诊断报告',
    close: '关闭',
    currentTier: '当前硬件阶梯定级',
    upgradeAdvice: '突破升阶指南',
    targetTier: '进阶目标',
    modelLadder: '大模型训练能力阶梯图',
    loading: '正在生成深层诊断数据...',
    achievable: '可支持',
    matrixTitle: '企业级大模型算力与硬件推荐矩阵',
    mFamily: '模型家族',
    mParams: '参数量',
    mQlora: '最低显存 (QLoRA)',
    mFull: '最低显存 (全参微调)',
    mConsumer: '推荐消费级显卡',
    mEnterprise: '推荐企业级 GPU',
    mMobileTitle: '移动/边缘端大模型部署评估矩阵',
    mQuant: '量化级别',
    mRamReq: '运行内存底线',
    mDevice: '适配芯片/设备',
    mFramework: '推荐推理框架',
    enterpriseStorageIO: '企业级存储 I/O',
    readSpeed: '读取速度',
    writeSpeed: '写入速度',
    diskUsage: '磁盘空间占用',
    driveDetected: '检测到驱动器',
    suitableDataset: '适合数据集加载',
    checkRandomIO: '警告：请检查随机 I/O 性能',
    storageUnknown: '存储类型未知',
    computeLadderTitle: '业界主流算力硬件对比阶梯 (以 H100 为基准)',
    relativeCompute: '相对算力性能',
    uptime: '系统运行时间',
    heartbeat: '心跳活跃度',
    industrialMode: '工业级生产环境模式',
    secure: '加密安全连接',
    seconds: '秒',
    pkgOk: '已就绪',
    pkgMissing: '缺失',
    trendTitle: '算力与资源负载趋势 (过去 1 小时)',
    scoreTrend: '算力评分',
    cpuTrend: 'CPU 负载',
    vramTrend: '显存占用'
  }
};

const packageDescriptions = {
  'transformers': '模型架构库',
  'datasets': '数据集工具',
  'accelerate': '分布式加速',
  'peft': '参数高效微调',
  'bitsandbytes': '8/4-bit 量化',
  'flash_attn': 'Flash 闪速注意',
  'xformers': '内存高效算子',
  'deepspeed': '大规模训练框架'
};

const getLang = () => {
  // Use navigator language, fallback to en
  if (typeof navigator === 'undefined') return 'en';
  const lang = navigator.language || navigator.userLanguage;
  return lang.toLowerCase().startsWith('zh') ? 'zh' : 'en';
};

const t = (key) => {
  return locales[getLang()][key] || locales['en'][key] || key;
};

// --- Helper Functions ---
function getTempClass(temp) {
  if (!temp || typeof temp !== 'string') return 'temp-normal';
  const val = parseInt(temp);
  if (isNaN(val)) return 'temp-normal';
  if (val >= 80) return 'temp-danger';
  if (val >= 60) return 'temp-warn';
  return 'temp-normal';
}

function formatUptime(seconds) {
  if (!seconds || seconds <= 0) return '--';
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  
  const isZh = getLang() === 'zh';
  const dStr = isZh ? '天 ' : 'd ';
  const hStr = isZh ? '小时 ' : 'h ';
  const mStr = isZh ? '分钟 ' : 'm ';
  const sStr = isZh ? '秒' : 's';
  
  let result = '';
  if (d > 0) result += `${d}${dStr}`;
  if (h > 0 || d > 0) result += `${h}${hStr}`;
  if (m > 0 || h > 0 || d > 0) result += `${m}${mStr}`;
  result += `${s}${sStr}`;
  
  return result;
}

// --- Components ---

const ScoreRing = React.memo(({ score }) => {
  return (
    <div className="score-ring-container">
      <svg width="180" height="180" viewBox="0 0 180 180">
        <circle cx="90" cy="90" r="80" fill="none" stroke="rgba(45, 75, 110, 0.4)" strokeWidth="10" />
        <circle 
          cx="90" cy="90" r="80" 
          fill="none" 
          stroke="url(#neonGradient)" 
          strokeWidth="10" 
          strokeDasharray={`${(score / 100) * 502} 502`} 
          strokeLinecap="round" 
          transform="rotate(-90 90 90)"
          style={{ transition: 'stroke-dasharray 1s ease-out' }}
        />
        <defs>
          <linearGradient id="neonGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00f0ff" />
            <stop offset="100%" stopColor="#b026ff" />
          </linearGradient>
        </defs>
      </svg>
      <div className="score-value">{score || 0}</div>
    </div>
  );
});

const ProgressBar = React.memo(({ label, percent, valueStr, type }) => (
  <div className="progress-container">
    <div className="progress-header">
      <span>{label}</span>
      <span>{valueStr || `${Math.round(percent)}%`}</span>
    </div>
    <div className="progress-track">
      <div className={`progress-fill fill-${type}`} style={{ width: `${percent}%` }}></div>
    </div>
  </div>
));

const InfoItem = React.memo(({ label, value, highlight }) => (
  <div className="info-item">
    <span className="info-label">{label}</span>
    <span className={`info-value ${highlight ? 'highlight' : ''}`}>{value}</span>
  </div>
));

// --- Main App ---

const ComputeLadder = ({ data }) => {
  if (!data || data.length === 0) return null;
  
  return (
    <div style={{ marginTop: '24px', padding: '20px', background: 'rgba(0,0,0,0.2)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
        <Activity size={18} color="var(--primary-neon)" />
        <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', margin: 0 }}>
          {t('computeLadderTitle')}
        </h3>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {data.map((item, idx) => (
          <div key={idx} style={{ position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.75rem' }}>
              <span style={{ 
                color: item.is_current ? 'var(--primary-neon)' : '#fff', 
                fontWeight: item.is_current ? '800' : '400',
                letterSpacing: item.is_current ? '0.5px' : 'normal'
              }}>
                {item.name} {item.is_current && ' [YOU]'}
              </span>
              <span style={{ color: item.is_current ? 'var(--primary-neon)' : 'var(--text-muted)' }}>{item.score}%</span>
            </div>
            <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
              <div 
                style={{ 
                  height: '100%', 
                  width: `${item.display_percent || item.score}%`, 
                  background: item.is_current 
                    ? 'linear-gradient(90deg, var(--primary-neon), #b347ff)' 
                    : item.tier === 'Enterprise' ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)',
                  boxShadow: item.is_current ? '0 0 15px rgba(0, 240, 255, 0.4)' : 'none',
                  borderRadius: '3px'
                }} 
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const TrendChart = ({ data }) => {
  if (!data || data.length < 2) return (
    <div style={{ height: '180px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
      {t('analyzing')}
    </div>
  );

  const padding = 30;
  const width = 800;
  const height = 180;
  const points = data.length;
  
  const getPath = (key, color, max = 100) => {
    const coords = data.map((d, i) => {
      const x = padding + (i * (width - 2 * padding)) / (points - 1);
      const y = height - padding - (d[key] / max) * (height - 2 * padding);
      return `${x},${y}`;
    });
    return (
      <path
        d={`M ${coords.join(' L ')}`}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ filter: `drop-shadow(0 0 4px ${color}66)` }}
      />
    );
  };

  return (
    <div style={{ width: '100%', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
        <h3 style={{ fontSize: '0.85rem', color: 'var(--text-main)', margin: 0 }}>
          <Activity size={14} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          {t('trendTitle')}
        </h3>
        <div style={{ display: 'flex', gap: '15px', fontSize: '0.7rem' }}>
          <span style={{ color: 'var(--primary-neon)' }}>● {t('scoreTrend')}</span>
          <span style={{ color: 'var(--purple-neon)' }}>● {t('cpuTrend')}</span>
          <span style={{ color: 'var(--success-neon)' }}>● {t('vramTrend')}</span>
        </div>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto' }}>
        {/* Grid Lines */}
        <line x1={padding} y1={height-padding} x2={width-padding} y2={height-padding} stroke="var(--border-dim)" strokeWidth="1" />
        <line x1={padding} y1={padding} x2={padding} y2={height-padding} stroke="var(--border-dim)" strokeWidth="1" />
        
        {/* Paths */}
        {getPath('score', 'var(--primary-neon)', 100)}
        {getPath('cpu', 'var(--purple-neon)', 100)}
        {getPath('vram', 'var(--success-neon)', 100)}
      </svg>
    </div>
  );
};

const ReportModal = ({ show, onClose, data }) => {
  if (!show) return null;
  return (
    <div className="modal-overlay">
      <div className="glass-panel modal-content animate-in">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '16px' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--primary-neon)' }}>
            <FileText size={24} /> {t('reportTitle')}
          </h2>
          <button className="btn-icon" onClick={onClose}><X size={24} /></button>
        </div>

        {!data ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="spinner" style={{ margin: '0 auto 16px' }}></div>
            <p style={{ color: 'var(--text-muted)' }}>{t('loading')}</p>
          </div>
        ) : (
          <div className="report-grid">
            {/* Top Section */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
              <div className="report-card">
                <h3 style={{ color: 'var(--text-muted)', marginBottom: '12px', fontSize: '0.9rem' }}>{t('currentTier')}</h3>
                <h1 style={{ color: '#fff', fontSize: '1.8rem', marginBottom: '8px' }}>
                  {getLang() === 'zh' ? data.current_tier.name : data.current_tier.name_en}
                </h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  {data.current_tier.desc}
                </p>
              </div>
              <div className="report-card" style={{ background: data.upgrade_advice ? 'rgba(255, 179, 71, 0.05)' : 'rgba(0, 255, 102, 0.05)' }}>
                <h3 style={{ color: 'var(--text-muted)', marginBottom: '12px', fontSize: '0.9rem' }}>{t('upgradeAdvice')}</h3>
                {data.upgrade_advice ? (
                  <>
                    <p style={{ color: '#ffb347', fontSize: '0.9rem', marginBottom: '8px' }}>
                      {getLang() === 'zh' ? data.upgrade_advice.message : data.upgrade_advice.message_en}
                    </p>
                    <p style={{ color: '#fff', fontSize: '0.85rem' }}>
                      {t('targetTier')}: {getLang() === 'zh' ? data.upgrade_advice.target_tier : data.upgrade_advice.target_tier_en}
                    </p>
                  </>
                ) : (
                  <p style={{ color: 'var(--success-neon)' }}>You are at the highest tier!</p>
                )}
              </div>
            </div>

            {/* Ladder Chart */}
            <h3 style={{ color: 'var(--text-muted)', marginBottom: '16px', fontSize: '0.9rem' }}>{t('modelLadder')}</h3>
            <div className="ladder-chart">
              {[...data.ladder_chart].reverse().map((tier, idx) => (
                <div key={idx} className={`ladder-step ${tier.is_current ? 'current' : ''} ${!tier.achievable ? 'locked' : ''}`}>
                  <div className="step-header">
                    <span className="step-badge">{getLang() === 'zh' ? tier.name : tier.name_en}</span>
                    {tier.is_current && <span className="status-badge" style={{ background: 'var(--primary-neon)', color: '#000', padding: '2px 8px' }}>Current</span>}
                    {tier.achievable && !tier.is_current && <span style={{ color: 'var(--success-neon)', fontSize: '0.75rem' }}>✓ {t('achievable')}</span>}
                  </div>
                  <div className="step-body">
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                      VRAM: {tier.vram_req}GB+ | RAM: {tier.ram_req}GB+
                    </div>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {tier.models.map((m, i) => (
                        <span key={i} style={{ background: 'rgba(255,255,255,0.05)', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', color: '#fff' }}>
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Hardware Matrix Table */}
            {data.hardware_matrix && data.hardware_matrix.length > 0 && (
              <div style={{ marginTop: '32px' }}>
                <h3 style={{ color: 'var(--text-muted)', marginBottom: '16px', fontSize: '0.9rem' }}>{t('matrixTitle')}</h3>
                <div className="matrix-table-wrapper" style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid var(--border-dim)' }}>
                  <table className="matrix-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead>
                      <tr style={{ background: 'rgba(255,255,255,0.05)', textAlign: 'left', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '12px' }}>{t('mFamily')}</th>
                        <th style={{ padding: '12px' }}>{t('mParams')}</th>
                        <th style={{ padding: '12px' }}>{t('mQlora')}</th>
                        <th style={{ padding: '12px' }}>{t('mFull')}</th>
                        <th style={{ padding: '12px' }}>{t('mConsumer')}</th>
                        <th style={{ padding: '12px' }}>{t('mEnterprise')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.hardware_matrix.map((row, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)' }}>
                          <td style={{ padding: '12px', color: '#fff', fontWeight: 'bold' }}>{row.model_family}</td>
                          <td style={{ padding: '12px', color: 'var(--primary-neon)' }}>{row.params}</td>
                          <td style={{ padding: '12px', color: 'var(--text-muted)' }}>{row.qlora_vram}</td>
                          <td style={{ padding: '12px', color: 'var(--text-muted)' }}>{row.full_vram}</td>
                          <td style={{ padding: '12px', color: '#ffb347' }}>{row.consumer_gpu}</td>
                          <td style={{ padding: '12px', color: 'var(--success-neon)' }}>{row.enterprise_gpu}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Mobile & Edge Matrix Table */}
            {data.mobile_matrix && data.mobile_matrix.length > 0 && (
              <div style={{ marginTop: '32px' }}>
                <h3 style={{ color: 'var(--text-muted)', marginBottom: '16px', fontSize: '0.9rem' }}>{t('mMobileTitle')}</h3>
                <div className="matrix-table-wrapper" style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid var(--border-dim)' }}>
                  <table className="matrix-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead>
                      <tr style={{ background: 'rgba(255,255,255,0.05)', textAlign: 'left', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '12px' }}>{t('mFamily')}</th>
                        <th style={{ padding: '12px' }}>{t('mParams')}</th>
                        <th style={{ padding: '12px' }}>{t('mQuant')}</th>
                        <th style={{ padding: '12px' }}>{t('mRamReq')}</th>
                        <th style={{ padding: '12px' }}>{t('mDevice')}</th>
                        <th style={{ padding: '12px' }}>{t('mFramework')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.mobile_matrix.map((row, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)' }}>
                          <td style={{ padding: '12px', color: '#fff', fontWeight: 'bold' }}>{row.model_family}</td>
                          <td style={{ padding: '12px', color: 'var(--primary-neon)' }}>{row.params}</td>
                          <td style={{ padding: '12px', color: '#ffb347' }}>{row.quantization}</td>
                          <td style={{ padding: '12px', color: 'var(--success-neon)' }}>{row.ram_req}</td>
                          <td style={{ padding: '12px', color: '#fff' }}>{row.target_device}</td>
                          <td style={{ padding: '12px', color: 'var(--text-muted)' }}>{row.framework}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default function App() {
  const { data, isConnected, error } = useHardwareWebSocket(API_BASE + '/ws');
  
  const [showReport, setShowReport] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [historyData, setHistoryData] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(API_BASE + '/api/stats/history');
        const json = await res.json();
        if (Array.isArray(json)) setHistoryData(json);
      } catch (err) {
        console.error("Fetch history failed", err);
      }
    };
    
    fetchHistory();
    const timer = setInterval(fetchHistory, 10000); // 10秒刷新一次
    return () => clearInterval(timer);
  }, []);

  const fetchEnterpriseReport = async () => {
    setShowReport(true);
    setReportData(null);
    try {
      const res = await fetch(API_BASE + '/api/report/enterprise?api_key=NEXA-PRO-2026');
      const json = await res.json();
      setReportData(json);
    } catch (err) {
      console.error(err);
    }
  };
  
  const snapshot = data?.snapshot || {};
  const recommendations = data?.recommendations || {};
  
  const score = recommendations.score || 0;
  const cpu = snapshot.cpu || {};
  const mem = snapshot.memory || {};
  const gpuInfo = snapshot.gpu || {};
  const sys = snapshot.system || {};
  const temp = snapshot.temperature || {};
  const cuda = snapshot.cuda || {};
  const disk = snapshot.disk || {};

  if (error && !isConnected) {
    return (
      <div className="loading-screen">
        <ShieldAlert size={64} color="#ff2a2a" style={{ marginBottom: 20 }} />
        <h2 style={{ color: '#ff2a2a' }}>{t('connError')}</h2>
        <p style={{ color: 'var(--text-muted)' }}>{error}</p>
      </div>
    );
  }

  if (!data && isConnected) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <h3 style={{ color: 'var(--primary-neon)' }}>{t('init')}</h3>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="app">
      <header className="top-nav">
        <div className="nav-brand">
          <Brain size={32} color="var(--primary-neon)" />
          <div className="brand-text">
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <h1>NEXAFORGE AI</h1>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 'bold' }}>v{data.snapshot.version || '0.1.0'}</span>
            </div>
            <div style={{ display: 'flex', gap: '8px', fontSize: '0.65rem', color: 'var(--success-neon)', opacity: 0.8 }}>
              <ShieldCheck size={12} /> {t('industrialMode')}
            </div>
          </div>
        </div>
        <div className="nav-status-container" style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div className="pro-stats" style={{ display: 'flex', gap: '16px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <div className="stat-item" style={{ display: 'flex', alignItems: 'center' }}>
              <span className="heartbeat-dot"></span>
              {t('heartbeat')}: <span style={{ color: '#fff', marginLeft: '4px' }}>{data.snapshot.heartbeat || 0}</span>
            </div>
            <div className="stat-item">
              <Activity size={12} style={{ marginRight: '4px' }} />
              {t('uptime')}: <span style={{ color: '#fff' }}>{formatUptime(data.snapshot.uptime_seconds)}</span>
            </div>
          </div>
          <div className="nav-status">
          <div className="status-badge">
            <span className="status-dot"></span>
            {t('sysOnline')}
          </div>
        </div>
      </div>
    </header>

      <main className="main-content">
        {/* Sidebar */}
        <aside className="dashboard-sidebar">
          <div className="glass-panel score-dashboard animate-in" style={{ animationDelay: '0.1s' }}>
            <h3 style={{ marginBottom: '24px', color: 'var(--text-muted)' }}>{t('hwRating')}</h3>
            <ScoreRing score={Math.round(score)} />
            <h2 style={{ color: '#fff', marginBottom: '8px' }}>
              {recommendations.modes?.[recommendations.recommended_mode]?.[getLang() === 'zh' ? 'name' : 'name_en'] || t('analyzing')}
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              {recommendations.model_recommendation?.max_model_size ? `${t('maxModel')}${recommendations.model_recommendation.max_model_size}` : ''}
            </p>
          </div>

          <div className="glass-panel hw-card animate-in" style={{ gridColumn: 'span 2', padding: '24px' }}>
            <TrendChart data={historyData} />
          </div>

          <div className="glass-panel hw-card animate-in" style={{ animationDelay: '0.2s' }}>
            <div className="hw-card-header">
              <div className="hw-title"><Server className="hw-icon" /> {t('sysInfo')}</div>
            </div>
            <div className="info-list">
              <InfoItem label={t('os')} value={sys.os_display || sys.os} />
              <InfoItem label={t('arch')} value={sys.architecture} />
              <InfoItem label={t('uptime')} value={formatUptime(sys.uptime)} highlight />
              <InfoItem label="Python" value={sys.python_version} />
            </div>
          </div>
        </aside>

        {/* Main Grid */}
        <div className="hardware-grid">
          {/* CPU Card */}
          <div className="glass-panel hw-card animate-in" style={{ animationDelay: '0.3s' }}>
            <div className="hw-card-header">
              <div className="hw-title"><Cpu className="hw-icon" /> {t('cpuProc')}</div>
              <div style={{display: 'flex', gap: '8px'}}>
                {snapshot.numa_nodes > 1 && <span className="hw-badge" style={{borderColor: '#b347ff', color: '#b347ff', background: 'rgba(179, 71, 255, 0.1)'}}>NUMA: {snapshot.numa_nodes}</span>}
                <span className="hw-badge">{cpu.count || '--'}{t('cores')}</span>
              </div>
            </div>
            <p style={{ color: 'var(--text-muted)', marginBottom: '16px', fontSize: '0.9rem' }}>
              {cpu.model || t('unknownCpu')} {cpu.architecture ? `(${cpu.architecture})` : ''}
            </p>
            <ProgressBar label={t('totalLoad')} percent={cpu.percent} type="cpu" />
            <div className="temp-grid">
              <div className="temp-item">
                <Thermometer size={20} color="var(--text-muted)" />
                <div className={`temp-value ${getTempClass(temp.cpu)}`}>{temp.cpu || '--°C'}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('temp')}</div>
              </div>
              <div className="temp-item">
                <Activity size={20} color="var(--text-muted)" />
                <div className="temp-value" style={{ color: 'var(--primary-neon)' }}>{Math.round(cpu.freq_current || 0)}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>MHz</div>
              </div>
            </div>
          </div>

          {/* Memory Card */}
          <div className="glass-panel hw-card animate-in" style={{ animationDelay: '0.4s' }}>
            <div className="hw-card-header">
              <div className="hw-title"><Layers className="hw-icon" /> {t('sysMem')}</div>
              <span className="hw-badge">{(mem.total || 0).toFixed(1)} GB</span>
            </div>
            <ProgressBar 
              label={t('ramUsage')} 
              percent={mem.percent} 
              valueStr={`${(mem.used || 0).toFixed(1)} / ${(mem.total || 0).toFixed(1)} GB`}
              type="mem" 
            />
            <div className="info-list" style={{ marginTop: '20px' }}>
              <InfoItem label={t('available')} value={`${(mem.available || 0).toFixed(1)} GB`} highlight />
              <InfoItem label={t('swapUsed')} value={`${(mem.swap_used || 0).toFixed(1)} GB`} />
            </div>
          </div>

          {/* GPU Card */}
          <div className="glass-panel hw-card animate-in" style={{ animationDelay: '0.5s' }}>
            <div className="hw-card-header">
              <div className="hw-title"><Monitor className="hw-icon" /> {t('gpu')}</div>
              <div style={{display: 'flex', gap: '8px'}}>
                {snapshot.gpu_topology?.nvlink_detected && (
                  <span className="hw-badge" style={{ borderColor: '#b347ff', color: '#b347ff', background: 'rgba(179, 71, 255, 0.1)' }}>
                    NVLink Active
                  </span>
                )}
                {snapshot.gpu_topology?.topology_type && (
                  <span className="hw-badge" style={{ fontSize: '0.65rem', borderColor: 'rgba(255,255,255,0.2)', opacity: 0.8 }}>
                    {snapshot.gpu_topology.topology_type}
                  </span>
                )}
                <span className="hw-badge" style={{ borderColor: 'var(--success-neon)', color: 'var(--success-neon)', background: 'rgba(0, 255, 102, 0.1)' }}>
                  {gpuInfo.available ? t('online') : t('offline')}
                </span>
              </div>
            </div>
            {gpuInfo.devices && gpuInfo.devices.length > 0 ? (
              gpuInfo.devices.map((g, idx) => {
                let badgeStyle = { borderColor: 'var(--primary-neon)', color: 'var(--primary-neon)', background: 'rgba(0, 240, 255, 0.1)' };
                let vendorName = 'NVIDIA CUDA';
                if (g.vendor === 'amd') {
                  badgeStyle = { borderColor: '#ff2a2a', color: '#ff2a2a', background: 'rgba(255, 42, 42, 0.1)' };
                  vendorName = 'AMD ROCm';
                } else if (g.vendor === 'huawei') {
                  badgeStyle = { borderColor: '#ffb347', color: '#ffb347', background: 'rgba(255, 179, 71, 0.1)' };
                  vendorName = 'HUAWEI Ascend';
                }

                return (
                  <div key={idx} style={{ marginBottom: idx < gpuInfo.devices.length - 1 ? '20px' : '0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                      <p style={{ color: 'var(--primary-neon)', fontSize: '0.9rem', fontWeight: '600', margin: 0 }}>
                        {g.name}
                      </p>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <span className="hw-badge" style={badgeStyle}>{vendorName}</span>
                        {g.pcie_link && <span className="hw-badge" style={{fontSize: '0.65rem'}}>{g.pcie_link}</span>}
                      </div>
                    </div>
                  
                  <ProgressBar 
                    label={t('vramUsage')} 
                    percent={(g.memory_used / g.memory_total) * 100 || ((g.memory_allocated + g.memory_reserved) / g.memory_total) * 100 || 0} 
                    valueStr={`${g.memory_used?.toFixed(1) || (g.memory_allocated + g.memory_reserved)?.toFixed(1) || 0} / ${g.memory_total?.toFixed(1) || 0} GB`}
                    type="gpu" 
                  />
                  
                  {(g.memory_reserved > 0 || g.memory_allocated > 0) && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      <span>{t('alloc')}: {g.memory_allocated?.toFixed(1)} GB</span>
                      <span style={{ color: '#ffb347' }}>{t('reserved')}: {g.memory_reserved?.toFixed(1)} GB</span>
                      {g.vram_fragmentation_ratio !== undefined && (
                        <span style={{ color: g.vram_fragmentation_ratio > 0.1 ? '#ff2a2a' : 'var(--text-muted)', fontWeight: g.vram_fragmentation_ratio > 0.1 ? 'bold' : 'normal' }}>
                          碎片率: {(g.vram_fragmentation_ratio * 100).toFixed(1)}%
                        </span>
                      )}
                    </div>
                  )}

                  <div className="temp-grid" style={{ marginTop: '12px' }}>
                    <div className="temp-item" style={{ padding: '8px' }}>
                      <Thermometer size={16} color="var(--text-muted)" />
                      <div className={`temp-value ${getTempClass(temp.gpu)}`} style={{ fontSize: '1.1rem' }}>{temp.gpu || '--°C'}</div>
                    </div>
                    {g.power_usage > 0 && (
                      <div className="temp-item" style={{ padding: '8px' }}>
                        <Activity size={16} color="var(--text-muted)" />
                        <div className="temp-value" style={{ fontSize: '1.1rem', color: '#fff' }}>{Math.round(g.power_usage)}W</div>
                      </div>
                    )}
                  </div>
                  {g.is_throttling && (
                    <div style={{ color: '#ff2a2a', fontSize: '0.8rem', fontWeight: 'bold', marginTop: '8px', animation: 'pulse 1s infinite' }}>
                      {t('throttling')}
                    </div>
                  )}
                </div>
                );
              })
            ) : (
              <p style={{ color: 'var(--text-muted)' }}>{t('noGpu')}</p>
            )}
            
            {snapshot.gpu_topology?.bottlenecks?.length > 0 && (
              <div style={{ marginTop: '16px', padding: '10px', background: 'rgba(255, 42, 42, 0.08)', borderRadius: '6px', border: '1px solid rgba(255, 42, 42, 0.2)' }}>
                {snapshot.gpu_topology.bottlenecks.map((b, i) => (
                  <div key={i} style={{ fontSize: '0.7rem', color: '#ff5555', marginBottom: i < snapshot.gpu_topology.bottlenecks.length -1 ? '4px' : 0 }}>
                    ⚠ {b}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="glass-panel hw-card animate-in" style={{ animationDelay: '0.6s' }}>
            <div className="hw-card-header">
              <div className="hw-title"><Zap className="hw-icon" /> {t('cudaEnv')} & Storage I/O</div>
              <span className={`hw-badge ${cuda.cuda_available ? '' : 'hw-badge-offline'}`}>
                {cuda.cuda_available ? t('ready') : t('na')}
              </span>
            </div>
            <div className="info-list" style={{ marginBottom: '16px' }}>
              <InfoItem label={t('cudaVer')} value={cuda.cuda_version || t('notInstalled')} />
              <InfoItem label="cuDNN" value={cuda.cudnn_version || '--'} />
            </div>
            
            <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '16px' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>
                {t('enterpriseStorageIO')}
              </div>
              
              {disk.main && (
                <div style={{ marginBottom: '16px' }}>
                  <ProgressBar 
                    label={t('diskUsage')} 
                    percent={disk.main.percent} 
                    valueStr={`${disk.main.used?.toFixed(1)} / ${disk.main.total?.toFixed(1)} GB`}
                    type="mem" 
                  />
                </div>
              )}

              <div className="info-list">
                <InfoItem label={t('readSpeed')} value={`${disk.read_mbs?.toFixed(1) || 0} MB/s`} highlight />
                <InfoItem label={t('writeSpeed')} value={`${disk.write_mbs?.toFixed(1) || 0} MB/s`} />
              </div>
            </div>
          </div>

          {/* AI Readiness Card */}
          <div className="glass-panel hw-card animate-in" style={{ animationDelay: '0.7s' }}>
            <div className="hw-card-header">
              <div className="hw-title"><Brain className="hw-icon" /> {t('aiReady')}</div>
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>
                {t('packages')}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                {snapshot.ai_frameworks?.python_packages?.slice(0, 8).map((pkg, idx) => (
                  <div key={idx} style={{ 
                    display: 'flex', justifyContent: 'space-between', 
                    fontSize: '0.75rem', padding: '4px 8px',
                    background: 'rgba(255,255,255,0.03)', borderRadius: '4px'
                  }}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <span style={{ color: pkg.available ? '#fff' : 'var(--text-muted)', fontWeight: 'bold' }}>{pkg.name}</span>
                      {getLang() === 'zh' && packageDescriptions[pkg.name] && (
                        <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          {packageDescriptions[pkg.name]}
                        </span>
                      )}
                    </div>
                    <span style={{ color: pkg.available ? 'var(--success-neon)' : 'var(--danger-neon)', fontWeight: 'bold' }}>
                      {pkg.available ? t('pkgOk') : t('pkgMissing')}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '16px' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>
                {t('storageAdvice')}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#fff' }}>
                {disk.main?.fstype ? (
                  <>
                    <span style={{ color: 'var(--primary-neon)' }}>{disk.main.type && disk.main.type !== 'Unknown' ? disk.main.type : disk.main.fstype}</span> {t('driveDetected')}. 
                    {(disk.main.type?.toLowerCase().includes('ssd') || disk.main.fstype.toLowerCase().includes('ext4') || disk.main.fstype.toLowerCase().includes('ntfs')) 
                      ? ` ${t('suitableDataset')}.` 
                      : ` ${t('checkRandomIO')}.`}
                  </>
                ) : t('storageUnknown')}
              </div>
              
              {snapshot.storage_prediction && snapshot.storage_prediction.risk !== 'healthy' && (
                <div style={{ 
                  marginTop: '10px', padding: '6px 10px', 
                  fontSize: '0.7rem', borderRadius: '4px',
                  background: snapshot.storage_prediction.risk === 'critical' ? 'rgba(255, 42, 42, 0.1)' : 'rgba(255, 179, 71, 0.1)',
                  border: `1px solid ${snapshot.storage_prediction.risk === 'critical' ? 'var(--danger-neon)' : 'var(--warning-neon)'}`,
                  color: snapshot.storage_prediction.risk === 'critical' ? 'var(--danger-neon)' : 'var(--warning-neon)'
                }}>
                  ⚠ {snapshot.storage_prediction.message}
                </div>
              )}
            </div>
            
            <button className="btn-primary" onClick={fetchEnterpriseReport}>
              <FileText size={18} /> {t('reportBtn')}
            </button>
          </div>

          {/* Compute Ladder Card (Prominent Position) */}
          <div className="glass-panel hw-card animate-in" style={{ gridColumn: 'span 2', animationDelay: '0.8s' }}>
            <ComputeLadder data={snapshot.compute_ladder} />
          </div>

        </div>
      </main>

      <ReportModal show={showReport} onClose={() => setShowReport(false)} data={reportData} />
    </div>
  );
}
