import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Stack from '@mui/material/Stack'
import { DataGrid, GridToolbarFilterButton } from '@mui/x-data-grid'
import moment from 'moment'
import PropTypes from 'prop-types'
import * as React from 'react'
import { useEffect } from 'react'
import { useQuery } from 'react-query'
import { getProductsSpecz } from '../services/product'

const DataTableWrapper = ({
  filters = {},
  query = '',
  onSelectionChange = () => {},
  clearSelection = false
}) => {
  const [page, setPage] = React.useState(0)
  const [pageSize, setPageSize] = React.useState(25)
  const [selectedRows, setSelectedRows] = React.useState([])

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
      keepPreviousData: true,
      staleTime: Infinity,
      refetchInterval: false,
      retry: false
    }
  )

  // Reset paginação quando a busca/filtros mudam.
  // Serializa os filtros: como `filters` é um objeto recriado a cada render,
  // usar ele direto como dependência dispararia o efeito em todo render,
  // travando a paginação sempre na primeira página.
  const filtersKey = JSON.stringify(filters)
  useEffect(() => {
    setPage(0)
  }, [query, filtersKey])

  const handleSelectionChange = selection => {
    const currentPageProducts = data?.results || []
    const previousSelection = selectedRows.filter(
      row => !currentPageProducts.some(p => p.id === row.id)
    )
    const newSelectionFromPage = selection
      .map(id => currentPageProducts.find(product => product.id === id))
      .filter(Boolean)

    const merged = [...previousSelection, ...newSelectionFromPage]
    setSelectedRows(merged)
    onSelectionChange(merged)
  }

  const handleClearAll = () => {
    setSelectedRows([])
    onSelectionChange([])
  }

  useEffect(() => {
    if (clearSelection) {
      setSelectedRows([])
    }
  }, [clearSelection])

  const visibleIds = new Set((data?.results || []).map(r => r.id))
  const visibleSelectedCount = selectedRows.filter(r =>
    visibleIds.has(r.id)
  ).length
  const hiddenSelectedCount = selectedRows.length - visibleSelectedCount

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
    <Stack spacing={1}>
      {selectedRows.length > 0 && (
        <Alert
          severity={hiddenSelectedCount > 0 ? 'warning' : 'info'}
          icon={<InfoOutlinedIcon fontSize="inherit" />}
          action={
            <Button color="inherit" size="small" onClick={handleClearAll}>
              Clear all
            </Button>
          }
          sx={{ py: 0 }}
        >
          <Chip
            label={`${selectedRows.length} selected`}
            size="small"
            color="primary"
            sx={{ mr: 1 }}
          />
          {hiddenSelectedCount > 0 && (
            <span>
              {hiddenSelectedCount} item{hiddenSelectedCount > 1 ? 's' : ''}{' '}
              currently hidden by search/filter. They will still be submitted.
            </span>
          )}
        </Alert>
      )}
      <Box
        sx={{
          height: 400,
          minHeight: 200,
          width: '100%',
          resize: 'vertical',
          overflow: 'auto'
        }}
      >
        <DataGrid
          checkboxSelection
          keepNonExistentRowsSelected
          getRowId={row => row.id || row.unique_key}
          rows={data?.results || []}
          columns={columns}
          loading={isLoading}
          paginationMode="server"
          page={page}
          pageSize={pageSize}
          rowCount={data?.count || 0}
          onPageChange={newPage => setPage(newPage)}
          onPageSizeChange={newPageSize => setPageSize(newPageSize)}
          rowsPerPageOptions={[10, 25, 50]}
          onSelectionModelChange={newSelection =>
            handleSelectionChange(newSelection)
          }
          localeText={{
            noRowsLabel: isLoading ? 'Loading...' : 'No products found'
          }}
          selectionModel={selectedRows.map(row => row.id)}
          components={{ Toolbar: GridToolbarFilterButton }}
        />
      </Box>
    </Stack>
  )
}

DataTableWrapper.propTypes = {
  filters: PropTypes.object,
  query: PropTypes.string,
  onSelectionChange: PropTypes.func,
  clearSelection: PropTypes.bool
}

export default DataTableWrapper
