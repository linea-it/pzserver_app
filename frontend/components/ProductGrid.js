/* eslint-disable multiline-ternary */
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';
import EditIcon from '@mui/icons-material/Edit';
import ShareIcon from '@mui/icons-material/Share';
import Alert from '@mui/material/Alert';
import Link from '@mui/material/Link';
import Snackbar from '@mui/material/Snackbar';
import Tooltip from '@mui/material/Tooltip';
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import moment from 'moment';
import { useRouter } from 'next/router';
import PropTypes from 'prop-types';
import * as React from 'react';
import { getProducts } from '../services/product';

import ProductRemove from '../components/ProductRemove';
import ProductShare from './ProductShare';

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
  const [selectedFileUrl, setSelectedFileUrl] = React.useState('')
  const [copySnackbarOpen, setCopySnackbarOpen] = React.useState(false)
  const [snackbarOpen, setSnackbarOpen] = React.useState(false)
  const productShareRef = React.useRef(null)

  const handleSortModelChange = newModel => {
    setSortModel(newModel)
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
    const handleDownload = row => {
      router.push(getProductUrl(row.internal_name))
    }

    const handleDelete = row => {
      setDelRecordId(row.id)
    }

    const handleShare = row => {
      const productUrl = getProductUrl(row.internal_name)
      const shareUrl = `${window.location.origin}${productUrl}`
      setSelectedFileUrl(shareUrl)
      setSnackbarOpen(true)
    }

    const handleEdit = row => {
      router.push(`/product/edit/${row.internal_name}`)
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
          <Tooltip
            title={
              !params.row.can_delete
                ? 'You cannot delete this data product because it belongs to another user.'
                : 'Delete this data product.'
            }
          >
            <div>
              <GridActionsCellItem
                icon={<DeleteIcon />}
                onClick={() => handleDelete(params.row)}
                disabled={!params.row.can_delete}
              />
            </div>
          </Tooltip>
        )
      },
      {
        field: 'can_update',
        headerName: 'Edit',
        width: 120,
        sortable: false,
        renderCell: params => (
          <Tooltip
            title={
              !params.row.can_update
                ? 'You cannot update this data product because it belongs to another user.'
                : 'Edit this data product.'
            }
          >
            <div>
              <GridActionsCellItem
                icon={<EditIcon />}
                onClick={() => handleEdit(params.row)}
                disabled={!params.row.can_update}
              />
            </div>
          </Tooltip>
        )
      }
    ]
  }, [getProductUrl, router])

  function handleError(errorMessage) {
    console.error(errorMessage)
  }

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

      <ProductShare
        isOpen={snackbarOpen}
        handleShareDialogOpen={() => setSnackbarOpen(!snackbarOpen)}
        url={selectedFileUrl}
        setParentSnackbarOpen={setCopySnackbarOpen}
        productShareRef={productShareRef}
      />
      {delRecordId && (
        <ProductRemove
          open={Boolean(delRecordId)}
          onClose={() => setDelRecordId(null)}
          recordId={delRecordId}
          onRemoveSuccess={loadProducts}
          onError={handleError}
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
