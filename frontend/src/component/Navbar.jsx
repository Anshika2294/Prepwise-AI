import { useNavigate } from "react-router-dom"

export default function Navbar() {
  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem("token")
    navigate("/")
  }

  return (
    <nav style={styles.nav}>
      <span style={styles.logo}>🎯 MockAI</span>
      <div style={styles.links}>
        <button onClick={() => navigate("/dashboard")} style={styles.btn}>Dashboard</button>
        <button onClick={() => navigate("/resume")}    style={styles.btn}>Upload Resume</button>
        <button onClick={logout}                       style={styles.logout}>Logout</button>
      </div>
    </nav>
  )
}

const styles = {
  nav    : { display:"flex", justifyContent:"space-between", alignItems:"center",
             padding:"12px 24px", background:"#1e1e2e", color:"#fff" },
  logo   : { fontSize:"20px", fontWeight:"bold" },
  links  : { display:"flex", gap:"12px" },
  btn    : { background:"transparent", color:"#fff", border:"1px solid #555",
             padding:"6px 14px", borderRadius:"6px", cursor:"pointer" },
  logout : { background:"#e74c3c", color:"#fff", border:"none",
             padding:"6px 14px", borderRadius:"6px", cursor:"pointer" },
}