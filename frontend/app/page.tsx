"use client";
import { FormEvent, useState } from "react";
type Message = { role: "user" | "assistant"; content: string; sources?: { file: string; section?: string }[] };
const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export default function Home() {
  const [question, setQuestion] = useState(""); const [loading, setLoading] = useState(false); const [messages, setMessages] = useState<Message[]>([]);
  async function ask(event: FormEvent) {
    event.preventDefault(); const text = question.trim(); if (!text || loading) return;
    setMessages((items) => [...items, { role: "user", content: text }]); setQuestion(""); setLoading(true);
    try { const response = await fetch(`${API}/api/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: text }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail ?? "请求失败"); setMessages((items) => [...items, { role: "assistant", content: data.answer, sources: data.sources }]); }
    catch (error) { setMessages((items) => [...items, { role: "assistant", content: `暂时无法回答：${error instanceof Error ? error.message : "未知错误"}` }]); }
    finally { setLoading(false); }
  }
  return <main><section className="hero"><p>个人职业 AI Agent</p><h1>Calvin AI Resume Assistant</h1><span>基于真实简历与项目资料回答，并显示引用来源。</span></section><section className="chat">{messages.length === 0 && <p className="hint">试试问：“介绍一下你的支付宝 NFC 项目经历”</p>}{messages.map((m, i) => <article key={i} className={m.role}><b>{m.role === "user" ? "招聘经理" : "Calvin AI"}</b><p>{m.content}</p>{m.sources?.length ? <small>来源：{m.sources.map((s) => `${s.file}${s.section ? ` · ${s.section}` : ""}`).join("；")}</small> : null}</article>)}{loading && <article className="assistant">正在检索知识库…</article>}</section><form onSubmit={ask}><input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="输入关于经历、能力或项目的问题"/><button disabled={loading}>{loading ? "回答中" : "发送"}</button></form></main>;
}
