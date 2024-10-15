import Box from '@mui/material/Box'
import Radio from '@mui/material/Radio'
import { DataGrid } from '@mui/x-data-grid'
import moment from 'moment'
import PropTypes from 'prop-types'
import * as React from 'react'
import { useQuery } from 'react-query'
import { getProductsSpecz } from '../services/product'

const DataTableWrapper = ({ filters, query, onProductSelect }) => {
  const [page, setPage] = React.useState(0)
  const [pageSize, setPageSize] = React.useState(10)
  const [selectedRowId, setSelectedRowId] = React.useState(null)

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

  const handleRowSelection = rowId => {
    setSelectedRowId(rowId)
    if (onProductSelect) {
      onProductSelect(rowId)
    }
  }

  const columns = [
    {
      field: 'select',
      headerName: '',
      renderCell: params => (
        <Radio
          checked={selectedRowId === params.row.id}
          onChange={() => handleRowSelection(params.row.id)}
        />
      ),
      width: 50
    },
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
    <>
      <Box sx={{ height: 400, width: '100%' }}>
        <DataGrid
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
          disableColumnMenu
          disableColumnSelector
          loading={isLoading}
          localeText={{
            noRowsLabel: isLoading ? 'Loading...' : 'No products found'
          }}
          onRowClick={params => handleRowSelection(params.row.id)}
        />
      </Box>
    </>
  )
}

DataTableWrapper.propTypes = {
  filters: PropTypes.object,
  query: PropTypes.string,
  onProductSelect: PropTypes.func
}

DataTableWrapper.defaultProps = {
  filters: {},
  query: ''
}

export default DataTableWrapper
