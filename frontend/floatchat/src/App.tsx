import './App.css'
import { Routes, Route, useNavigate } from 'react-router-dom'
import SignupForm from './components/SignupForm'
import ChatPage from './components/ChatPage'

function ChatRoot() {
  return (
    <>
      <ChatPage />
    </>
  )
}

function SigninRoute() {
  const navigate = useNavigate()
  return (
    <SignupForm onToggleMode={() => navigate('/')} onSignedIn={() => navigate('/')} />
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<ChatRoot />} />
      <Route path="/signin" element={<SigninRoute />} />
    </Routes>
  )
}

export default App
