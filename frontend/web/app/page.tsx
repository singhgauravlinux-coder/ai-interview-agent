"use client";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
type Interview = { id: string; job_title: string; category: string; status: string; mode: string };
type Role = { title: string; family: string; level: string; skills: string[]; icon: string; description: string };
const ROLES: Role[] = [
  { title: "DevOps Engineer", family: "Platform engineering", level: "mid", icon: "⌘", description: "CI/CD, infrastructure automation and delivery reliability", skills: ["Linux", "Docker", "Kubernetes", "CI/CD", "Terraform", "Monitoring"] },
  { title: "Site Reliability Engineer", family: "Reliability engineering", level: "senior", icon: "◈", description: "SLOs, incident response, observability and resilient systems", skills: ["SLO / SLI", "Incident response", "Prometheus", "Kubernetes", "Capacity planning", "Distributed systems"] },
  { title: "Production Support Engineer", family: "Technical operations", level: "mid", icon: "⌁", description: "Troubleshooting, production incidents and service operations", skills: ["Linux", "SQL", "Networking", "Log analysis", "ITIL", "Root cause analysis"] },
  { title: "Cloud Engineer", family: "Cloud infrastructure", level: "mid", icon: "☁", description: "Cloud architecture, security, networking and cost control", skills: ["AWS / Azure", "IAM", "Networking", "Terraform", "Containers", "Security"] },
  { title: "Backend Engineer", family: "Software engineering", level: "mid", icon: "{}", description: "APIs, data modelling, performance and service design", skills: ["Python", "REST APIs", "PostgreSQL", "Caching", "Testing", "System design"] },
  { title: "Technical Support Engineer", family: "Customer engineering", level: "junior", icon: "◎", description: "Customer communication, diagnostics and issue resolution", skills: ["Troubleshooting", "Networking", "Ticketing", "Communication", "Documentation", "Escalation"] },
];
const CATEGORIES = [{ value: "technical", label: "Technical deep dive" }, { value: "hr", label: "Behavioral / HR" }, { value: "managerial", label: "Leadership / managerial" }, { value: "mixed", label: "Mixed interview" }];
export default function Home() {
  const router = useRouter();
  const [items, setItems] = useState<Interview[]>([]);
  const [role, setRole] = useState(0);
  const [category, setCategory] = useState("mixed");
  const [mode, setMode] = useState("practice");
  const [interaction, setInteraction] = useState("text");
  const [experience, setExperience] = useState("mid");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);
  const selectedRole = ROLES[role];
  const completed = useMemo(() => items.filter(x => x.status === "completed").length, [items]);
  async function load() {
    try { const r = await fetch(`${API}/interviews`, { cache: "no-store" }); if (!r.ok) throw new Error(); setItems(await r.json()); setApiOnline(true); }
    catch { setApiOnline(false); setMessage("API connection unavailable. Check the backend URL and CORS settings."); }
  }
  useEffect(() => { void load(); }, []);
  async function create() {
    setLoading(true); setMessage("Preparing your interview workspace…");
    try {
      const r = await fetch(`${API}/interviews`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ mode, category, interaction_mode: interaction, job_title: selectedRole.title, experience_level: experience, duration_minutes: 30, skills: selectedRole.skills }) });
      const data = await r.json(); if (!r.ok) throw new Error(data.detail || `Request failed (${r.status})`);
      setMessage(`Interview created · ${data.id}`); await load(); router.push(`/interviews/${data.id}`);
    } catch (e) { setMessage(e instanceof Error ? e.message : "Unable to create interview"); }
    finally { setLoading(false); }
  }
  return <main className="shell">
    <div className="ambient ambient-a"/><div className="ambient ambient-b"/><div className="ambient ambient-c"/>
    <header className="topbar glass">
      <a className="brand" href="#home"><span className="brand-mark">✳</span><span>orbit<span className="brand-light">interview</span></span></a>
      <nav><a className="active" href="#workspace">Workspace</a><a href="#roles">Role library</a><a href="#history">Sessions</a></nav>
      <div className="top-actions"><span className={`status-dot ${apiOnline ? "online" : "offline"}`}/><span className="api-label">{apiOnline ? "API connected" : "API not connected"}</span><div className="avatar">AI</div></div>
    </header>
    <section className="hero" id="home">
      <div className="hero-copy"><div className="eyebrow"><span/> AI-POWERED INTERVIEW STUDIO</div><h1>Make every interview<br/><em>count.</em></h1><p>Practice with purpose. Hire with evidence. Build the confidence and signal that move careers forward.</p><div className="hero-pills"><span>✦ Adaptive interview flows</span><span>◉ Voice & text ready</span><span>◷ 30-minute sessions</span></div></div>
      <div className="hero-orbit" aria-hidden="true"><div className="orbit-ring ring-one"/><div className="orbit-ring ring-two"/><div className="orbit-ring ring-three"/><div className="orbit-core">✳</div><span className="orbit-chip chip-one">TECHNICAL</span><span className="orbit-chip chip-two">BEHAVIORAL</span><span className="orbit-chip chip-three">AI INSIGHTS</span></div>
    </section>
    <section className="stats-grid"><div className="stat glass"><span className="stat-icon">◷</span><div><strong>30 min</strong><small>Focused sessions</small></div></div><div className="stat glass"><span className="stat-icon">⌘</span><div><strong>{ROLES.length} roles</strong><small>Ready-to-use tracks</small></div></div><div className="stat glass"><span className="stat-icon">↗</span><div><strong>{items.length}</strong><small>Total sessions</small></div></div><div className="stat glass"><span className="stat-icon">✧</span><div><strong>{completed}</strong><small>Completed sessions</small></div></div></section>
    <section className="workspace-grid" id="workspace">
      <div className="panel glass create-panel"><div className="panel-heading"><div><div className="eyebrow">START HERE</div><h2>Build your interview</h2><p>Choose a role and tailor the conversation.</p></div><span className="step-badge">01 / 03</span></div>
        <div className="field-label" id="roles">Choose a role</div><div className="role-grid">{ROLES.map((r, i) => <button key={r.title} className={`role-card ${role === i ? "selected" : ""}`} onClick={() => { setRole(i); setExperience(r.level); }}><span className="role-icon">{r.icon}</span><span className="role-name">{r.title}</span><span className="role-family">{r.family}</span>{role === i && <span className="check">✓</span>}</button>)}</div>
        <div className="role-description">{selectedRole.description}</div>
        <div className="form-row"><div><label htmlFor="category">Interview focus</label><select id="category" value={category} onChange={e => setCategory(e.target.value)}>{CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}</select></div><div><label htmlFor="experience">Experience level</label><select id="experience" value={experience} onChange={e => setExperience(e.target.value)}><option value="entry">Entry level</option><option value="junior">Junior</option><option value="mid">Mid-level</option><option value="senior">Senior</option><option value="lead">Lead / Principal</option></select></div></div>
        <label>Session type</label><div className="segmented"><button className={mode === "practice" ? "chosen" : ""} onClick={() => setMode("practice")}>◎ Practice</button><button className={mode === "recruitment" ? "chosen" : ""} onClick={() => setMode("recruitment")}>♙ Recruitment</button></div>
        <label>Conversation format</label><div className="segmented"><button className={interaction === "text" ? "chosen" : ""} onClick={() => setInteraction("text")}>▤ Text</button><button className={interaction === "voice" ? "chosen" : ""} onClick={() => setInteraction("voice")}>◖ Voice</button></div>
        {interaction === "voice" && <p className="inline-note">Voice session selection is saved; live speech transport still requires a configured voice provider.</p>}
        <div className="session-summary"><div><small>SESSION LENGTH</small><strong>30 minutes</strong></div><div><small>SKILLS IN SCOPE</small><strong>{selectedRole.skills.length} competencies</strong></div><div><small>AI PROVIDER</small><strong>Configurable</strong></div></div>
        <button className="primary-button" onClick={create} disabled={loading}>{loading ? "Creating workspace…" : "Create interview workspace  →"}</button><p className="feedback" role="status">{message}</p>
      </div>
      <aside className="side-column"><div className="panel glass how-panel"><div className="eyebrow">THE FLOW</div><h3>From warm-up to insight.</h3><div className="flow-step"><span>01</span><div><b>Get in the zone</b><small>Context, expectations and a calm start</small></div></div><div className="flow-step"><span>02</span><div><b>Go deeper</b><small>Adaptive questions and relevant follow-ups</small></div></div><div className="flow-step"><span>03</span><div><b>See your signal</b><small>Evidence-led feedback and next steps</small></div></div></div>
      <div className="quote-card"><span className="quote-mark">“</span><p>Great interviews reveal how people think, not just what they remember.</p><small>THE ORBIT PRINCIPLE</small><div className="quote-stars">✦ ✧ ✦</div></div></aside>
    </section>
    <section className="panel glass history-panel" id="history"><div className="panel-heading"><div><div className="eyebrow">YOUR ACTIVITY</div><h2>Recent sessions</h2></div><button className="subtle-button" onClick={() => void load()}>↻ Refresh</button></div>{items.length === 0 ? <div className="empty-state"><span>◌</span><b>Your next breakthrough starts here.</b><p>Created interviews will appear in this space.</p></div> : <div className="session-list">{items.map(i => <div className="session-item" key={i.id}><span className="session-symbol">✳</span><div className="session-info"><a href={`/interviews/${i.id}`}><b>{i.job_title}</b></a><small>{i.category} · {i.mode}</small></div><span className={`tag ${i.status}`}>{i.status}</span><code>{i.id.slice(0, 8)}</code></div>)}</div>}</section>
    <footer><span>✳ orbitinterview</span><span>Built for better conversations · Human judgement stays in the loop</span></footer>
  </main>;
}
