import { useEffect, useState } from 'react'
import api from '../api/client'

function Documents() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [file, setFile] = useState(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/documents')
      setDocuments(response.data.documents)
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      await api.post('/documents', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      alert('Документ успешно добавлен!')
      setFile(null)
      fetchDocuments()
    } catch (error) {
      alert('Ошибка при добавлении документа: ' + error.message)
    }
  }

  const handleDelete = async (docId) => {
    if (!confirm('Удалить документ?')) return

    try {
      await api.delete(`/documents/${docId}`)
      alert('Документ удален!')
      fetchDocuments()
    } catch (error) {
      alert('Ошибка при удалении: ' + error.message)
    }
  }

  if (loading) return <div className="card">Загрузка...</div>

  return (
    <div>
      <h1>Документы базы знаний</h1>
      
      <div className="card">
        <h2>Добавить документ</h2>
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              accept=".docx,.doc,.pdf,.txt"
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={!file}>
            Загрузить
          </button>
        </form>
      </div>

      <div className="card">
        <h2>Список документов</h2>
        {documents.length === 0 ? (
          <div style={{ color: 'var(--muted)' }}>
            Документов пока нет. Загрузите файл выше.
          </div>
        ) : null}
        <table className="table">
          <thead>
            <tr>
              <th>ID документа</th>
              <th>Количество чанков</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.document_id}>
                <td>{doc.document_id}</td>
                <td>{doc.chunks_count}</td>
                <td>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDelete(doc.document_id)}
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Documents

