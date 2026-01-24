import { useEffect, useState } from 'react'
import api from '../api/client'

function Settings() {
  const [botSettings, setBotSettings] = useState([])
  const [ragConfig, setRagConfig] = useState({
    chunk_size: 500,
    chunk_overlap: 100,
    n_results: 3,
    use_reranking: true,
    min_similarity_threshold: 0.3
  })
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ;(async () => {
      await Promise.all([fetchBotSettings(), fetchRAGConfig(), fetchPrompt()])
      setLoading(false)
    })()
  }, [])

  const fetchBotSettings = async () => {
    try {
      const response = await api.get('/settings/bot')
      setBotSettings(response.data)
    } catch (error) {
      console.error('Error fetching bot settings:', error)
    }
  }

  const fetchRAGConfig = async () => {
    try {
      const response = await api.get('/settings/rag/config')
      setRagConfig({
        chunk_size: response.data.chunk_size ?? 500,
        chunk_overlap: response.data.chunk_overlap ?? 100,
        n_results: response.data.n_results ?? 3,
        use_reranking: response.data.use_reranking ?? true,
        min_similarity_threshold: response.data.min_similarity_threshold ?? 0.3
      })
    } catch (error) {
      console.error('Error fetching RAG config:', error)
    }
  }

  const fetchPrompt = async () => {
    try {
      const response = await api.get('/settings/rag/prompt')
      setPrompt(response.data.prompt || '')
    } catch (error) {
      console.error('Error fetching prompt:', error)
    }
  }

  const updateBotSetting = async (key, value) => {
    try {
      await api.put(`/settings/bot/${key}`, { value })
      alert('Настройка обновлена!')
      fetchBotSettings()
    } catch (error) {
      alert('Ошибка при обновлении: ' + error.message)
    }
  }

  const updateRAGConfig = async () => {
    try {
      await api.put('/settings/rag/config', ragConfig)
      alert('Конфигурация RAG обновлена!')
    } catch (error) {
      alert('Ошибка при обновлении: ' + error.message)
    }
  }

  const updatePrompt = async () => {
    try {
      await api.put('/settings/rag/prompt', { prompt })
      alert('Промпт обновлен!')
    } catch (error) {
      alert('Ошибка при обновлении: ' + error.message)
    }
  }

  if (loading) return <div className="card">Загрузка...</div>

  return (
    <div>
      <h1>Настройки</h1>

      <div className="card">
        <h2>Настройки бота</h2>
        {botSettings.map((setting) => (
          <div key={setting.key} className="form-group">
            <label>{setting.description || setting.key}</label>
            <textarea
              value={setting.value}
              onChange={(e) => {
                const updated = botSettings.map(s => 
                  s.key === setting.key ? { ...s, value: e.target.value } : s
                )
                setBotSettings(updated)
              }}
              rows="3"
            />
            <button
              className="btn btn-primary"
              onClick={() => updateBotSetting(setting.key, setting.value)}
              style={{ marginTop: '10px' }}
            >
              Сохранить
            </button>
          </div>
        ))}
      </div>

      <div className="card">
        <h2>Настройки RAG</h2>
        <div className="form-group">
          <label>Размер чанка</label>
          <input
            type="number"
            value={ragConfig.chunk_size}
            onChange={(e) => setRagConfig({ ...ragConfig, chunk_size: parseInt(e.target.value) })}
          />
        </div>
        <div className="form-group">
          <label>Перекрытие чанков</label>
          <input
            type="number"
            value={ragConfig.chunk_overlap}
            onChange={(e) => setRagConfig({ ...ragConfig, chunk_overlap: parseInt(e.target.value) })}
          />
        </div>
        <div className="form-group">
          <label>Количество результатов</label>
          <input
            type="number"
            value={ragConfig.n_results}
            onChange={(e) => setRagConfig({ ...ragConfig, n_results: parseInt(e.target.value) })}
          />
        </div>
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={ragConfig.use_reranking}
              onChange={(e) => setRagConfig({ ...ragConfig, use_reranking: e.target.checked })}
            />
            Использовать re-ranking
          </label>
        </div>
        <div className="form-group">
          <label>Минимальный порог релевантности</label>
          <input
            type="number"
            step="0.1"
            value={ragConfig.min_similarity_threshold}
            onChange={(e) => setRagConfig({ ...ragConfig, min_similarity_threshold: parseFloat(e.target.value) })}
          />
        </div>
        <button className="btn btn-primary" onClick={updateRAGConfig}>
          Сохранить конфигурацию
        </button>
      </div>

      <div className="card">
        <h2>Промпт для LLM</h2>
        <div className="form-group">
          <label>Системный промпт</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows="15"
            placeholder="Введите промпт..."
          />
        </div>
        <button className="btn btn-primary" onClick={updatePrompt}>
          Сохранить промпт
        </button>
      </div>
    </div>
  )
}

export default Settings

