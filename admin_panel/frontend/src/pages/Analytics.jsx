import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../api/client'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']

function Analytics() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/analytics')
      setAnalytics(response.data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="card">Загрузка...</div>
  if (!analytics) return <div className="card">Нет данных</div>

  const similarityData = Object.entries(analytics.similarity_distribution).map(([key, value]) => ({
    name: key === 'high' ? 'Высокая (≥0.7)' : 
          key === 'medium' ? 'Средняя (0.5-0.7)' :
          key === 'low' ? 'Низкая (0.3-0.5)' : 'Очень низкая (<0.3)',
    value
  }))

  return (
    <div>
      <h1>Аналитика</h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div className="card">
          <h3>Всего пользователей</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#3498db' }}>
            {analytics.total_users}
          </p>
        </div>
        <div className="card">
          <h3>Всего диалогов</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#27ae60' }}>
            {analytics.total_conversations}
          </p>
        </div>
        <div className="card">
          <h3>Записи на занятия</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#e74c3c' }}>
            {analytics.total_registrations}
          </p>
        </div>
        <div className="card">
          <h3>Средняя релевантность</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#f39c12' }}>
            {analytics.avg_similarity.toFixed(3)}
          </p>
        </div>
      </div>

      <div className="card">
        <h2>Диалоги по дням (последние 30 дней)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={analytics.conversations_by_day}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#3498db" name="Количество диалогов" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2>Распределение релевантности</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={similarityData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {similarityData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2>Топ вопросов</h2>
        <div style={{ color: 'var(--muted)', marginBottom: 10 }}>
          График показывает первые 10, полный список ниже.
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={analytics.top_questions}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="question" angle={-45} textAnchor="end" height={150} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#3498db" name="Количество" />
            <Bar dataKey="avg_similarity" fill="#27ae60" name="Средняя релевантность" />
          </BarChart>
        </ResponsiveContainer>

        <div style={{ overflowX: 'auto', marginTop: 14 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Вопрос</th>
                <th>Кол-во</th>
                <th>Средняя релевантность</th>
              </tr>
            </thead>
            <tbody>
              {(analytics.top_questions || []).map((q, idx) => (
                <tr key={idx}>
                  <td style={{ maxWidth: 700, whiteSpace: 'normal' }}>{q.question}</td>
                  <td>{q.count}</td>
                  <td>{(q.avg_similarity || 0).toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Analytics

