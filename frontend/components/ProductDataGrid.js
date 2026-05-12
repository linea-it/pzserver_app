import { Alert } from '@mui/material'
import Box from '@mui/material/Box'
import { DataGrid } from '@mui/x-data-grid'
import uniqueId from 'lodash/uniqueId'
import PropTypes from 'prop-types'
import * as React from 'react'
import { useQuery } from 'react-query'

import { fetchProductData } from '../services/product'

export default function ProductDataGrid(props) {
  const { productId } = props
  const [rows, setRows] = React.useState([])
  const [columns, setColumns] = React.useState([])
  const [rowCount, setRowCount] = React.useState(0)
  const [page, setPage] = React.useState(0)
  const [pageSize, setPageSize] = React.useState(10)
  const [error, setError] = React.useState(null)
  const [processingPollCount, setProcessingPollCount] = React.useState(0)

  React.useEffect(() => {
    setProcessingPollCount(0)
  }, [productId])

  const {
    status,
    isLoading,
    data,
    error: queryError
  } = useQuery(
    ['productData', { productId, page, pageSize }],
    fetchProductData,
    {
      enabled: !!productId,
      staleTime: Infinity,
      refetchInterval: latestData => {
        if (latestData?._httpStatus !== 202) {
          return false
        }

        if (processingPollCount <= 3) return 3000
        if (processingPollCount <= 6) return 4000
        return 5000
      },
      refetchOnWindowFocus: false,
      retry: false
    }
  )

  React.useEffect(() => {
    if (status === 'success' && data) {
      if (data._httpStatus === 202) {
        if (data.message) {
          console.log(`Product preview status: ${data.message}`)
        }
        setProcessingPollCount(prev => prev + 1)
        setError(null)
        setRows([])
        setColumns([])
        return
      }

      setProcessingPollCount(0)
      setError(null)
      setRowCount(data.count)
      setRows(data.results)
      makeColumns(data.columns)
    } else if (status === 'error') {
      setProcessingPollCount(0)
      const message =
        queryError?.response?.data?.message ||
        'Error loading data. Please try again.'
      setError(message)
    }
  }, [status, data, queryError])

  if (isLoading) return <p>Loading...</p>
  if (status === 'success' && data?._httpStatus === 202) {
    return <Alert severity="info">Loading...</Alert>
  }
  if (error !== null) return <Alert severity="error">{error}</Alert>
  if (status !== 'success' || !data) return null

  function makeColumns(names) {
    const cols = names.map(name => {
      return {
        field: name,
        headerName: name,
        sortable: false,
        flex: 1,
        minWidth: 100
      }
    })
    setColumns(cols)
  }

  return (
    <>
      {status === 'success' && (
        <DataGrid
          getRowId={() => uniqueId('id_')}
          rows={rows}
          columns={columns}
          disableSelectionOnClick
          autoHeight
          // sortingMode="server"
          // sortModel={sortModel}
          // onSortModelChange={handleSortModelChange}
          paginationMode="server"
          rowCount={Number.isFinite(rowCount) ? rowCount : 0}
          // pagination
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
            noRowsLabel: isLoading ? 'No rows' : 'Loading...'
          }}
        />
      )}
      <Box
        sx={{
          mt: 2,
          display: 'flex',
          justifyContent: 'flex-end',
          fontSize: '14px'
        }}
      >
        10 First Rows
      </Box>
    </>
  )
}
ProductDataGrid.propTypes = {
  productId: PropTypes.number
}
