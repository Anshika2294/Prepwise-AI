import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "react-toastify"
import API from "../api/axios"

export default function Dashboard() {
  const navigate = useNavigate()
  const [data, setData]       = useState(null)
  const [jobRole, setJobRole] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    API.get("/report/dashboard")
      .then(res => setData(res.data))
      .catch(()  => toast.error("Dashboard load nahi hua"))
  }, [])

  const startInterview = async () => {
    if (!jobRole.trim()) {
      toast.error("Job role daalo!")
      return
    }
    setLoading(true)
    try {
      const res = await API.post("/interview/start", { job_role: jobRole })
      navigate(`/interview/${res.data.id}`)
    } catch {
      toast.error("Interview start nahi hua")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>👋 Welcome, {data?.user || "..."}</h2>

      {/* Start Interview */}
      <div style={styles.card}>
        <h3 style={styles.cardTitle}>🚀 New Interview Start Karo</h3>
        <div style={styles.row}>
          <input
            style={styles.input}
            placeholder="Job role likho (e.g. Python Developer)"
            value={jobRole}
            onChange={e => setJobRole(e.target.value)}
          />
          <button style={styles.btn} onClick={startInterview} disabled={loading}>
            {loading ? "Starting..." : "Start"}
          </button>
        </div>
      </div>

      {/* Past Sessions */}
      <div style={styles.card}>
        <h3 style={styles.cardTitle}>📋 Past Sessions</h3>
        {data?.sessions?.length === 0 && (
          <p style={styles.muted}>Abhi koi session nahi hai</p>
        )}
        {data?.sessions?.map(s => (
          <div key={s.session_id} style={styles.sessionRow}>
            <div>
              <b style={styles.role}>{s.job_role}</b>
              <span style={styles.muted}> — {new Date(s.date).toLocaleDateString()}</span>
            </div>
            <div style={styles.scores}>
              <span style={styles.score}>⭐ {s.overall_score}</span>
              <button
                style={styles.viewBtn}
                onClick={() => navigate(`/report/${s.session_id}`)}
              >
                View Report
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

const styles = {
  page       : { padding:"24px", maxWidth:"800px", margin:"0 auto", color:"#fff" },
  heading    : { fontSize:"24px", marginBottom:"24px" },
  card       : { background:"#1e1e2e", borderRadius:"12px", padding:"24px", marginBottom:"20px" },
  cardTitle  : { color:"#a78bfa", marginBottom:"16px" },
  row        : { display:"flex", gap:"12px" },
  input      : { flex:1, padding:"10px", borderRadius:"8px", border:"1px solid #444",
                 background:"#2a2a3e", color:"#fff", fontSize:"14px" },
  btn        : { padding:"10px 20px", background:"#7c3aed", color:"#fff",
                 border:"none", borderRadius:"8px", cursor:"pointer", whiteSpace:"nowrap" },
  sessionRow : { display:"flex", justifyContent:"space-between", alignItems:"center",
                 padding:"12px 0", borderBottom:"1px solid #333" },
  role       : { color:"#fff", fontSize:"15px" },
  muted      : { color:"#888", fontSize:"13px" },
  scores     : { display:"flex", alignItems:"center", gap:"12px" },
  score      : { color:"#a78bfa", fontWeight:"bold" },
  viewBtn    : { padding:"6px 14px", background:"transparent", color:"#a78bfa",
                 border:"1px solid #a78bfa", borderRadius:"6px", cursor:"pointer" },
}