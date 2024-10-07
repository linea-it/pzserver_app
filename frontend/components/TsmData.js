import { Alert, Box } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import PropTypes from 'prop-types'
import * as React from 'react'
import { useQuery } from 'react-query'
import moment from 'moment'
import { getProducts } from '../services/product'

const columns = [
  {
    field: 'display_name',
    headerName: 'Name',
    sortable: true,
    flex: 1
  },
  {
    field: 'uploaded_by',
    headerName: 'Uploaded By',
    flex: 1,
    sortable: false
  },
  {
    field: 'created_at',
    headerName: 'Created at',
    sortable: true,
    width: 200,
    valueFormatter: (params) => {
      if (!params.value) {
        return ''
      }
      return moment(params.value).format('YYYY-MM-DD')
    }
  }
]

export default function DataTableWrapper({ filters, query }) {
  const [page, setPage] = React.useState(0)
  const [pageSize, setPageSize] = React.useState(10)

  const { data, status, error, isLoading } = useQuery(
    ['productData', { filters, query, page, pageSize }],
    () => getProducts({
      filters,
      page,
      page_size: pageSize,
      sort: [{ field: 'created_at', sort: 'desc' }],
      search: query
    }),
    {
      staleTime: Infinity,
      refetchInterval: false,
      retry: false
    }
  )

  if (error) return <Alert severity="error">Error loading data. Please try again.</Alert>

  const filteredData = data?.results?.filter(product => product.product_type_name === 'Spec-z Catalog') || []

  return (
    <>
      <Box sx={{ height: 400, width: '100%' }}>
        <DataGrid
          rows={filteredData}
          columns={columns}
          paginationMode="server"
          page={page}
          pageSize={pageSize}
          onPageChange={(newPage) => setPage(newPage)}
          onPageSizeChange={(newPageSize) => setPageSize(newPageSize)}
          rowsPerPageOptions={[5, 10, 25]}
          disableColumnMenu
          disableColumnSelector
          loading={isLoading}
          localeText={{
            noRowsLabel: filteredData.length === 0 && !isLoading ? 'No products found' : 'Loading...',
          }}
        />
      </Box>
      <Box
        sx={{
          mt: 2,
          display: 'flex',
          justifyContent: 'flex-end',
          fontSize: '14px'
        }}
      >
        {`Showing ${filteredData.length} products`}
      </Box>
    </>
  )
}

DataTableWrapper.propTypes = {
  filters: PropTypes.object,
  query: PropTypes.string
}

DataTableWrapper.defaultProps = {
  filters: {},
  query: ''
}