import { api } from './api'


export const getReleases = ({ }) => {
    return api.get('/api/releases/').then(res => res.data)
}