import React, {useEffect, useRef, useState} from "react";
import { createRoot } from "react-dom/client";
import { Mic, MicOff, Upload, LogOut, Sparkles, ShieldCheck } from "lucide-react";
import "./styles.css";

const API = "http://localhost:8000";

async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {...(options.headers || {})};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (!(options.body instanceof FormData) && options.body) {
    headers["Content-Type"] = "application/json";
  }
  const r = await fetch(API + path, {...options, headers});
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function Auth({onAuth}) {
  const [login, setLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setErr("");
    try {
      const data = await request(login ? "/auth/login" : "/auth/register", {
        method: "POST",
        body: JSON.stringify({email, password})
      });
      localStorage.setItem("token", data.token);
      onAuth();
    } catch (e) { setErr(e.message); }
  }

  return (
    <div className="center">
      <div className="auth-card">
        <div className="brand"><Sparkles size={28}/> Interview Coach</div>
        <h1>{login ? "Welcome back" : "Create account"}</h1>
        <p className="muted">Resume-aware interview practice with live question detection.</p>
        <form onSubmit={submit}>
          <input placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required/>
          <input placeholder="Password (8+ characters)" type="password" value={password} onChange={e=>setPassword(e.target.value)} required/>
          {err && <div className="error">{err}</div>}
          <button className="primary">{login ? "Login" : "Register"}</button>
        </form>
        <button className="link" onClick={()=>setLogin(!login)}>
          {login ? "Create a new account" : "Already have an account?"}
        </button>
      </div>
    </div>
  );
}

function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem("token"));
  const [resume, setResume] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answer, setAnswer] = useState("");
  const [transcript, setTranscript] = useState("");
  const [listening, setListening] = useState(false);
  const [status, setStatus] = useState("");
  const recognitionRef = useRef(null);

  async function load() {
    try {
      const r = await request("/resume/latest");
      setResume(r);
      const q = await request("/practice/questions");
      setQuestions(q.questions);
    } catch {}
  }

  useEffect(()=>{ if (authed) load(); }, [authed]);

  async function upload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    setStatus("Analyzing resume...");
    try {
      const data = await request("/resume/upload", {method:"POST", body:form});
      setResume(data);
      const q = await request("/practice/questions");
      setQuestions(q.questions);
      setStatus("Resume ready.");
    } catch(e) { setStatus(e.message); }
  }

  async function ask(q) {
    setTranscript(q);
    setAnswer("Generating practice coaching...");
    try {
      const data = await request("/practice/answer", {
        method:"POST", body:JSON.stringify({question:q})
      });
      setAnswer(data.answer);
    } catch(e) { setAnswer(e.message); }
  }

  function startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setStatus("Speech recognition is not supported in this browser. Try Chrome or Edge.");
      return;
    }
    const rec = new SpeechRecognition();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-US";

    rec.onresult = async (event) => {
      let finalText = "";
      let interimText = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const txt = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += txt + " ";
        else interimText += txt;
      }
      setTranscript(prev => (prev + " " + finalText + interimText).trim());

      if (finalText.trim()) {
        try {
          const data = await request("/practice/transcript", {
            method:"POST",
            body: JSON.stringify({transcript: finalText.trim()})
          });
          if (data.is_question) setAnswer(data.answer);
        } catch {}
      }
    };

    rec.onend = () => setListening(false);
    rec.start();
    recognitionRef.current = rec;
    setListening(true);
  }

  function stopListening() {
    recognitionRef.current?.stop();
    setListening(false);
  }

  function logout() {
    localStorage.removeItem("token");
    setAuthed(false);
  }

  if (!authed) return <Auth onAuth={()=>setAuthed(true)}/>;

  return (
    <div>
      <header>
        <div className="brand"><Sparkles size={24}/> Interview Coach</div>
        <button className="ghost" onClick={logout}><LogOut size={18}/> Logout</button>
      </header>

      <main>
        <div className="notice">
          <ShieldCheck size={22}/>
          <div><b>Practice mode</b><br/><span>Use for mock interviews, preparation, or disclosed coaching—not covert assistance in a real hiring interview.</span></div>
        </div>

        <section className="grid">
          <div className="card">
            <h2>1. Upload resume</h2>
            <label className="upload">
              <Upload size={20}/>
              <span>Choose PDF, DOCX, or TXT</span>
              <input type="file" accept=".pdf,.docx,.txt" onChange={upload}/>
            </label>
            {status && <p className="muted">{status}</p>}
            {resume && (
              <div className="analysis">
                <b>{resume.filename}</b>
                <p>{resume.analysis}</p>
              </div>
            )}
          </div>

          <div className="card">
            <h2>2. Live practice listener</h2>
            <p className="muted">The browser transcribes speech and sends detected questions to the practice coach.</p>
            <button className={listening ? "danger" : "primary"} onClick={listening ? stopListening : startListening}>
              {listening ? <MicOff size={18}/> : <Mic size={18}/>}
              {listening ? "Stop listening" : "Start microphone"}
            </button>
            <div className="transcript">
              <b>Transcript</b>
              <p>{transcript || "No speech captured yet."}</p>
            </div>
          </div>
        </section>

        <section className="grid">
          <div className="card">
            <h2>3. Resume-based mock questions</h2>
            {!questions.length && <p className="muted">Upload a resume to generate questions.</p>}
            <div className="questions">
              {questions.map((q,i)=><button key={i} onClick={()=>ask(q)}>{q}</button>)}
            </div>
          </div>

          <div className="card">
            <h2>4. Answer coach</h2>
            <div className="answer">
              {answer || "Choose a mock question or speak one aloud."}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App/>);
