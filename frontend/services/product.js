/* eslint-disable camelcase */
import { api } from './api'
import forIn from 'lodash/forIn'
// import isEmpty from 'lodash/isEmpty'

export const getReleases = ({ }) => {
  return api.get('/api/releases/').then(res => res.data)
}

export const getProductTypes = ({ }) => {
  return api.get('/api/product-types/').then(res => res.data)
}

export const downloadProduct = (id, file_name) => {
  const link = document.createElement('a')
  link.target = '_blank'
  link.download = file_name
  api
    .get('/api/products/' + id + '/download/', {
      responseType: 'blob'
    })
    .then(res => {
      link.href = URL.createObjectURL(
        new Blob([res.data], { type: res.headers['content-type'] })
      )
      link.click()
    })
}

// Exemplo de como enviar arquivo via upload: https://dev.to/thomz/uploading-images-to-django-rest-framework-from-forms-in-react-3jhj
export const createProduct = data => {
  const formData = new FormData()

  formData.append('display_name', data.display_name)
  formData.append('release', data.release)
  formData.append('product_type', data.product_type)
  // formData.append('main_file', data.main_file)
  // formData.append('description_file', data.description_file)
  formData.append('official_product', data.official_product)
  formData.append('survey', data.survey)
  formData.append('pz_code', data.pz_code)
  formData.append('description', data.description)

  return api.post('/api/products/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const patchProduct = data => {
  const formData = new FormData()

  formData.append('display_name', data.display_name)
  formData.append('release', data.release)
  formData.append('product_type', data.product_type)
  // formData.append('main_file', data.main_file)
  // formData.append('description_file', data.description_file)
  formData.append('official_product', data.official_product)
  formData.append('survey', data.survey)
  formData.append('pz_code', data.pz_code)
  formData.append('description', data.description)

  return api.patch(`/api/products/${data.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getProducts = ({
  filters = {},
  search = '',
  page = 0,
  page_size = 25,
  sort = []
}) => {
  // // Obrigatório o filtro por release para fazer a requisição
  // if (isEmpty(filters) || filters.release === '') {
  //   return {
  //     count: 0,
  //     results: []
  //   }
  // }
  let ordering = null

  // Ordenação no DRF
  // https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter
  if (sort.length === 1) {
    ordering = sort[0].field

    if (sort[0].sort === 'desc') {
      ordering = '-' + ordering
    }
  }
  // Paginação no DRF
  // https://www.django-rest-framework.org/api-guide/pagination/#pagenumberpagination
  // Django não aceita pagina 0 por isso é somado 1 ao numero da página.
  page += 1

  // Todos os Query Params
  const params = { page, page_size, ordering, search }

  // Filtros no DRF
  // https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html
  // cada filtro que tiver valor deve virar uma propriedade no objeto params
  // Só aplica os filtros caso não tenha um search dessa forma a busca é feita em todos os registros.
  // o filtro official_product deve ser enviado no search também.
  if (search === '') {
    forIn(filters, function (value, key) {
      if (key === 'release' && value === '0') {
        params.release__isnull = true
        params.release = null
      } else {
        if (value != null) {
          params[key] = value
        }
      }
    })
  }

  params.official_product = filters.official_product

  return api.get('/api/products/', { params }).then(res => res.data)
}

export const getProduct = product_id => {
  return api.get(`/api/products/${product_id}/`).then(res => res.data)
}

export const getProductContents = product_id => {
  return api
    .get('/api/product-contents/', {
      params: { product_id: product_id, ordering: 'order' }
    })
    .then(res => res.data)
}

export const contentAssociation = (pc_id, ucd) => {
  return api
    .patch(`/api/product-contents/${pc_id}/`, {
      ucd: ucd === '' ? null : ucd
    })
    .then(res => res.data)
}

export const getProductFiles = product_id => {
  return api
    .get('/api/product-files/', {
      params: { product_id: product_id, ordering: 'role' }
    })
    .then(res => res.data)
}

export const deleteProductFile = id => {
  return api.delete(`/api/product-files/${id}/`)
}

export const createProductFile = (product_id, file, role, onUploadProgress) => {
  const formData = new FormData()

  formData.append('product', product_id)
  formData.append('file', file)
  formData.append('role', role)
  formData.append('type', file.type)

  return api.post('/api/product-files/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: onUploadProgress
  })
}
