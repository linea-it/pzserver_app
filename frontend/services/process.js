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

export const getProcess = process_id => {
    return api.get(`/api/processes/${process_id}/`).then(res => res.data)
}

export const getProcessLogs = async process_id => {
    const res = await api.get(`/api/processes/${process_id}/logs/`)
    return res.data
}

export const getProcessByUpload = (product_id) => {
    return api.get(`/api/processes/`, { params: { upload: product_id } }).then((res) => {
        if (res.data.count == 1) {
            return res.data.results[0]
        } else {
            return null
        }
    });
}