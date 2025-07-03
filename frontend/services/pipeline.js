import { api } from './api'

export const getPipelineByName = ({ name }) => {
    return api.get(`/api/pipelines/?name=${name}`)
}