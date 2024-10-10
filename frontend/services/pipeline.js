import { api } from './api'

export const getPipeline = ({ }) => {
    return api.get('/api/pipelines/')
}