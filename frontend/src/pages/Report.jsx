import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { toast } from "react-toastify"
import API from "../api/axios"

export default function Report() {
  const { sessionId } = useParams()
  const [report, setReport] = useState(null)

  useEffect(() => {
    API.get(`/report/session/${sessionId}`)
      .then(res => setReport(res.data))
      .catch(()  => toast.error("Report load nahi hua"))
  }, [])

  if (!report) return <p style={{ color:"#fff", padding:"24px" }}>Loading...</p>

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>📋 Interview Report</h2>

      {/* Summary */}
      <div style={styles.card}>
        <h3 style={styles.cardTitle}>Summary</h3>
        <div style={styles.summaryGrid}>
          <SummaryItem label="Job Role"     value={report.job_role} />
          <SummaryItem label="Overall Score" value={`${report.overall_score}/100`} />
          <SummaryItem label="Keyword Avg"  value={report.avg_keyword} />
          <SummaryItem label="Grammar Avg"  value={report.avg_grammar} />
          <SummaryItem label="Relevance Avg" value={report.avg_relevance} />
          <SummaryItem label="Questions"    value={report.questions.length} />
        </div>
      </div>

      {/* Per question detail */}
      {report.questions.map((q) => (
        <div key={q.q_no} style={styles.qCard}>
          <p style={styles.qLabel}>Q{q.q_no}. {q.question}</p>
          <p style={styles.answerLabel}>Your Answer:</p>
          <p style={styles.answer}>{q.answer}</p>

          <div style={styles.scoreRow}>
            <ScoreBadge label="Keyword"   value={q.keyword_score} />
            <ScoreBadge label="Grammar"   value={q.grammar_score} />
            <ScoreBadge label="Relevance" value={q.relevance_score} />
          </div>

          <p style={styles.feedbackLabel}>💬 Feedback:</p>
          <p style={styles.feedback}>{q.feedback}</p>
        </div>
      ))}
    </div>
  )
}

function SummaryItem({ label, value }) {
  return (
    <div style={summaryStyles.box}>
      <span style={summaryStyles.label}>{label}</span>
      <span style={summaryStyles.value}>{value}</span>
    </div>
  )
}

function ScoreBadge({ label, value }) {
  const color = value >= 70 ? "#22c55e" : value >= 40 ? "#f59e0b" : "#ef4444"
  return (
    <div style={{ textAlign:"center" }}>
      <div style={{ fontSize:"24px", fontWeight:"bold", color }}>{value}</div>
      <div style={{ color:"#888", fontSize:"12px" }}>{label}</div>
    </div>
  )
}

const styles = {
  page        : { padding:"24px", maxWidth:"760px", margin:"0 auto", color:"#fff" },
  heading     : { fontSize:"24px", marginBottom:"24px" },
  card        : { background:"#1e1e2e", borderRadius:"12px",
                  padding:"24px", marginBottom:"20px" },
  cardTitle   : { color:"#a78bfa", marginBottom:"16px" },
  summaryGrid : { display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"12px" },
  qCard       : { background:"#1e1e2e", borderRadius:"12px",
                  padding:"20px", marginBottom:"16px" },
  qLabel      : { fontSize:"16px", fontWeight:"bold", color:"#fff", marginBottom:"12px" },
  answerLabel : { color:"#888", fontSize:"13px" },
  answer      : { color:"#ccc", fontSize:"14px", marginBottom:"12px" },
  scoreRow    : { display:"flex", gap:"24px", margin:"12px 0" },
  feedbackLabel:{ color:"#a78bfa", fontSize:"13px", marginBottom:"4px" },
  feedback    : { color:"#ccc", fontSize:"14px", lineHeight:"1.6" },
}

const summaryStyles = {
  box  : { background:"#2a2a3e", borderRadius:"8px", padding:"12px", textAlign:"center" },
  label: { display:"block", color:"#888", fontSize:"12px", marginBottom:"4px" },
  value: { display:"block", color:"#fff", fontWeight:"bold", fontSize:"16px" },
}