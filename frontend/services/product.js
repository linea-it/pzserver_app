/* eslint-disable camelcase */
import forIn from 'lodash/forIn'
import { api } from './api'
// import isEmpty from 'lodash/isEmpty'

export const getProductTypes = ({ }) => {
  return api.get('/api/product-types/?ordering=order').then(res => res.data)
}

export const downloadProduct = (id, internalName) => {
  return api.get('/api/products/' + id + '/download/', {
    responseType: 'blob',
    timeout: 120000
  })
}

export const MAX_UPLOAD_SIZE = 200

// Exemplo de como enviar arquivo via upload: https://dev.to/thomz/uploading-images-to-django-rest-framework-from-forms-in-react-3jhj
export const createProduct = data => {
  const formData = new FormData()

  formData.append('display_name', data.display_name)
  formData.append('release', data.release)
  formData.append('product_type', data.product_type)
  // formData.append('main_file', data.main_file)
  // formData.append('description_file', data.description_file)
  formData.append('official_product', data.official_product)
  formData.append('release_year', data.release_year)
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
  formData.append('official_product', data.official_product)
  formData.append('survey', data.survey)
  formData.append('pz_code', data.pz_code)
  formData.append('description', data.description)
  formData.append('status', data.status)

  if (data.release_year !== '' && data.release_year !== null) {
    formData.append('release_year', data.release_year)
  }

  if (data.release !== '' && data.release !== null) {
      formData.append('release', data.release)
  }

  if (data.product_type !== '' && data.product_type !== null) {
    formData.append('product_type', data.product_type)
  }

  return api.patch(`/api/products/${data.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const changeProductStatus = (productId, status) => {
  const formData = new FormData()
  formData.append('status', status)

  return api.patch(`/api/products/${productId}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const registryProduct = product_id => {
  return api.post(`/api/products/${product_id}/registry/`).then(res => res.data)
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

export const getProductByInternalName = (internalName) => {
  return api.get(`/api/products/`, { params: { internal_name: internalName } }).then((res) => {
    if (res.data.count == 1) {
      return res.data.results[0]
    } else {
      return undefined
    }
  });

}

export const fetchProductData = ({ queryKey }) => {
  const [_, params] = queryKey
  const { productId, page, pageSize: page_size } = params
  if (!productId) {
    return
  }
  page += 1
  return api.get(`/api/products/${productId}/read_data/`, { timeout: 120000, params: { page, page_size } }).then(res => res.data)
}

export const deleteProduct = product_id => {
  return api.delete(`/api/products/${product_id}/`)
}

export const getProductPendingPublication = () => {
  return api.get('/api/products/pending_publication/').then(res => res.data)
}

export const getProductContents = product_id => {
  return api
    .get('/api/product-contents/', {
      params: { product: product_id, ordering: 'order' }
    })
    .then(res => res.data)
}

export const contentAssociation = (pc_id, ucd, alias) => {
  return api
    .patch(`/api/product-contents/${pc_id}/`, {
      ucd: ucd === '' ? null : ucd,
      alias: alias === '' ? null : alias
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
    timeout: 120000,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: onUploadProgress
  })
}


export const getProductsSpecz = ({
  filters = {},
  search = '',
  page = 0,
  page_size = 25,
  sort = []
}) => {
  // Esse endpoint retorna apenas os catalogos cujo o product type é = 'redshift' e status = 1
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

  return api.get('/api/products-specz/', { params }).then(res => res.data)
}