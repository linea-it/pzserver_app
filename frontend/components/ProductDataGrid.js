import { Alert } from '@mui/material'
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

  const { status, isLoading } = useQuery({
    queryKey: ['productData', { productId, page, pageSize }],
    queryFn: fetchProductData,
    keepPreviousData: true,
    refetchInterval: false,
    retry: false,
    onSuccess: data => {
      if (!data) {
        return
      }
      setRowCount(data.count)
      setRows(data.results)
      makeColumns(data.columns)
    },
    onError: error => {
      let msg = error.message
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        // console.log(error.response.data);
        // console.log(error.response.status);
        // console.log(error.response.headers);
        msg = error.response.data.message
      } else if (error.request) {
        // The request was made but no response was received
        // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
        // http.ClientRequest in node.js
        console.log(error.request)
      } else {
        // Something happened in setting up the request that triggered an Error
        console.log('Error', error.message)
      }
      setError(msg)
    }
  })

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

  function handleError() {
    return <Alert severity="error">{error}</Alert>
  }

  if (isLoading && rows.length === 0) return <p>Loading data...</p>
  if (error !== null) return handleError()
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
          rowCount={rowCount}
          pagination
          page={page}
          onPageChange={page => setPage(page)}
          pageSize={pageSize}
          onPageSizeChange={newPageSize => setPageSize(newPageSize)}
          rowsPerPageOptions={[10, 25, 50, 100]}
          loading={isLoading}
          disableColumnMenu
          disableColumnSelector
          localeText={{
            noRowsLabel: isLoading ? 'No rows' : 'Loading...',
          }}
        />
      )}
    </>
  )
}
ProductDataGrid.propTypes = {
  productId: PropTypes.number
}
