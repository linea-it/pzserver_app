/* eslint-disable multiline-ternary */
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
import EditIcon from '@mui/icons-material/Edit'
import ShareIcon from '@mui/icons-material/Share'
import { Box } from '@mui/material'
import Alert from '@mui/material/Alert'
import Link from '@mui/material/Link'
import Snackbar from '@mui/material/Snackbar'
import Tooltip from '@mui/material/Tooltip'
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid'
import moment from 'moment'
import { useRouter } from 'next/router'
import PropTypes from 'prop-types'
import * as React from 'react'
import { getProcessLogs } from '../services/process'
import { getProducts } from '../services/product'

import ProductRemove from '../components/ProductRemove'
import ProcessLogs from './ProcessLogs'
import ProductShare from './ProductShare'

export default function ProductGrid(props) {
  const router = useRouter()
  const [rows, setRows] = React.useState([])
  const [rowCount, setRowCount] = React.useState(0)

  // Load pagination state from sessionStorage
  const [page, setPage] = React.useState(() => {
    if (
      typeof window !== 'undefined' &&
      props.storageKey &&
      props.applyPagination
    ) {
      const saved = sessionStorage.getItem(`${props.storageKey}_page`)
      return saved ? parseInt(saved, 10) : 0
    }
    return 0
  })

  const [pageSize, setPageSize] = React.useState(() => {
    if (
      typeof window !== 'undefined' &&
      props.storageKey &&
      props.applyPagination
    ) {
      const saved = sessionStorage.getItem(`${props.storageKey}_pageSize`)
      return saved ? parseInt(saved, 10) : 25
    }
    return 25
  })

  const [sortModel, setSortModel] = React.useState(() => {
    if (
      typeof window !== 'undefined' &&
      props.storageKey &&
      props.applyPagination
    ) {
      const saved = sessionStorage.getItem(`${props.storageKey}_sortModel`)
      if (saved) {
        try {
          return JSON.parse(saved)
        } catch (e) {
          console.error('Error parsing saved sortModel:', e)
        }
      }
    }
    return [{ field: 'created_at', sort: 'desc' }]
  })
  const [loading, setLoading] = React.useState(false)
  const [delRecord, setDelRecord] = React.useState(null)
  const [selectedFileUrl, setSelectedFileUrl] = React.useState('')
  const [copySnackbarOpen, setCopySnackbarOpen] = React.useState(false)
  const [snackbarOpen, setSnackbarOpen] = React.useState(false)
  const productShareRef = React.useRef(null)
  const [productName, setProductName] = React.useState('')
  const [pipelineOut, setPipelineOut] = React.useState('')
  const [schedulerOut, setSchedulerOut] = React.useState('')
  const [isOpen, setOpen] = React.useState(false)

  // Track if this is the first render to avoid resetting page on mount
  const isFirstRender = React.useRef(true)

  // Save pagination state to sessionStorage
  React.useEffect(() => {
    if (typeof window !== 'undefined' && props.storageKey) {
      sessionStorage.setItem(`${props.storageKey}_page`, page.toString())
    }
  }, [page, props.storageKey])

  // Reset pagination when filters or search change (but not on mount)
  React.useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false
      return
    }

    setPage(0)
    if (typeof window !== 'undefined' && props.storageKey) {
      sessionStorage.setItem(`${props.storageKey}_page`, '0')
    }
  }, [props.filters, props.query, props.storageKey])

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

    const handleProcessLogs = async row => {
      console.log(row)
      try {
        setProductName(row.display_name)
        const data = await getProcessLogs(row.process_id)
        console.log(data)

        setPipelineOut(data.pipeline.content)
        setSchedulerOut(data.slurm.content)
        setOpen(true)
      } catch (error) {
        console.error(error)
      }
    }

    const handleDelete = row => {
      setDelRecord(row)
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
        minWidth: 130,
        renderCell: params => (
          <>
            {params.row.product_status !== 'Published' ? (
              params.value
            ) : (
              <Tooltip
                title={params.row.description || 'No description available'}
              >
                <Link href={getProductUrl(params.row.internal_name)}>
                  {params.value}
                </Link>
              </Tooltip>
            )}
          </>
        )
      },
      {
        field: 'release_name',
        headerName: 'Release',
        flex: 1,
        minWidth: 130,
        sortable: false
      },
      {
        field: 'product_type_name',
        headerName: 'Product Type',
        flex: 1,
        minWidth: 130,
        sortable: false
      },
      {
        field: 'uploaded_by',
        headerName: 'Owner',
        flex: 1,
        maxWidth: 130,
        sortable: false
      },
      {
        field: 'product_status',
        headerName: 'Status',
        flex: 1,
        maxWidth: 130,
        sortable: false
      },
      {
        field: 'process_status',
        headerName: 'Process Status',
        flex: 1,
        maxWidth: 130,
        sortable: false,
        renderCell: params => (
          <>
            {['Queued', 'Pending'].includes(params.row.process_status) ? (
              params.value
            ) : (
              <Link
                component="button"
                onClick={() => handleProcessLogs(params.row)}
              >
                {params.value}
              </Link>
            )}
          </>
        )
      },
      {
        field: 'created_at',
        headerName: 'Created at',
        width: 130,
        sortable: true,
        valueFormatter: params => {
          if (!params.value) {
            return ''
          }
          return moment(params.value).format('YYYY-MM-DD')
        }
      },
      {
        field: 'actions',
        headerName: '',
        type: 'actions',
        width: 150,
        renderCell: params => (
          <>
            <Tooltip title={'Download this product'}>
              <Box>
                <GridActionsCellItem
                  icon={<DownloadIcon />}
                  label="Download"
                  disabled={params.row.product_status !== 'Published'}
                  onClick={() => handleDownload(params.row)}
                />
              </Box>
            </Tooltip>
            <Tooltip title={'Share product'}>
              <Box>
                <GridActionsCellItem
                  icon={<ShareIcon />}
                  label="Share"
                  disabled={params.row.product_status !== 'Published'}
                  onClick={() => handleShare(params.row)}
                />
              </Box>
            </Tooltip>
            <Tooltip
              title={
                !params.row.can_delete
                  ? 'You cannot delete this data product because it belongs to another user.'
                  : 'Delete this data product.'
              }
            >
              <Box>
                <GridActionsCellItem
                  icon={<DeleteIcon />}
                  label="Delete"
                  onClick={() => handleDelete(params.row)}
                  disabled={
                    !(
                      params.row.product_status === 'Published' &&
                      params.row.can_delete === true
                    )
                  }
                />
              </Box>
            </Tooltip>
            <Tooltip
              title={
                !params.row.can_update
                  ? 'You cannot update this data product because it belongs to another user.'
                  : 'Edit this data product.'
              }
            >
              <Box>
                <GridActionsCellItem
                  icon={<EditIcon />}
                  label="Edit"
                  onClick={() => handleEdit(params.row)}
                  disabled={
                    !(
                      params.row.product_status === 'Published' &&
                      params.row.can_update === true
                    )
                  }
                />
              </Box>
            </Tooltip>
          </>
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
        page={page}
        pageSize={pageSize}
        onPageChange={newPage => setPage(newPage)}
        onPageSizeChange={newPageSize => setPageSize(newPageSize)}
        sortModel={sortModel}
        onSortModelChange={handleSortModelChange}
        loading={loading}
        autoHeight
        hideFooterSelectedRowCount
        getRowClassName={params =>
          params.id === delRecord?.id ? 'highlight-row' : ''
        }
        sx={{
          '& .highlight-row': {
            backgroundColor: '#ffe6e6 !important'
          }
        }}
      />

      <ProductShare
        isOpen={snackbarOpen}
        handleShareDialogOpen={() => setSnackbarOpen(!snackbarOpen)}
        url={selectedFileUrl}
        setParentSnackbarOpen={setCopySnackbarOpen}
        productShareRef={productShareRef}
      />
      {delRecord && (
        <ProductRemove
          open={Boolean(delRecord)}
          onClose={() => setDelRecord(null)}
          recordId={delRecord.id}
          productName={delRecord.display_name}
          onRemoveSuccess={loadProducts}
          onError={handleError}
        />
      )}

      <ProcessLogs
        isOpen={isOpen}
        handleProcessLogsDialogOpen={() => setOpen(!isOpen)}
        productName={productName}
        pipelineOut={pipelineOut}
        schedulerOut={schedulerOut}
      />

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
  query: PropTypes.string,
  storageKey: PropTypes.string,
  applyPagination: PropTypes.bool
}

ProductGrid.defaultProps = {
  filters: {},
  query: '',
  storageKey: null,
  applyPagination: false
}
