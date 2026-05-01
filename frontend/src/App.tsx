import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  Play, Square, Upload, Settings, Activity, Terminal as TerminalIcon, 
  Database, CheckCircle2, AlertCircle, Cpu, Zap, ShieldCheck, BarChart3, 
  Search, FileSearch, Box, Save, Loader2, Gauge, Timer, Cpu as CpuIcon, 
  HardDrive, LayoutDashboard, Microscope, Shield, Sliders, Wand2, Star
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';

const API_BASE = 'http://localhost:8000';

interface TrainLog {
  step: number;
  total_steps?: number;
  loss: number;
  learning_rate: number;
  epoch: number;
  status: string;
  message?: string;
}

interface EnvReport {
    gpu: string;
    vram: string;
    cap: string;
    count: number;
    level: string;
    notes: string[];
}

const App: React.FC = () => {
  const [config, setConfig] = useState({
    dataset_path: 'dataset.jsonl',
    epochs: 3,
    learning_rate: 0.0002,
    use_cpu: false,
    batch_size: 2,
    lora_r: 16,
    lora_alpha: 32,
    is_smart: true
  });
  
  const [isTraining, setIsTraining] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [chartData, setChartData] = useState<any[]>([]);
  const [currentMetrics, setCurrentMetrics] = useState<TrainLog | null>(null);
  const [envReport, setEnvReport] = useState<EnvReport | null>(null);
  const [isScanning, setIsScanning] = useState(true);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  
  const [steps, setSteps] = useState([
    { id: 'analyzing', label: '环境分析', status: 'pending', icon: <Search size={16} /> },
    { id: 'data_check', label: '数据体检', status: 'pending', icon: <FileSearch size={16} /> },
    { id: 'loading_model', label: '模型加载', status: 'pending', icon: <Box size={16} /> },
    { id: 'training', label: '模型训练', status: 'pending', icon: <Zap size={16} /> },
    { id: 'saving', label: '权重保存', status: 'pending', icon: <Save size={16} /> }
  ]);

  const consoleRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // 初始化扫描环境
  useEffect(() => {
    const scanEnv = async () => {
        setIsScanning(true);
        try {
            const res = await axios.get(`${API_BASE}/api/env/scan`);
            setEnvReport(res.data);
            addLog(`✅ 智核环境扫描就绪，炼制评级: ${res.data.level}`, 'success');
        } catch (error) {
            addLog('❌ 智核扫描接口响应异常，请检查后端状态', 'error');
        } finally {
            setIsScanning(false);
        }
    };
    scanEnv();
  }, []);

  useEffect(() => {
    if (consoleRef.current) consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
  }, [logs]);

  const updateStepStatus = (id: string, status: 'pending' | 'active' | 'completed' | 'error') => {
    setSteps(prev => prev.map(step => (step.id === id ? { ...step, status } : step)));
  };

  const onStartTraining = async () => {
    try {
      setLogs(['🚀 智核引擎启动，进入炼制模式...']);
      setChartData([]);
      setCurrentMetrics(null);
      setSteps(s => s.map(step => ({...step, status: 'pending'})));
      
      const response = await axios.post(`${API_BASE}/api/train/start`, config);
      setIsTraining(true);
      addLog('炼制指令下达成功', 'success');

      if (eventSourceRef.current) eventSourceRef.current.close();
      const es = new EventSource(`${API_BASE}/api/train/stream`);
      eventSourceRef.current = es;

      es.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleProgressUpdate(data);
      };

      es.onerror = () => { addLog('连接异常', 'error'); es.close(); };
    } catch (error: any) { addLog(`启动失败: ${error.message}`, 'error'); }
  };

  const onStopTraining = async () => {
    try {
      await axios.post(`${API_BASE}/api/train/stop`);
      if (eventSourceRef.current) eventSourceRef.current.close();
      setIsTraining(false);
      addLog('炼制已停止', 'warning');
      setSteps(s => s.map(step => step.status === 'active' ? {...step, status: 'error'} : step));
    } catch (error) { addLog('终止失败', 'error'); }
  };

  const handleProgressUpdate = (data: any) => {
    if (data.status === 'analyzing') {
      updateStepStatus('analyzing', 'active');
      addLog(`🔍 ${data.message}`);
    } else if (data.status === 'env_report') {
        setEnvReport(data);
        updateStepStatus('analyzing', 'completed');
    } else if (data.message && data.message.includes('体检')) {
      updateStepStatus('data_check', 'active');
    } else if (data.status === 'info' && data.message.includes('修复')) {
        updateStepStatus('data_check', 'completed');
    } else if (data.message && data.message.includes('加载')) {
      updateStepStatus('loading_model', 'active');
    } else if (data.status === 'starting') {
      updateStepStatus('loading_model', 'completed');
      updateStepStatus('training', 'active');
      addLog(data.message, 'success');
    } else if (data.status === 'training') {
      setChartData(prev => [...prev, { step: data.step, loss: parseFloat(data.loss.toFixed(4)), epoch: data.epoch }]);
      setCurrentMetrics(data);
    } else if (data.status === 'completed') {
      setIsTraining(false);
      updateStepStatus('training', 'completed');
      updateStepStatus('saving', 'completed');
      addLog('🎉 炼制圆满完成！', 'success');
      if (eventSourceRef.current) eventSourceRef.current.close();
    } else if (data.status === 'error') {
      setIsTraining(false);
      addLog(`❌ 炼制中断: ${data.message}`, 'error');
      if (eventSourceRef.current) eventSourceRef.current.close();
    }
  };

  const addLog = (msg: string, type: string = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${msg}`]);
  };

  const onFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post(`${API_BASE}/api/data/upload`, formData);
      setConfig(prev => ({ ...prev, dataset_path: res.data.path }));
      setUploadStatus('success');
      addLog(`✅ 数据集就绪: ${file.name}`, 'success');
    } catch (error) { setUploadStatus('error'); addLog('❌ 导入失败', 'error'); }
  };

  const progress = currentMetrics?.total_steps ? Math.min(Math.round((currentMetrics.step / currentMetrics.total_steps) * 100), 100) : 0;

  return (
    <div className="app-container forge-layout">
      <header className="header-forge">
        <div className="brand-group">
          <div className="forge-logo"><Zap size={24} fill="white" /></div>
          <div className="forge-title"><h1>智核万炼<sup>®</sup></h1><span>NexaForge AI Training Platform</span></div>
        </div>
        <div className="forge-status-pills">
          <div className="pill"><Microscope size={14} /> 模式: {config.is_smart ? '智核自动' : '专家手动'}</div>
          <div className={`pill ${isTraining ? 'active' : ''}`}><Activity size={14} /> 状态: {isTraining ? '炼制中' : '待命'}</div>
          <div className="pill"><Timer size={14} /> 进度: {progress}%</div>
        </div>
        <div className="forge-user">降低AI训练门槛 · 实现开箱即用</div>
      </header>

      <main className="forge-main">
        <section className="forge-left">
          <div className="card glass-card control-center">
            <div className="panel-header-row">
                <h3 className="card-title"><LayoutDashboard size={18} /> 控制中心</h3>
                <div className="mode-switch-pills">
                    <div className={`mode-pill ${config.is_smart ? 'active' : ''}`} onClick={() => setConfig({...config, is_smart: true})}><Wand2 size={12} /> 智核</div>
                    <div className={`mode-pill ${!config.is_smart ? 'active' : ''}`} onClick={() => setConfig({...config, is_smart: false})}><Sliders size={12} /> 专家</div>
                </div>
            </div>
            
            <div className="forge-form scroll-form">
              <div className="field"><label>核心数据集</label>
                <div className="file-uploader" onClick={() => document.getElementById('file-input')?.click()}><Database size={16} /> {uploadStatus === 'success' ? config.dataset_path : '加载数据'}
                  <input id="file-input" type="file" hidden onChange={onFileUpload} accept=".jsonl" />
                </div>
              </div>

              {!config.is_smart ? (
                  <div className="expert-fields fade-in">
                      <div className="field"><label>学习率 (LR)</label>
                        <input type="number" step="0.00001" value={config.learning_rate} onChange={e => setConfig({...config, learning_rate: parseFloat(e.target.value)})} />
                      </div>
                      <div className="grid-2">
                        <div className="field"><label>LoRA Rank</label>
                            <select value={config.lora_r} onChange={e => setConfig({...config, lora_r: parseInt(e.target.value)})}>
                                <option value={8}>8 (极速)</option>
                                <option value={16}>16 (标准)</option>
                                <option value={32}>32 (深度)</option>
                                <option value={64}>64 (极限)</option>
                            </select>
                        </div>
                        <div className="field"><label>BatchSize</label>
                            <input type="number" value={config.batch_size} onChange={e => setConfig({...config, batch_size: parseInt(e.target.value)})} />
                        </div>
                      </div>
                  </div>
              ) : (
                  <div className="smart-info-card">
                      <Shield size={16} /> 智核引擎将根据环境体检结果自动锁定最优超参数矩阵
                  </div>
              )}

              <div className="field"><label>炼制轮数 (Epochs)</label>
                <input type="number" value={config.epochs} onChange={e => setConfig({...config, epochs: parseInt(e.target.value)})} />
              </div>
            </div>

            <button className={`forge-btn ${isTraining ? 'stop' : 'start'}`} onClick={isTraining ? onStopTraining : onStartTraining}>
              {isTraining ? <><Square size={18} /> 终止炼制</> : <><Play size={18} /> 开启智核万炼</>}
            </button>
          </div>

          <div className="card glass-card env-report-card">
              <h3 className="card-title"><ShieldCheck size={18} /> 企业级环境扫描报告</h3>
              {envReport ? (
                  <div className="report-content fade-in">
                      <div className="gpu-level-row">
                          <div className="gpu-info">主渲染设备: <span>{envReport.gpu}</span></div>
                          <div className="env-tag"><Star size={12} fill="currentColor" /> {envReport.level}</div>
                      </div>
                      <div className="gpu-grid">
                          <div className="g-item"><span className="g-label">显存</span><span className="g-val">{envReport.vram}</span></div>
                          <div className="g-item"><span className="g-label">架构</span><span className="g-val">{parseFloat(envReport.cap) >= 8 ? 'Ampere+' : 'Legacy'}</span></div>
                          <div className="g-item"><span className="g-label">设备数</span><span className="g-val">{envReport.count}</span></div>
                      </div>
                      <div className="optimization-list">
                          {envReport.notes.map((note, i) => <div key={i} className="opt-note">✅ {note}</div>)}
                      </div>
                  </div>
              ) : (
                  <div className="report-empty">
                      {isScanning ? <><Loader2 size={24} className="animate-spin" /> 正在进行企业级系统探测...</> : '环境扫描异常，请检查后端连接'}
                  </div>
              )}
          </div>
        </section>

        <section className="forge-center">
          <div className="forge-core-box">
             <div className="core-progress-ring">
                <svg width="240" height="240"><circle cx="120" cy="120" r="110" className="ring-bg" /><circle cx="120" cy="120" r="110" className="ring-fill" style={{strokeDashoffset: 691 - (691 * progress / 100)}} /></svg>
                <div className="ring-content"><span className="pct">{progress}%</span><span className="lbl">炼制深度</span></div>
                {isTraining && <div className="core-glow pulse"></div>}
             </div>
             <div className="core-metrics">
                <div className="m-card"><span className="m-val">{currentMetrics?.loss?.toFixed(4) || '0.0000'}</span><span className="m-lbl">当前 Loss</span></div>
                <div className="m-card"><span className="m-val">{currentMetrics?.step || 0}</span><span className="m-lbl">迭代步数</span></div>
             </div>
          </div>
          <div className="card glass-card chart-forge">
            <div className="chart-header"><Activity size={18} /> 损失函数收敛监测 (Convergence Trace)</div>
            <div className="chart-box-container">
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={chartData}>
                  <defs><linearGradient id="colorLoss" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/><stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/></linearGradient></defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d35" vertical={false} /><XAxis dataKey="step" hide /><YAxis hide domain={['auto', 'auto']} /><Tooltip contentStyle={{ background: '#1c1c22', border: 'none', borderRadius: '8px' }} /><Area type="monotone" dataKey="loss" stroke="var(--primary)" fillOpacity={1} fill="url(#colorLoss)" strokeWidth={3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="forge-right">
          <div className="card glass-card pipeline-box">
            <h3 className="card-title"><Search size={18} /> 炼制流水线追踪</h3>
            <div className="forge-pipeline">{steps.map(step => (
                <div key={step.id} className={`p-step ${step.status}`}>
                    <div className="p-icon">{step.status === 'completed' ? <CheckCircle2 size={16} /> : step.status === 'active' ? <Loader2 size={16} className="animate-spin" /> : step.icon}</div>
                    <div className="p-info"><span className="p-label">{step.label}</span><span className="p-status-txt">{step.status === 'active' ? '正在执行' : step.status === 'completed' ? '已就绪' : '待处理'}</span></div>
                </div>
            ))}</div>
          </div>
          <div className="card glass-card log-forge">
             <h3 className="card-title"><TerminalIcon size={18} /> 智核诊断日志</h3>
             <div className="log-scroll" ref={consoleRef}>{logs.map((log, i) => (<div key={i} className={`log-line ${log.includes('✅') ? 'success' : log.includes('❌') ? 'error' : ''}`}>{log}</div>))}</div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;
