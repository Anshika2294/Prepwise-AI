import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { toast } from "react-toastify"
import API from "../api/axios"

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: "", email: "", password: "" })
  const [loading, setLoading] = useState(false)

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async () => {
    if (!form.name || !form.email || !form.password) {
      toast.error("Sab fields bharo!")
      return
    }
    setLoading(true)
    try {
      await API.post("/auth/register", form)
      toast.success("Account ban gaya! Login karo.")
      navigate("/")
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h2 style={styles.title}>📝 Register</h2>

        <input style={styles.input} name="name"     placeholder="Full Name"
               value={form.name}     onChange={handleChange} />
        <input style={styles.input} name="email"    placeholder="Email" type="email"
               value={form.email}    onChange={handleChange} />
        <input style={styles.input} name="password" placeholder="Password" type="password"
               value={form.password} onChange={handleChange} />

        <button style={styles.btn} onClick={handleSubmit} disabled={loading}>
          {loading ? "Creating..." : "Register"}
        </button>

        <p style={styles.link}>
          Already account hai? <Link to="/">Login karo</Link>
        </p>
      </div>
    </div>
  )
}

const styles = {
  page  : { display:"flex", justifyContent:"center", alignItems:"center",
            minHeight:"100vh", background:"#0f0f1a" },
  card  : { background:"#1e1e2e", padding:"40px", borderRadius:"12px",
            width:"360px", display:"flex", flexDirection:"column", gap:"16px" },
  title : { color:"#fff", textAlign:"center", marginBottom:"8px" },
  input : { padding:"12px", borderRadius:"8px", border:"1px solid #444",
            background:"#2a2a3e", color:"#fff", fontSize:"14px" },
  btn   : { padding:"12px", background:"#7c3aed", color:"#fff", border:"none",
            borderRadius:"8px", fontSize:"16px", cursor:"pointer" },
  link  : { color:"#aaa", textAlign:"center", fontSize:"13px" },
}