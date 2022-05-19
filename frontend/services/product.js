/* eslint-disable camelcase */
import { api } from './api'
import forIn from 'lodash/forIn'
import isEmpty from 'lodash/isEmpty'

export const getReleases = ({ }) => {
  return api.get('/releases/').then(res => res.data)
}

export const getProductTypes = ({ }) => {
  return api.get('/product-types/').then(res => res.data)
}

export const getProducts = ({
  filters = {},
  search,
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
  if (search === '') {
    forIn(filters, function (value, key) {
      if (value != null) {
        params[key] = value
      }
    })
  }

  return api.get('/products/', { params }).then(res => res.data)
}
