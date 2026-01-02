import React, { useState, useEffect, useRef } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { 
  Cpu, Database, HardDrive, Activity, Terminal, LayoutDashboard, 
  Server, Network, Pause, Play, ChevronRight, BrainCircuit, 
  Settings, Bell, Search, Sparkles, Loader2, X 
} from 'lucide-react';

const App = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const [isPaused, setIsPaused] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState('cpu'); 
  const [history, setHistory] = useState([]);
  const [logs, setLogs] = useState([]);
  const [activeMethod, setActiveMethod] = useState('USE');
  const [dataSource, setDataSource] = useState('CONNECTING...'); // 'LIVE' or 'SIMULATION'
  
  // --- AI State ---
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState('');
  const [aiTitle, setAiTitle] = useState('');

  const scrollRef = useRef(null);
  const MAX_HISTORY = 30;

  // --- Data Engine (Dual Mode: Live vs Simulation) ---
  useEffect(() => {
    if (isPaused) return;

    const fetchData = async () => {
      const now = new Date();
      const timeLabel = now.toLocaleTimeString('en-US', { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
      
      try {
        // 1. Try to fetch REAL data from Python
        const response = await fetch('http://localhost:5000/api/metrics');
        if (!response.ok) throw new Error("Backend offline");
        
        const realData = await response.json();
        
        setDataSource('LIVE');
        const newPoint = {
          time: realData.timestamp || timeLabel,
          cpu: realData.cpu,
          memory: realData.memory,
          disk: realData.disk,
          network: realData.network,
        };

        setHistory(prev => {
          const updated = [...prev, newPoint];
          return updated.slice(-MAX_HISTORY);
        });

      } catch (error) {
        // 2. Fallback to SIMULATION if Python is down
        setDataSource('SIMULATION');
        
        const simPoint = {
          time: timeLabel,
          cpu: Math.floor(Math.random() * 30) + 30 + (Math.random() > 0.9 ? 20 : 0),
          memory: Math.floor(Math.random() * 10) + 60,
          network: Math.floor(Math.random() * 50) + 20,
          disk: Math.floor(Math.random() * 5) + 10,
        };

        setHistory(prev => {
          const updated = [...prev, simPoint];
          return updated.slice(-MAX_HISTORY);
        });
      }
    };

    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [isPaused]);

  // --- AI Functions ---
  const callGemini = async (prompt, title) => {
    setAiTitle(title);
    setAiModalOpen(true);
    setAiLoading(true);
    setAiResponse('');

    try {
      const apiKey = ""; // System provides this at runtime. 
      // NOTE: In a local React app, you might need to hardcode your key here temporarily or use process.env.REACT_APP_GEMINI_KEY
      
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
      });

      const data = await response.json();
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text || "No analysis available.";
      setAiResponse(text);
    } catch (error) {
      setAiResponse(`Diagnostic failed: ${error.message}.`);
    } finally {
      setAiLoading(false);
    }
  };

  const handleFullDiagnostics = () => {
    if (history.length === 0) return;
    const current = history[history.length - 1];
    
    const prompt = `Act as a Senior SRE. Analyze my system (${dataSource} Mode):
    CPU: ${current.cpu}%, RAM: ${current.memory}%, Disk: ${current.disk}%.
    Give a 1-sentence status and 1 actionable tip.`;

    callGemini(prompt, "System Diagnostics");
  };

  // --- UI Components ---
  const MetricCard = ({ title, value, unit, icon: Icon, metricKey, color, trend }) => (
    <button 
      onClick={() => setSelectedMetric(metricKey)}
      className={`relative group overflow-hidden rounded-2xl border p-5 text-left transition-all duration-300 ${
        selectedMetric === metricKey 
          ? `bg-${color}-500/10 border-${color}-500/50 ring-1 ring-${color}-500/50` 
          : 'bg-zinc-900/50 border-white/5 hover:bg-zinc-800/50 hover:border-white/10'
      }`}
    >
      <div className="flex justify-between items-start mb-4">
        <div className={`p-2 rounded-lg bg-${color}-500/20 text-${color}-400`}>
          <Icon size={20} />
        </div>
        <span className={`text-xs font-mono px-2 py-1 rounded-full ${
          trend === 'up' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
        }`}>
          {trend === 'up' ? '↑ High' : '↓ Stable'}
        </span>
      </div>
      <div>
        <p className="text-zinc-500 text-xs font-medium uppercase tracking-wider">{title}</p>
        <h3 className="text-2xl font-bold text-white mt-1">
          {value} <span className="text-sm text-zinc-500 font-normal">{unit}</span>
        </h3>
      </div>
      {selectedMetric === metricKey && (
        <div className={`absolute bottom-0 left-0 w-full h-1 bg-${color}-500 animate-pulse`} />
      )}
    </button>
  );

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans selection:bg-blue-500/30 flex overflow-hidden relative">
      
      {/* AI Modal */}
      {aiModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-zinc-900 border border-zinc-700 w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
            <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/50">
              <h3 className="font-semibold text-blue-400 flex items-center gap-2">
                <Sparkles size={18} /> {aiTitle}
              </h3>
              <button onClick={() => setAiModalOpen(false)} className="p-1 hover:bg-zinc-800 rounded-lg">
                <X size={20} className="text-zinc-500" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto bg-zinc-950/50">
              {aiLoading ? (
                <div className="flex flex-col items-center justify-center py-12 gap-4">
                  <Loader2 size={32} className="animate-spin text-blue-500" />
                  <p className="text-zinc-500 text-sm animate-pulse">Analyzing...</p>
                </div>
              ) : (
                <p className="whitespace-pre-wrap leading-relaxed text-zinc-300">{aiResponse}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <aside className="w-20 lg:w-64 border-r border-white/5 flex flex-col bg-zinc-900/30 backdrop-blur-xl">
        <div className="p-6 flex items-center gap-3 text-blue-500">
          <BrainCircuit size={28} className="animate-pulse" />
          <span className="font-bold text-xl tracking-tight hidden lg:block text-white">Sentin<span className="text-blue-500">el</span></span>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          {[{ id: 'dashboard', icon: LayoutDashboard, label: 'Overview' }, { id: 'network', icon: Network, label: 'Network' }, { id: 'logs', icon: Terminal, label: 'Logs' }].map(item => (
            <button key={item.id} onClick={() => setActiveView(item.id)} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeView === item.id ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20' : 'text-zinc-500 hover:bg-white/5'}`}>
              <item.icon size={20} />
              <span className="hidden lg:block text-sm font-medium">{item.label}</span>
              {activeView === item.id && <ChevronRight size={14} className="ml-auto hidden lg:block" />}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>

        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-zinc-900/30 backdrop-blur-sm z-10">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold">System Overview</h2>
            <div className={`px-3 py-1 rounded-full border flex items-center gap-2 ${dataSource === 'LIVE' ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-amber-500/10 border-amber-500/20'}`}>
              <div className={`w-1.5 h-1.5 rounded-full animate-pulse ${dataSource === 'LIVE' ? 'bg-emerald-500' : 'bg-amber-500'}`}></div>
              <span className={`text-xs font-medium ${dataSource === 'LIVE' ? 'text-emerald-400' : 'text-amber-400'}`}>
                {dataSource === 'LIVE' ? 'Connected to Localhost' : 'Simulation Mode'}
              </span>
            </div>
          </div>
          <button onClick={handleFullDiagnostics} className="flex items-center gap-2 px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-full text-sm font-medium shadow-lg shadow-blue-500/20 transition-all">
            <Sparkles size={14} /> AI Diagnostics
          </button>
        </header>

        <div className="flex-1 overflow-y-auto p-8 z-0">
          <div className="max-w-7xl mx-auto space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <MetricCard title="CPU" value={history[history.length-1]?.cpu || 0} unit="%" icon={Cpu} metricKey="cpu" color="blue" trend="up" />
              <MetricCard title="RAM" value={history[history.length-1]?.memory || 0} unit="%" icon={Database} metricKey="memory" color="purple" trend="down" />
              <MetricCard title="DISK" value={history[history.length-1]?.disk || 0} unit="%" icon={HardDrive} metricKey="disk" color="amber" trend="down" />
              <MetricCard title="NET" value={history[history.length-1]?.network || 0} unit="Mb" icon={Activity} metricKey="network" color="emerald" trend="down" />
            </div>

            <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-6 backdrop-blur-sm h-[400px]">
              <div className="flex justify-between mb-4">
                <h3 className="text-lg font-semibold flex gap-2 items-center text-white">
                  <Activity size={18} className="text-blue-400"/> Real-time Monitor ({selectedMetric.toUpperCase()})
                </h3>
                <div className="flex gap-2">
                  <button onClick={() => setIsPaused(!isPaused)} className="p-2 border border-zinc-700 rounded-lg text-zinc-400 hover:text-white">
                    {isPaused ? <Play size={16} /> : <Pause size={16} />}
                  </button>
                </div>
              </div>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={history}>
                  <defs>
                    <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                  <XAxis dataKey="time" stroke="#52525b" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#52525b" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a' }} itemStyle={{ color: '#fff' }} />
                  <Area type="monotone" dataKey={selectedMetric} stroke="#3b82f6" strokeWidth={2} fill="url(#chartGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            
             {/* Methodology Toggle */}
            <div className="bg-zinc-900/30 border border-white/10 rounded-2xl p-6 flex justify-between items-center">
               <div>
                 <h3 className="font-bold text-white mb-1">Analysis Method</h3>
                 <p className="text-zinc-500 text-sm">
                   {activeMethod === 'USE' ? "Utilization • Saturation • Errors (Best for Hardware)" : "Rate • Errors • Duration (Best for APIs)"}
                 </p>
               </div>
               <div className="bg-black/40 p-1 rounded-xl border border-white/5 flex">
                 <button onClick={() => setActiveMethod('USE')} className={`px-4 py-2 rounded-lg text-xs font-bold ${activeMethod === 'USE' ? 'bg-zinc-800 text-white' : 'text-zinc-500'}`}>U.S.E.</button>
                 <button onClick={() => setActiveMethod('RED')} className={`px-4 py-2 rounded-lg text-xs font-bold ${activeMethod === 'RED' ? 'bg-zinc-800 text-white' : 'text-zinc-500'}`}>R.E.D.</button>
               </div>
            </div>

          </div>
        </div>
      </main>
      
      {/* Global CSS */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 4px; }
      `}</style>
    </div>
  );
};

export default App;
