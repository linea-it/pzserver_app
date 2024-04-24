import { api } from './api'

export const getVersion = ({ }) => {
  return api.get('/api/git/').then(res => res.data)
}
