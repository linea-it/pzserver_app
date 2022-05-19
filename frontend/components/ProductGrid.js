import * as React from 'react'
import PropTypes from 'prop-types'
// import { Paper, Box } from '@mui/material'
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid'
// import Grid from '@mui/material/Grid'
// import Divider from '@mui/material/Divider'
// import Typography from '@mui/material/Typography'
import DownloadIcon from '@mui/icons-material/Download'
import prettyBytes from 'pretty-bytes'
import moment from 'moment'

// import ProductTypeSelect from '../components/ProductTypeSelect'
// import ReleaseSelect from '../components/ReleaseSelect'
// import SearchField from '../components/SearchField'
import { getProducts } from '../services/product'

export default function ProductGrid(props) {
  const [rows, setRows] = React.useState([])
  const [rowCount, setRowCount] = React.useState(undefined)

  const [page, setPage] = React.useState(0)
  const [pageSize, setPageSize] = React.useState(25)
  const [sortModel, setSortModel] = React.useState([
    { field: 'created_at', sort: 'desc' }
  ])
  const [loading, setLoading] = React.useState(false)

  const handleSortModelChange = newModel => {
    setSortModel(newModel)
  }

  const handleDownload = React.useCallback(
    row => () => {
      console.log('Download Product with ID: %o', row.id)
      // Pode redirecionar direto para a url do arquivo row.main_file
    },
    []
  )

  // https://www.django-rest-framework.org/api-guide/pagination/#pagenumberpagination
  React.useEffect(() => {
    // eslint-disable-next-line prettier/prettier
    let active = true;

    // eslint-disable-next-line no-unexpected-multiline
    // eslint-disable-next-line prettier/prettier
    (async () => {
      setLoading(true)
      const response = await getProducts({
        filters: props.filters,
        page: page,
        page_size: pageSize,
        sort: sortModel,
        search: props.query
      })

      if (!active) {
        return
      }
      setRows(response.results)
      setRowCount(response.count)
      setLoading(false)
    })()

    return () => {
      active = false
    }
  }, [page, pageSize, sortModel, props.query, props.filters])

  // Some api client return undefine while loading
  // Following lines are here to prevent `rowCountState` from being undefined during the loading
  const [rowCountState, setRowCountState] = React.useState(rowCount || 0)
  React.useEffect(() => {
    setRowCountState(prevRowCountState =>
      rowCount !== undefined ? rowCount : prevRowCountState
    )
  }, [rowCount, setRowCountState])

  const columns = React.useMemo(
    () => [
      { field: 'id', headerName: 'ID', width: 90, sortable: true },
      // TODO: Utilizar o Render Cell para gerar um LINK no nome do produto
      { field: 'display_name', headerName: 'Name', sortable: true, flex: 1 },
      {
        field: 'release_name',
        headerName: 'Release',
        width: 120,
        sortable: false
      },
      {
        field: 'product_type_name',
        headerName: 'Product Type',
        width: 120,
        sortable: false
      },
      {
        field: 'uploaded_by',
        headerName: 'Uploaded By',
        width: 160,
        sortable: false
      },
      {
        field: 'created_at',
        headerName: 'Created at',
        width: 180,
        sortable: true,
        valueFormatter: params => {
          if (params.value == null) {
            return ''
          }
          const valueFormatted = moment(params.value).format('L LTS')
          return `${valueFormatted}`
        }
      },
      { field: 'file_name', headerName: 'Filename', sortable: true, flex: 1 },
      {
        field: 'file_size',
        headerName: 'Size',
        width: 90,
        sortable: true,
        valueFormatter: params => {
          if (params.value == null) {
            return ''
          }

          const valueFormatted = prettyBytes(Number(params.value))
          return `${valueFormatted}`
        }
      },
      {
        field: 'actions',
        type: 'actions',
        headerName: 'Download',
        width: 100,
        sortable: false,
        getActions: row => [
          <GridActionsCellItem
            key={'product_download_' + row.id}
            icon={<DownloadIcon />}
            label="Download"
            onClick={handleDownload(row)}
          />
        ]
      }
    ],
    [handleDownload]
  )

  return (
    <DataGrid
      getRowId={row => row.id}
      rows={rows}
      columns={columns}
      disableSelectionOnClick
      autoHeight
      sortingMode="server"
      sortModel={sortModel}
      onSortModelChange={handleSortModelChange}
      paginationMode="server"
      rowCount={rowCountState}
      pagination
      page={page}
      onPageChange={page => setPage(page)}
      pageSize={pageSize}
      onPageSizeChange={newPageSize => setPageSize(newPageSize)}
      rowsPerPageOptions={[25, 50, 100]}
      loading={loading}
    />
  )
}

ProductGrid.propTypes = {
  query: PropTypes.string,
  filters: PropTypes.shape({
    release: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    product_type: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    official_product: PropTypes.bool
  })
}
