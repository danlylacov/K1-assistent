import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import Users from './pages/Users'
import Conversations from './pages/Conversations'
import Documents from './pages/Documents'
import Messages from './pages/Messages'
import Settings from './pages/Settings'
import Analytics from './pages/Analytics'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <div className="sidebar-header">
            <div className="brand-badge">
              <span className="brand-dot" />
              <div>
                <h1>K1 Admin</h1>
              </div>
            </div>
          </div>
          <ul className="sidebar-menu">
            <li><Link to="/users">👥 Пользователи</Link></li>
            <li><Link to="/conversations">💬 Диалоги</Link></li>
            <li><Link to="/documents">📄 Документы</Link></li>
            <li><Link to="/messages">📨 Сообщения</Link></li>
            <li><Link to="/settings">⚙️ Настройки</Link></li>
            <li><Link to="/analytics">📈 Аналитика</Link></li>
          </ul>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/analytics" replace />} />
            <Route path="/users" element={<Users />} />
            <Route path="/conversations" element={<Conversations />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/messages" element={<Messages />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

