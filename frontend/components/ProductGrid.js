/* eslint-disable multiline-ternary */
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
import { Button } from '@mui/material'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import Snackbar from '@mui/material/Snackbar'
import Alert from '@mui/material/Alert'
import Link from '@mui/material/Link'
import ShareIcon from '@mui/icons-material/Share'
import TextField from '@mui/material/TextField'
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
  const [rowCount, setRowCount] = React.useState(0)
  const [page, setPage] = React.useState(0)
  const [pageSize, setPageSize] = React.useState(25)
  const [sortModel, setSortModel] = React.useState([
    { field: 'created_at', sort: 'desc' }
  ])
  const [loading, setLoading] = React.useState(false)
  const [delRecordId, setDelRecordId] = React.useState(null)
  const [shareDialogOpen, setShareDialogOpen] = React.useState(false)
  const [selectedFileUrl, setSelectedFileUrl] = React.useState('')
  const [copySnackbarOpen, setCopySnackbarOpen] = React.useState(false)

  const handleSortModelChange = newModel => {
    setSortModel(newModel)
  }

  const handleCopyUrl = () => {
    navigator.clipboard
      .writeText(selectedFileUrl)
      .then(() => {
        setCopySnackbarOpen(true)
      })
      .catch(error => {
        console.error(error)
      })
  }

  const handleCloseShareDialog = () => {
    setShareDialogOpen(false)
  }

  const handleCloseCopySnackbar = () => {
    setCopySnackbarOpen(false)
  }

  const loadProducts = React.useCallback(async () => {
    setLoading(true)
    try {
      const response = await getProducts({
        filters: props.filters,
        page,
        page_size: pageSize,
        sort: sortModel,
        search: props.query
      })

      setRows(response.results)
      setRowCount(response.count)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, sortModel, props.query, props.filters])

  React.useEffect(() => {
    loadProducts()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadProducts])

  const getProductUrl = React.useCallback(internalName => {
    return `/product/${encodeURIComponent(internalName)}`
  }, [])

  const columns = React.useMemo(() => {
    const getDownloadUrl = row => {
      const { id, /* eslint-disable camelcase */ display_name } = row

      const formattedDisplayName = display_name
        .replace(/[-\s]/g, '')
        .toLowerCase()

      const productUrl = getProductUrl(`${id}_${formattedDisplayName}`)
      const downloadUrl = `${window.location.origin}${productUrl}`
      return downloadUrl
    }

    const handleDownload = row => {
      router.push(getProductUrl(row.internal_name))
    }

    const handleDelete = row => {
      setDelRecordId(row.id)
    }

    const handleShare = row => {
      const downloadUrl = getDownloadUrl(row)
      setSelectedFileUrl(downloadUrl)
      setShareDialogOpen(true)
    }

    return [
      // Hide Id Column ISSUE #123
      // { field: 'id', headerName: 'ID', width: 90, sortable: true },
      {
        field: 'display_name',
        headerName: 'Name',
        sortable: true,
        flex: 1,
        renderCell: params => (
          <Link component="button" onClick={() => handleDownload(params.row)}>
            {params.value}
          </Link>
        )
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
          if (!params.value) {
            return ''
          }
          return moment(params.value).format('YYYY-MM-DD')
        }
      },
      {
        field: 'actions_download',
        headerName: 'Download',
        width: 120,
        sortable: false,
        renderCell: params => (
          <GridActionsCellItem
            icon={<DownloadIcon />}
            onClick={() => handleDownload(params.row)}
          />
        )
      },
      {
        field: 'share',
        headerName: 'Share',
        width: 120,
        sortable: false,
        renderCell: params => (
          <GridActionsCellItem
            icon={<ShareIcon />}
            onClick={() => handleShare(params.row)}
          />
        )
      },
      {
        field: 'delete',
        headerName: 'Delete',
        width: 120,
        sortable: false,
        renderCell: params => (
          <GridActionsCellItem
            icon={<DeleteIcon />}
            onClick={() => handleDelete(params.row)}
          />
        )
      }
    ]
  }, [getProductUrl, router])

  return (
    <React.Fragment>
      <DataGrid
        rows={rows}
        columns={columns}
        rowCount={rowCount}
        pagination
        paginationMode="server"
        pageSize={pageSize}
        onPageChange={newPage => setPage(newPage)}
        onPageSizeChange={newPageSize => setPageSize(newPageSize)}
        sortModel={sortModel}
        onSortModelChange={handleSortModelChange}
        loading={loading}
        autoHeight
        hideFooterSelectedRowCount
      />

      <Dialog
        open={shareDialogOpen}
        onClose={handleCloseShareDialog}
        PaperProps={{
          style: { width: '500px', minHeight: '150px' }
        }}
      >
        <DialogContent>
          <DialogContentText>Copy the download URL:</DialogContentText>
          <TextField
            fullWidth
            variant="outlined"
            value={selectedFileUrl}
            InputProps={{
              endAdornment: (
                <Button variant="contained" onClick={handleCopyUrl}>
                  Copy
                </Button>
              )
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseShareDialog}>Close</Button>
        </DialogActions>
      </Dialog>

      {delRecordId && (
        <ProductRemove
          open={Boolean(delRecordId)}
          onClose={() => setDelRecordId(null)}
          recordId={delRecordId}
          onRemoveSuccess={loadProducts}
        />
      )}

      <Snackbar
        open={copySnackbarOpen}
        autoHideDuration={3000}
        onClose={handleCloseCopySnackbar}
      >
        <Alert
          onClose={handleCloseCopySnackbar}
          severity="success"
          sx={{ width: '100%' }}
        >
          Link copied successfully!
        </Alert>
      </Snackbar>
    </React.Fragment>
  )
}

ProductGrid.propTypes = {
  filters: PropTypes.object,
  query: PropTypes.string
}

ProductGrid.defaultProps = {
  filters: {},
  query: ''
}
