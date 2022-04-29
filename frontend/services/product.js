import { api } from './api'

export const getReleases = ({ }) => {
  return api.get('/releases/').then(res => res.data)
}

export const getProductTypes = ({ }) => {
  return api.get('/product-types/').then(res => res.data)
}

export const getProducts = ({ filters = {}, search, page = 0, page_size = 25, sort = [] }) => {
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

  // TODO: Tratar os objeto de filtro, cada propriedade deve virar um elemento no objeto params
  // if (filters) {
  //   filters.forEach(element => {
  //     params[element.property] = element.value
  //   })
  // }

  // Todos os Query Params
  const params = { page, page_size, ordering, search }
  console.log(params)
  return api.get('/products/', { params }).then(res => res.data)
}
