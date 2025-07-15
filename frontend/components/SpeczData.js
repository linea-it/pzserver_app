import Box from '@mui/material/Box'
import { DataGrid, GridToolbarFilterButton } from '@mui/x-data-grid'
import moment from 'moment'
import PropTypes from 'prop-types'
import * as React from 'react'
import { useEffect } from 'react'
import { useQuery } from 'react-query'
import { getAllProductsSpecz } from '../services/product'

const DataTableWrapper = ({ onSelectionChange, clearSelection }) => {
  const [selectedRows, setSelectedRows] = React.useState([])

  const { data, isLoading } = useQuery(
    ['productData'],
    () => getAllProductsSpecz(),
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

  useEffect(() => {
    if (clearSelection) {
      setSelectedRows([])
    }
  }, [clearSelection])

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
        checkboxSelection
        getRowId={row => row.id || row.unique_key}
        rows={data?.results || []}
        columns={columns}
        loading={isLoading}
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
  )
}

DataTableWrapper.propTypes = {
  onSelectionChange: PropTypes.func,
  clearSelection: PropTypes.bool
}

DataTableWrapper.defaultProps = {
  onSelectionChange: () => {},
  clearSelection: false
}

export default DataTableWrapper
