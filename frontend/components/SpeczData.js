import { DataGrid } from '@mui/x-data-grid'
import moment from 'moment'
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
    <div style={{ height: 300, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        // getRowId={row => row.id}
        pageSizeOptions={[5, 10]}
        checkboxSelection
      />
    </div>
  )
}

DataTable.propTypes = {
  rows: PropTypes.arrayOf(PropTypes.object).isRequired
}

export default DataTable
