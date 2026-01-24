import { useEffect, useState } from 'react'
import api from '../api/client'

function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchUsers()
  }, [search])

  const fetchUsers = async () => {
    try {
      const params = search ? { search } : {}
      const response = await api.get('/users', { params })
      setUsers(response.data.users)
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="card">Загрузка...</div>

  return (
    <div>
      <h1>Пользователи</h1>
      <div className="card">
        <input
          type="text"
          placeholder="Поиск по имени, username или телефону..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: '100%', padding: '10px', marginBottom: '20px' }}
        />
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Имя</th>
              <th>Username</th>
              <th>Телефон</th>
              <th>Диалоги</th>
              <th>Записи</th>
              <th>Telegram</th>
              <th>Дата регистрации</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.user_id}>
                <td>{user.user_id}</td>
                <td>{user.first_name || '-'}</td>
                <td>@{user.username || '-'}</td>
                <td>{user.phone_number || '-'}</td>
                <td>{user.conversations_count}</td>
                <td>{user.registrations_count}</td>
                <td>
                  <a href={user.telegram_link} target="_blank" rel="noopener noreferrer">
                    Открыть
                  </a>
                </td>
                <td>{new Date(user.created_at).toLocaleDateString('ru-RU')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Users

