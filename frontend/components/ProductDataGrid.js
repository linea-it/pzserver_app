import { Alert } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import uniqueId from 'lodash/uniqueId'
import PropTypes from 'prop-types'
import * as React from 'react'
import { useQuery } from 'react-query'
import Box from '@mui/material/Box'

import { fetchProductData } from '../services/product'

export default function ProductDataGrid(props) {
  const { productId } = props
  const [rows, setRows] = React.useState([])
  const [columns, setColumns] = React.useState([])
  const [rowCount, setRowCount] = React.useState(0)
  const [page, setPage] = React.useState(0)
  const [pageSize, setPageSize] = React.useState(10)
  const [error, setError] = React.useState(null)

  const { status, isLoading, data } = useQuery(
    ['productData', { productId, page, pageSize }],
    fetchProductData,
    {
      enabled: !!productId,
      staleTime: Infinity,
      refetchInterval: false,
      retry: false
    }
  )

  React.useEffect(() => {
    if (status === 'success' && data) {
      setRowCount(data.count)
      setRows(data.results)
      makeColumns(data.columns)
    } else if (status === 'error') {
      setError('Error loading data. Please try again.')
    }
  }, [status, data])

  if (isLoading) return <p>Loading...</p>
  if (error !== null) return <Alert severity="error">{error}</Alert>
  if (status !== 'success' || !data) return null

  function makeColumns(names) {
    const cols = names.map(name => {
      return {
        field: name,
        headerName: name,
        sortable: false,
        flex: 1
      }
    })
    setColumns(cols)
  }

  return (
    <>
      {status === 'success' && (
        <DataGrid
          getRowId={row => uniqueId('id_')}
          rows={rows}
          columns={columns}
          disableSelectionOnClick
          autoHeight
          // sortingMode="server"
          // sortModel={sortModel}
          // onSortModelChange={handleSortModelChange}
          paginationMode="server"
          //rowCount={rowCount}
          page={page}
          onPageChange={page => setPage(page)}
          pageSize={pageSize}
          hideFooter
          onPageSizeChange={newPageSize => setPageSize(newPageSize)}
          
          rowsPerPageOptions={[10]}
          
          loading={isLoading}
          disableColumnMenu
          disableColumnSelector
          localeText={{
            noRowsLabel: isLoading ? 'No rows' : 'Loading...',
          }}
        /> 
      )}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', fontSize: '14px' }}>
        10 First Rows
      </Box>
    </>
  )
}
ProductDataGrid.propTypes = {
  productId: PropTypes.number
}
