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

function DataTable({ rows }) {
  return (
    <Box style={{ height: 300, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        // getRowId={row => row.id}
        pageSizeOptions={[5, 10]}
      />
    </Box>
  )
}

DataTable.propTypes = {
  rows: PropTypes.arrayOf(PropTypes.object).isRequired
}

const rows = [
  {
    id: 1,
    display_name: 'Jandson 1',
    uploaded_by: 'User1',
    created_at: '2023-01-01'
  },
  {
    id: 2,
    display_name: 'Jandson 2',
    uploaded_by: 'User2',
    created_at: '2023-02-15'
  },
  {
    id: 3,
    display_name: 'Jandson 3',
    uploaded_by: 'User3',
    created_at: '2023-03-22'
  },
  {
    id: 4,
    display_name: 'Jandson V',
    uploaded_by: 'User1',
    created_at: '2023-04-10'
  },
  {
    id: 5,
    display_name: 'Jandson Try',
    uploaded_by: 'User2',
    created_at: '2023-05-05'
  }
]

export default function App() {
  return <DataTable rows={rows} />
}
