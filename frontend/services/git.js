import { api } from './api'

export const getGitInfo = ({ }) => {
  return api.get('/api/git/').then(res => res.data)
}
