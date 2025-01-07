import Box from '@mui/material/Box'
import { DataGrid } from '@mui/x-data-grid'
import moment from 'moment'
import PropTypes from 'prop-types'
import * as React from 'react'
import { useQuery } from 'react-query'
import { getProductsSpecz } from '../services/product'

const DataTableWrapper = ({ filters, query, onSelectionChange }) => {
  const [page, setPage] = React.useState(0)
  const [pageSize, setPageSize] = React.useState(10)
  const setSelectedRows = React.useState([])[1]

  const { data, isLoading } = useQuery(
    ['productData', { filters, query, page, pageSize }],
    () =>
      getProductsSpecz({
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

  const handleSelectionChange = selection => {
    const selectedProducts = selection.map(
      id => data?.results?.find(product => product.id === id) || {}
    )
    setSelectedRows(selectedProducts)
    onSelectionChange(selectedProducts)
  }

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
      valueFormatter: params => {
        if (!params.value) {
          return ''
        }
        return moment(params.value).format('YYYY-MM-DD')
      }
    }
  ]

  return (
    <Box sx={{ height: 300, width: '100%' }}>
      <DataGrid
        pageSizeOptions={[5, 10]}
        checkboxSelection
        getRowId={row => row.id || row.unique_key}
        rows={data?.results || []}
        columns={columns}
        paginationMode="server"
        page={page}
        pageSize={pageSize}
        rowCount={data?.count || 0}
        onPageChange={newPage => setPage(newPage)}
        onPageSizeChange={newPageSize => setPageSize(newPageSize)}
        rowsPerPageOptions={[10]}
        loading={isLoading}
        onSelectionModelChange={newSelection =>
          handleSelectionChange(newSelection)
        }
        localeText={{
          noRowsLabel: isLoading ? 'Loading...' : 'No products found'
        }}
      />
    </Box>
  )
}

DataTableWrapper.propTypes = {
  filters: PropTypes.object,
  query: PropTypes.string,
  onSelectionChange: PropTypes.func
}

DataTableWrapper.defaultProps = {
  filters: {},
  query: '',
  onSelectionChange: () => {}
}

export default DataTableWrapper
