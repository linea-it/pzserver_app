/* eslint-disable camelcase */
import { api } from './api'

export const getReleases = () => {
  return api.get('/api/releases/').then(res => res.data)
}

export const getReleaseHatsConfig = releaseId => {
  return api
    .get(`/api/releases/${releaseId}/hats_config/`)
    .then(res => res.data)
}
