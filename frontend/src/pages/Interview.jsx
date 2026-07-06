import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { toast } from "react-toastify"
import API from "../api/axios"

export default function Interview() {
  const { sessionId } = useParams()
  const navigate      = useNavigate()

  const [question, setQuestion]   = useState(null)
  const [answer, setAnswer]       = useState("")
  const [feedback, setFeedback]   = useState(null)
  const [qNo, setQNo]             = useState(0)
  const [loading, setLoading]     = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone]           = useState(false)

  useEffect(() => { fetchQuestion() }, [])

  const fetchQuestion = async () => {
    setLoading(true)
    setFeedback(null)
    setAnswer("")
    try {
      const res = await API.get(`/interview/question/${sessionId}`)
      setQuestion(res.data)
      setQNo(res.data.question_no)
    } catch (err) {
      const msg = err.response?.data?.detail || ""
      if (msg.includes("Max 10")) {
        toast.info("10 questions complete! Session end ho raha hai.")
        endSession()
      } else {
        toast.error("Question load nahi hua")
      }
    } finally {
      setLoading(false)
    }
  }

  const submitAnswer = async () => {
    if (!answer.trim()) {
      toast.error("Answer likho pehle!")
      return
    }
    setSubmitting(true)
    try {
      const res = await API.post("/interview/answer", {
        question_id : question.question_id,
        user_answer : answer,
      })
      setFeedback(res.data)
    } catch {
      toast.error("Answer submit nahi hua")
    } finally {
      setSubmitting(false)
    }
  }

  const endSession = async () => {
    try {
      await API.post(`/interview/end/${sessionId}`)
      setDone(true)
    } catch {
      toast.error("Session end nahi hua")
    }
  }

  if (done) return (
    <div style={styles.center}>
      <h2 style={{ color:"#a78bfa" }}>🎉 Interview Complete!</h2>
      <button style={styles.btn} onClick={() => navigate(`/report/${sessionId}`)}>
        Report Dekho
      </button>
    </div>
  )

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <span style={styles.qNo}>Question {qNo} / 10</span>
        <button style={styles.endBtn} onClick={endSession}>End Interview</button>
      </div>

      {/* Question */}
      {loading ? (
        <p style={styles.muted}>Question load ho raha hai...</p>
      ) : (
        <div style={styles.card}>
          <p style={styles.questionText}>
            {question?.question_text || "Loading..."}
          </p>
        </div>
      )}

      {/* Answer box */}
      {!feedback && !loading && (
        <div style={styles.card}>
          <textarea
            style={styles.textarea}
            placeholder="Apna answer yahan likho..."
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            rows={6}
          />
          <button style={styles.btn} onClick={submitAnswer} disabled={submitting}>
            {submitting ? "Submitting..." : "Submit Answer"}
          </button>
        </div>
      )}

      {/* Feedback */}
      {feedback && (
        <div style={styles.feedbackCard}>
          <h3 style={styles.cardTitle}>📊 Score</h3>
          <div style={styles.scoreRow}>
            <ScoreBadge label="Keyword"   value={feedback.keyword_score} />
            <ScoreBadge label="Grammar"   value={feedback.grammar_score} />
            <ScoreBadge label="Relevance" value={feedback.relevance_score} />
          </div>

          <h3 style={styles.cardTitle}>💬 AI Feedback</h3>
          <p style={styles.feedbackText}>{feedback.ai_feedback}</p>

          <button style={styles.btn} onClick={fetchQuestion}>
            Next Question ➜
          </button>
        </div>
      )}
    </div>
  )
}

function ScoreBadge({ label, value }) {
  const color = value >= 70 ? "#22c55e" : value >= 40 ? "#f59e0b" : "#ef4444"
  return (
    <div style={{ textAlign:"center" }}>
      <div style={{ fontSize:"28px", fontWeight:"bold", color }}>{value}</div>
      <div style={{ color:"#888", fontSize:"12px" }}>{label}</div>
    </div>
  )
}

const styles = {
  page        : { padding:"24px", maxWidth:"720px", margin:"0 auto", color:"#fff" },
  header      : { display:"flex", justifyContent:"space-between",
                  alignItems:"center", marginBottom:"20px" },
  qNo         : { fontSize:"18px", color:"#a78bfa", fontWeight:"bold" },
  endBtn      : { padding:"8px 16px", background:"#dc2626", color:"#fff",
                  border:"none", borderRadius:"8px", cursor:"pointer" },
  card        : { background:"#1e1e2e", borderRadius:"12px", padding:"24px",
                  marginBottom:"16px", display:"flex", flexDirection:"column", gap:"12px" },
  feedbackCard: { background:"#1a1a2e", border:"1px solid #7c3aed",
                  borderRadius:"12px", padding:"24px", marginBottom:"16px" },
  cardTitle   : { color:"#a78bfa", marginBottom:"12px" },
  questionText: { fontSize:"18px", color:"#fff", lineHeight:"1.6" },
  textarea    : { padding:"12px", borderRadius:"8px", border:"1px solid #444",
                  background:"#2a2a3e", color:"#fff", fontSize:"14px",
                  resize:"vertical", fontFamily:"inherit" },
  btn         : { padding:"12px", background:"#7c3aed", color:"#fff",
                  border:"none", borderRadius:"8px", cursor:"pointer", fontSize:"15px" },
  scoreRow    : { display:"flex", gap:"32px", justifyContent:"center", marginBottom:"20px" },
  feedbackText: { color:"#ccc", lineHeight:"1.7", fontSize:"14px" },
  muted       : { color:"#888" },
  center      : { textAlign:"center", marginTop:"80px", color:"#fff" },
}