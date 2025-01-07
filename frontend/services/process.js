import { api } from './api'

export const submitProcess = (processData) => {
    return api.post('/api/processes/', processData)
        .then(response => {
            if (response.status === 201) {
                return response
            } else {
                throw new Error('Failed to submit process')
            }
        })
        .catch(error => {
            console.error('Error response:', error.response || error.message)
            if (error.response) {
                console.error('Error details:', error.response.data)
            }
            throw error
        })
}