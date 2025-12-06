import react from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Home from "./pages/Home"
import Profile from "./pages/Profile"
import HackathonDetail from "./pages/HackathonDetail"
import Messages from "./pages/Messages"
import MyTeams from "./pages/MyTeams"
import NotFound from "./pages/NotFound"
import TelegramLogin from "./pages/TelegramLogin"
import ProtectedRoute from "./components/ProtectedRoute"
import UserTypeRouter from "./components/UserTypeRouter"

function Logout() {
  localStorage.clear()
  return <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <UserTypeRouter />
            </ProtectedRoute>
          }
        />
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
          path="/hackathon/:id"
          element={
            <ProtectedRoute>
              <HackathonDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/messages"
          element={
            <ProtectedRoute>
              <Messages />
            </ProtectedRoute>
          }
        />
        <Route
          path="/my-teams"
          element={
            <ProtectedRoute>
              <MyTeams />
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/telegram-login" element={<TelegramLogin />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="*" element={<NotFound />}></Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
