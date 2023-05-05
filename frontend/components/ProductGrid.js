/* eslint-disable multiline-ternary */
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import Link from '@mui/material/Link'
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid'
import moment from 'moment'
import { useRouter } from 'next/router'
import PropTypes from 'prop-types'
import * as React from 'react'
import { getProducts } from '../services/product'

import ProductRemove from '../components/ProductRemove'

export default function ProductGrid(props) {
  const router = useRouter()
  const [rows, setRows] = React.useState([])
  const [rowCount, setRowCount] = React.useState(undefined)

  const [page, setPage] = React.useState(0)
  const [pageSize, setPageSize] = React.useState(25)
  const [sortModel, setSortModel] = React.useState([
    { field: 'created_at', sort: 'desc' }
  ])
  const [loading, setLoading] = React.useState(false)
  const [delRecordId, setDelRecordId] = React.useState(null)
  const [error, setError] = React.useState(null)

  const handleSortModelChange = newModel => {
    setSortModel(newModel)
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const loadProducts = React.useCallback(() => {
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
  })

  React.useEffect(() => {
    loadProducts()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, sortModel, props.query, props.filters])

  // Some api client return undefine while loading
  // Following lines are here to prevent `rowCountState` from being undefined during the loading
  const [rowCountState, setRowCountState] = React.useState(rowCount || 0)
  React.useEffect(() => {
    setRowCountState(prevRowCountState =>
      rowCount !== undefined ? rowCount : prevRowCountState
    )
  }, [rowCount, setRowCountState])

  const columns = React.useMemo(() => {
    function handleDownload(row) {
      // Redirecionar para a pagina de detalhe do produto
      router.push(`/product/${encodeURIComponent(row.internal_name)}`)
    }

    function handleDelete(row) {
      setDelRecordId(row.id)
    }

    return [
      // Hide Id Column ISSUE #123
      // { field: 'id', headerName: 'ID', width: 90, sortable: true },
      {
        field: 'display_name',
        headerName: 'Name',
        sortable: true,
        flex: 1,
        renderCell: params => {
          return (
            <Link component="button" onClick={e => handleDownload(params.row)}>
              {params.value}
            </Link>
          )
        }
      },
      {
        field: 'release_name',
        headerName: 'Release',
        width: 200,
        sortable: false
      },
      {
        field: 'product_type_name',
        headerName: 'Product Type',
        flex: 1,
        sortable: false
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
        width: 200,
        sortable: true,
        valueFormatter: params => {
          if (params.value == null) {
            return ''
          }
          const valueFormatted = moment(params.value).format('L LTS')
          return `${valueFormatted}`
        }
      },
      {
        field: 'actions_download',
        type: 'actions',
        headerName: 'Download',
        width: 100,
        sortable: false,
        getActions: data => [
          <GridActionsCellItem
            key={'product_download_' + data.id}
            icon={<DownloadIcon />}
            label="Download"
            onClick={e => handleDownload(data.row)}
          />
        ]
      },
      {
        field: 'actions_delete',
        type: 'actions',
        headerName: 'Delete',
        width: 100,
        sortable: false,
        getActions: data => [
          <GridActionsCellItem
            key={'product_delete_' + data.id}
            icon={<DeleteIcon />}
            label="Delete Product"
            disabled={data.row.is_owner === false}
            onClick={e => handleDelete(data.row)}
          />
        ]
      }
    ]
  }, [router])

  const onDeleteOk = () => {
    loadProducts()
    setDelRecordId(null)
  }
  const onDeleteCancel = () => {
    setDelRecordId(null)
  }

  const handleError = () => {
    const handleClose = () => {
      setError(null)
    }
    return (
      <Dialog
        open={true}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            {error}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} autoFocus>
            Ok
          </Button>
        </DialogActions>
      </Dialog>
    )
  }

  const handleDeleteProduct = () => {
    return (
      <ProductRemove
        productId={delRecordId}
        open={delRecordId !== null}
        onOk={onDeleteOk}
        onCancel={onDeleteCancel}
        onError={e => setError(e)}
      ></ProductRemove>
    )
  }

  return (
    <>
      {error !== null ? handleError() : null}
      {delRecordId !== null ? handleDeleteProduct() : null}
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
    </>
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
