import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ToastContainer } from "react-toastify"
import "react-toastify/dist/ReactToastify.css"

import Login          from "./pages/Login"
import Register       from "./pages/Register"
import Dashboard      from "./pages/Dashboard"
import ResumeUpload   from "./pages/ResumeUpload"
import Interview      from "./pages/Interview"
import Report         from "./pages/Report"
import Navbar         from "./components/Navbar"
import ProtectedRoute from "./components/ProtectedRoute"

export default function App() {
  return (
    <BrowserRouter>
      <ToastContainer position="top-right" autoClose={3000} />
      <Routes>
        {/* Public routes */}
        <Route path="/"          element={<Login />} />
        <Route path="/register"  element={<Register />} />

        {/* Protected routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute><Navbar /><Dashboard /></ProtectedRoute>
        }/>
        <Route path="/resume" element={
          <ProtectedRoute><Navbar /><ResumeUpload /></ProtectedRoute>
        }/>
        <Route path="/interview/:sessionId" element={
          <ProtectedRoute><Navbar /><Interview /></ProtectedRoute>
        }/>
        <Route path="/report/:sessionId" element={
          <ProtectedRoute><Navbar /><Report /></ProtectedRoute>
        }/>
      </Routes>
    </BrowserRouter>
  )
}
