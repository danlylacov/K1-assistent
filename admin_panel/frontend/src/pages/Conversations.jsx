import { useEffect, useRef, useState } from 'react'
import api from '../api/client'

function Conversations() {
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState(null)
  const [thread, setThread] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  const [composerText, setComposerText] = useState('')
  const [composerFile, setComposerFile] = useState(null)
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    fetchUsers()
  }, [search])

  useEffect(() => {
    if (selectedUser?.user_id) {
      fetchThread(selectedUser.user_id)
    }
  }, [selectedUser?.user_id])

  useEffect(() => {
    // автоскролл в самый низ при обновлении треда
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }, [thread.length, selectedUser?.user_id])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const params = search ? { search } : {}
      const response = await api.get('/users', { params })
      setUsers(response.data.users || [])
      // автоселект первого
      if (!selectedUser && response.data.users?.length) {
        setSelectedUser(response.data.users[0])
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchThread = async (userId) => {
    try {
      const response = await api.get('/conversations', { params: { user_id: userId, limit: 200 } })
      // backend отдаёт newest-first, а нам нужно старые сверху, новые снизу
      const items = response.data.conversations || []
      setThread(items.slice().reverse())
    } catch (error) {
      console.error('Error fetching thread:', error)
    }
  }

  const sendQuickReply = async (e) => {
    e.preventDefault()
    if (!selectedUser?.user_id) return
    if (!composerText && !composerFile) return

    setSending(true)
    try {
      const formData = new FormData()
      formData.append('user_id', selectedUser.user_id)
      formData.append('message', composerText || '')
      if (composerFile) formData.append('file', composerFile)

      await api.post('/messages/send', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setComposerText('')
      setComposerFile(null)
      // обновляем тред
      await fetchThread(selectedUser.user_id)
    } catch (error) {
      alert('Ошибка при отправке: ' + error.message)
    } finally {
      setSending(false)
    }
  }

  if (loading) return <div className="card">Загрузка...</div>

  return (
    <div>
      <h1>Диалоги (мессенджер)</h1>

      <div className="messenger">
        <div className="card chat-list">
          <div className="chat-list-header">
            <input
              type="text"
              placeholder="Поиск пользователя..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <button
              className="btn btn-primary"
              type="button"
              onClick={() => fetchUsers()}
              style={{ whiteSpace: 'nowrap' }}
            >
              Найти
            </button>
          </div>

          <div className="chat-list-items">
            {users.map((u) => (
              <div
                key={u.user_id}
                className={`chat-item ${selectedUser?.user_id === u.user_id ? 'active' : ''}`}
                onClick={() => setSelectedUser(u)}
              >
                <div>
                  <div className="chat-item-title">{u.first_name || u.user_id} {u.username ? `(@${u.username})` : ''}</div>
                  <div className="chat-item-sub">
                    {u.phone_number ? `📞 ${u.phone_number}` : '📨 без телефона'} · 💬 {u.conversations_count}
                  </div>
                </div>
                <div className="pill">ID {u.user_id}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card chat-window">
          <div className="chat-header">
            <div>
              <div style={{ fontWeight: 900, fontSize: 16 }}>
                {selectedUser ? (selectedUser.first_name || selectedUser.user_id) : 'Выберите пользователя'}
                {selectedUser?.username ? <span style={{ color: 'var(--muted)' }}> @{selectedUser.username}</span> : null}
              </div>
              {selectedUser?.telegram_link ? (
                <div className="chat-item-sub">
                  <a href={selectedUser.telegram_link} target="_blank" rel="noopener noreferrer">Открыть Telegram</a>
                </div>
              ) : null}
            </div>
            <div className="pill">RAG</div>
          </div>

          <div className="chat-messages">
            {!selectedUser ? (
              <div style={{ color: 'var(--muted)' }}>Выберите пользователя слева</div>
            ) : (
              thread.flatMap((conv) => ([
                {
                  key: `${conv.id}-q`,
                  type: 'user',
                  text: conv.question,
                  meta: new Date(conv.created_at).toLocaleString('ru-RU')
                },
                {
                  key: `${conv.id}-a`,
                  type: 'bot',
                  text: conv.answer,
                  meta: `релевантность: ${(conv.avg_similarity || 0).toFixed(3)}`
                }
              ])).map((m) => (
                <div key={m.key} className={`bubble ${m.type}`}>
                  {m.text}
                  <div className="bubble-meta">{m.meta}</div>
                </div>
              ))
            )}
            <div ref={bottomRef} />
          </div>

          {selectedUser ? (
            <form className="composer" onSubmit={sendQuickReply}>
              <div className="composer-card">
                <textarea
                  value={composerText}
                  onChange={(e) => setComposerText(e.target.value)}
                  placeholder="Написать сообщение пользователю…"
                />
                <div className="file-pill">
                  {composerFile ? `📎 ${composerFile.name}` : '📎 Можно прикрепить фото или файл'}
                </div>
              </div>

              <div className="composer-actions">
                <label className="icon-btn" title="Прикрепить файл">
                  📎
                  <input
                    className="hidden-file"
                    type="file"
                    onChange={(e) => setComposerFile(e.target.files?.[0] || null)}
                  />
                </label>
                <button className="btn btn-success" type="submit" disabled={sending}>
                  {sending ? 'Отправка…' : 'Отправить'}
                </button>
              </div>
            </form>
          ) : null}
        </div>
      </div>
    </div>
  )
}

export default Conversations

