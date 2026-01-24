import { useEffect, useState } from 'react'
import api from '../api/client'

function Messages() {
  const [users, setUsers] = useState([])
  const [broadcasts, setBroadcasts] = useState([])
  const [selectedUserId, setSelectedUserId] = useState('')
  const [message, setMessage] = useState('')
  const [messageFile, setMessageFile] = useState(null)
  const [broadcastMessage, setBroadcastMessage] = useState('')
  const [scheduledDate, setScheduledDate] = useState('')
  const [scheduledTime, setScheduledTime] = useState('')
  const [broadcastFile, setBroadcastFile] = useState(null)

  useEffect(() => {
    fetchUsers()
    fetchBroadcasts()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await api.get('/users')
      setUsers(response.data.users)
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  const fetchBroadcasts = async () => {
    try {
      const response = await api.get('/messages/broadcasts')
      setBroadcasts(response.data)
    } catch (error) {
      console.error('Error fetching broadcasts:', error)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!selectedUserId) return
    if (!message && !messageFile) return

    try {
      const formData = new FormData()
      formData.append('user_id', selectedUserId)
      formData.append('message', message || '')
      if (messageFile) formData.append('file', messageFile)

      await api.post('/messages/send', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      alert('Сообщение отправлено!')
      setMessage('')
      setSelectedUserId('')
      setMessageFile(null)
    } catch (error) {
      alert('Ошибка при отправке: ' + error.message)
    }
  }

  const handleBroadcast = async (e) => {
    e.preventDefault()
    if (!broadcastMessage && !broadcastFile) return

    try {
      const formData = new FormData()
      formData.append('message', broadcastMessage || '')
      if (scheduledDate && scheduledTime) formData.append('scheduled_at', `${scheduledDate}T${scheduledTime}`)
      if (broadcastFile) formData.append('file', broadcastFile)

      await api.post('/messages/broadcast', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      alert('Рассылка создана!')
      setBroadcastMessage('')
      setScheduledDate('')
      setScheduledTime('')
      setBroadcastFile(null)
      fetchBroadcasts()
    } catch (error) {
      alert('Ошибка при создании рассылки: ' + error.message)
    }
  }

  return (
    <div>
      <h1>Сообщения</h1>

      <div className="card">
        <h2>Отправить сообщение пользователю</h2>
        <form onSubmit={handleSendMessage}>
          <div className="form-group">
            <label>Пользователь</label>
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              required
            >
              <option value="">Выберите пользователя</option>
              {users.map((user) => (
                <option key={user.user_id} value={user.user_id}>
                  {user.first_name || user.user_id} (@{user.username || 'N/A'})
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Сообщение</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows="5"
            />
            <div className="file-pill">
              {messageFile ? `Файл: ${messageFile.name}` : 'Можно прикрепить фото или файл'}
            </div>
            <input
              type="file"
              onChange={(e) => setMessageFile(e.target.files?.[0] || null)}
              style={{ marginTop: '10px' }}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Отправить
          </button>
        </form>
      </div>

      <div className="card">
        <h2>Создать рассылку</h2>
        <form onSubmit={handleBroadcast}>
          <div className="form-group">
            <label>Сообщение</label>
            <textarea
              value={broadcastMessage}
              onChange={(e) => setBroadcastMessage(e.target.value)}
              rows="5"
            />
            <div className="file-pill">
              {broadcastFile ? `Файл: ${broadcastFile.name}` : 'Можно прикрепить фото или файл'}
            </div>
            <input
              type="file"
              onChange={(e) => setBroadcastFile(e.target.files?.[0] || null)}
              style={{ marginTop: '10px' }}
            />
          </div>
          <div className="form-group">
            <label>Запланировать на (оставьте пустым для мгновенной рассылки)</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <input
                type="date"
                value={scheduledDate}
                onChange={(e) => setScheduledDate(e.target.value)}
              />
              <input
                type="time"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
              />
            </div>
          </div>
          <button type="submit" className="btn btn-success">
            {scheduledDate && scheduledTime ? 'Запланировать рассылку' : 'Отправить всем'}
          </button>
        </form>
      </div>

      <div className="card">
        <h2>История рассылок</h2>
        {broadcasts.length === 0 ? (
          <div style={{ color: 'var(--muted)', marginBottom: 10 }}>
            Расссылок пока нет. Создайте рассылку выше — она появится здесь.
          </div>
        ) : null}
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Сообщение</th>
              <th>Получателей</th>
              <th>Статус</th>
              <th>Вложение</th>
              <th>Запланировано</th>
              <th>Отправлено</th>
            </tr>
          </thead>
          <tbody>
            {broadcasts.map((broadcast) => (
              <tr key={broadcast.id}>
                <td>{broadcast.id}</td>
                <td style={{ maxWidth: '300px' }}>{broadcast.message.substring(0, 100)}...</td>
                <td>{broadcast.target_count}</td>
                <td>
                  <span style={{
                    color: broadcast.status === 'completed' ? '#27ae60' : 
                           broadcast.status === 'failed' ? '#e74c3c' : '#f39c12'
                  }}>
                    {broadcast.status}
                  </span>
                </td>
                <td>{broadcast.attachment_name ? `${broadcast.attachment_name}` : '-'}</td>
                <td>{broadcast.scheduled_at ? new Date(broadcast.scheduled_at).toLocaleString('ru-RU') : '-'}</td>
                <td>{broadcast.sent_at ? new Date(broadcast.sent_at).toLocaleString('ru-RU') : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Messages

