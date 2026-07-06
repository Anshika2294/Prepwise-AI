import { useState } from "react"
import { toast } from "react-toastify"
import API from "../api/axios"

export default function ResumeUpload() {
  const [file, setFile]       = useState(null)
  const [jobRole, setJobRole] = useState("")
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    if (!file || !jobRole.trim()) {
      toast.error("File aur job role dono daalo!")
      return
    }
    const formData = new FormData()
    formData.append("file",     file)
    formData.append("job_role", jobRole)

    setLoading(true)
    try {
      const res = await API.post("/resume/upload", formData)
      // ATS detail lo
      const ats = await API.get(`/resume/ats-result/${res.data.id}?job_role=${jobRole}`)
      setResult(ats.data)
      toast.success("Resume upload ho gaya!")
    } catch (err) {
      toast.error(err.response?.data?.detail || "Upload failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>📄 Resume Upload</h2>

      <div style={styles.card}>
        <input
          style={styles.input}
          placeholder="Job role (e.g. Data Scientist)"
          value={jobRole}
          onChange={e => setJobRole(e.target.value)}
        />
        <input
          type="file"
          accept=".pdf,.docx"
          style={styles.fileInput}
          onChange={e => setFile(e.target.files[0])}
        />
        <button style={styles.btn} onClick={handleUpload} disabled={loading}>
          {loading ? "Uploading..." : "Upload & Check ATS Score"}
        </button>
      </div>

      {/* ATS Result */}
      {result && (
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>📊 ATS Score Result</h3>

          <div style={styles.scoreBox}>
            <span style={styles.bigScore}>{result.ats_score}</span>
            <span style={styles.outOf}>/100</span>
          </div>

          <div style={styles.row}>
            <ScorePill label="Skill Match"  value={result.skill_score} />
            <ScorePill label="Similarity"   value={result.tfidf_score} />
            <ScorePill label="Experience"   value={result.experience_score} />
          </div>

          <div style={styles.section}>
            <p style={styles.label}>✅ Matched Skills:</p>
            <p style={styles.value}>{result.matched_skills.join(", ") || "None"}</p>
          </div>
          <div style={styles.section}>
            <p style={styles.label}>❌ Missing Skills:</p>
            <p style={styles.value}>{result.missing_skills.join(", ") || "None"}</p>
          </div>
        </div>
      )}
    </div>
  )
}

function ScorePill({ label, value }) {
  return (
    <div style={pillStyles.box}>
      <span style={pillStyles.label}>{label}</span>
      <span style={pillStyles.value}>{value}</span>
    </div>
  )
}

const styles = {
  page      : { padding:"24px", maxWidth:"700px", margin:"0 auto", color:"#fff" },
  heading   : { fontSize:"24px", marginBottom:"24px" },
  card      : { background:"#1e1e2e", borderRadius:"12px", padding:"24px",
                marginBottom:"20px", display:"flex", flexDirection:"column", gap:"14px" },
  cardTitle : { color:"#a78bfa", marginBottom:"8px" },
  input     : { padding:"10px", borderRadius:"8px", border:"1px solid #444",
                background:"#2a2a3e", color:"#fff", fontSize:"14px" },
  fileInput : { color:"#aaa", fontSize:"14px" },
  btn       : { padding:"12px", background:"#7c3aed", color:"#fff",
                border:"none", borderRadius:"8px", cursor:"pointer", fontSize:"15px" },
  scoreBox  : { textAlign:"center", margin:"8px 0" },
  bigScore  : { fontSize:"56px", fontWeight:"bold", color:"#a78bfa" },
  outOf     : { fontSize:"20px", color:"#888" },
  row       : { display:"flex", gap:"12px", justifyContent:"center" },
  section   : { marginTop:"8px" },
  label     : { color:"#888", fontSize:"13px", marginBottom:"4px" },
  value     : { color:"#fff", fontSize:"14px" },
}

const pillStyles = {
  box   : { background:"#2a2a3e", borderRadius:"8px", padding:"10px 16px", textAlign:"center" },
  label : { display:"block", color:"#888", fontSize:"12px" },
  value : { display:"block", color:"#a78bfa", fontSize:"20px", fontWeight:"bold" },
}