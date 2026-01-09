import React from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import Login from "./pages/Login"
import Register from "./pages/Register"
import Predictions from "./pages/Predictions"
import Layout from "./components/Layout"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Layout />}>
          <Route path="predictions" element={<Predictions />} />
          <Route index element={<Predictions />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
