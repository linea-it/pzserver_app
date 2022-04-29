import { api } from './api'

export const getReleases = ({ }) => {
  return api.get('/releases/').then(res => res.data)
}

export const getProductTypes = ({ }) => {
  return api.get('/product-types/').then(res => res.data)
}

export const getProducts = ({ filters = {}, search, limit, offset, sort = [] }) => {
  let ordering = null

  // Tratamento da ordenação no DRF
  // https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter
  if (sort.length === 1) {
    ordering = sort[0].field

    if (sort[0].sort === 'desc') {
      ordering = '-' + ordering
    }
  }

  // Tratamento dos filtros
  const params = { offset, limit, ordering, search }

  // TODO: Tratar os objeto de filtro, cada propriedade deve virar um elemento no objeto params
  // if (filters) {
  //   filters.forEach(element => {
  //     params[element.property] = element.value
  //   })
  // }
  console.log(params)
  return api.get('/products/', { params }).then(res => res.data)
}
