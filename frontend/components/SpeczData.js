import * as React from 'react'
import { getProducts } from '../services/product'
import { DataGrid } from '@mui/x-data-grid'
import moment from 'moment'
import { Box } from '@mui/material'
import PropTypes from 'prop-types'

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

async function fetchData(filters, query) {
  try {
    const response = await getProducts({
      filters,
      page: 0,
      page_size: 25,
      sort: [{ field: 'created_at', sort: 'desc' }],
      search: query
    })

    return response.results
  } catch (error) {
    console.error(error)
    throw error
  }
}

function DataTable({ rows }) {
  return (
    <Box sx={{ height: 300, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSizeOptions={[5, 10]}
        checkboxSelection
      />
    </Box>
  )
}

DataTable.propTypes = {
  rows: PropTypes.arrayOf(PropTypes.object).isRequired
}

function DataTableWrapper({ filters, query }) {
  const [rows, setRows] = React.useState([])

  React.useEffect(() => {
    const fetchAndSetData = async () => {
      try {
        const data = await fetchData(filters, query)
        setRows(data)
      } catch (error) {
        console.error(error)
      }
    }

    fetchAndSetData()
  }, [filters, query])

  return <DataTable rows={rows} />
}

DataTableWrapper.propTypes = {
  filters: PropTypes.object,
  query: PropTypes.string
}

DataTableWrapper.defaultProps = {
  filters: {},
  query: ''
}

export default DataTableWrapper
