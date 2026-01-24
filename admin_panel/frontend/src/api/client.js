import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Переопределяем метод для загрузки файлов, чтобы не устанавливать Content-Type
api.postForm = async function(url, formData, config = {}) {
  return this.post(url, formData, {
    ...config,
    headers: {
      ...config.headers,
      'Content-Type': 'multipart/form-data',
    },
  })
}

export default api

