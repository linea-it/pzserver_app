import CloseIcon from '@mui/icons-material/Close'
import EditIcon from '@mui/icons-material/Edit'
import {
  Alert,
  Box,
  Button,
  FormControl,
  Stack,
  TextField,
  Typography
} from '@mui/material'
import IconButton from '@mui/material/IconButton'
import InputAdornment from '@mui/material/InputAdornment'
import MenuItem from '@mui/material/MenuItem'
import debounce from 'lodash/debounce'
import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { contentAssociation, getProductContents } from '../../services/product'
import Loading from '../Loading'


export default function InputUcd({ isLoading }) {

  return (
    <Backdrop
      sx={{ color: '#fff', zIndex: theme => theme.zIndex.drawer + 1 }}
      open={isLoading}
    >
      <CircularProgress color="inherit" />
    </Backdrop>
  )
}
InputUcd.propTypes = {
  isLoading: PropTypes.bool.isRequired
}

export default function InputAlias({ }) {

  return (
    <Backdrop
      sx={{ color: '#fff', zIndex: theme => theme.zIndex.drawer + 1 }}
      open={isLoading}
    >
      <CircularProgress color="inherit" />
    </Backdrop>
  )
}
InputAlias.propTypes = {
  isLoading: PropTypes.bool.isRequired
}


export default function NewProductStep3({ productId, onNext, onPrev }) {
  const ucds = [
    {
      name: 'ID',
      value: 'meta.id;meta.main'
    },
    {
      name: 'RA',
      value: 'pos.eq.ra;meta.main'
    },
    {
      name: 'Dec',
      value: 'pos.eq.dec;meta.main'
    },
    {
      name: 'z',
      value: 'src.redshift'
    },
    {
      name: 'z_err',
      value: 'stat.error;src.redshift'
    },
    {
      name: 'z_flag',
      value: 'stat.rank'
    },
    {
      name: 'survey',
      value: 'meta.curation'
    }
  ]

  const [productColumns, setProductColumns] = React.useState([])
  const [usedUcds, setUsedUcds] = React.useState([])
  const [isLoading, setLoading] = useState(false)
  const [formError, setFormError] = React.useState('')
  const [editableFields, setEditableFields] = useState({})
  // const editFieldRefs = useRef({})

  const loadContents = React.useCallback(async () => {
    setLoading(true)
    try {
      const response = await getProductContents(productId)
      setProductColumns(response.results)

      // const aliases = {}
      // response.results.forEach(row => {
      //   if (row.alias) {
      //     aliases[row.column_name] = row.alias
      //   }
      // })
      // setEditableFields(aliases)

      setLoading(false)
    } catch (error) {
      setLoading(false)
      if (error.response && error.response.status === 500) {
        catchFormError(error.response.data)
      }
    }
  }, [productId])

  useEffect(() => {
    loadContents()
  }, [loadContents])

  useEffect(() => {
    const useducds = []
    productColumns.forEach(row => {
      if (row.ucd !== null) {
        useducds.push(row.ucd)
      }
    })
    setUsedUcds(useducds)
  }, [productColumns])

  const handleSubmit = () => {
    onNext(productId)
  }
  const handlePrev = () => {
    onPrev(productId)
  }

  const onSelectUcd = (pc, value) => {
    const ucd = ucds.find(o => o.value === value);
    onChangeProductContent(pc, ucd.value, ucd.name)
  }

  // Using lodash debounce to Delay search by 600ms
  // Exemplo: https://www.upbeatcode.com/react/how-to-use-lodash-in-react/
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const delayedEdit = useCallback(
    debounce((pc, alias) => onChangeProductContent(pc, null, alias), 600),
    []
  )

  const onChangeAlias = (pc, alias) => {
    // console.log('onChangeAlias: ', pc.column_name, value)
    delayedEdit(pc, alias)
  }

  const onChangeProductContent = (pc, ucd, alias) => {
    if (pc.ucd === ucd && pc.alias === alias) {
      return
    }
    // setLoading(true)
    contentAssociation(pc.id, ucd, alias)
      .then(() => {
        // setLoading(false)
        loadContents(productId)
      })
      .catch(res => {
        setLoading(false)
        if (res.response.status === 500) {
          catchFormError(res.response.data)
        }
      })
  }

  const handleEdit = (pc) => {
    setEditableFields(prevState => ({
      ...prevState,
      [pc.column_name]: pc.value
    }))
  }

  const handleCancelEdit = pc => {
    console.log("handleCancelEdit: ", pc.column_name)
    // const updatedEditableFields = { ...editableFields }
    // delete updatedEditableFields[pc.column_name]
    // setEditableFields(updatedEditableFields)
    onChangeProductContent(pc, null, null)
  }

  const createSelect = pc => {
    // Check Available Ucds and Current UCD when pc.ucd is not null
    const avoptions = []
    let currentUcd = null
    ucds.forEach(ucd => {
      if (usedUcds.indexOf(ucd.value) === -1 || ucd.value === pc.ucd) {
        avoptions.push(ucd)
      }
      if (ucd.value === pc.ucd) {
        currentUcd = ucd
      }
    })

    const isOptionSelected = pc.ucd !== null

    return (
      <Box sx={{ display: "flex", alignItems: "center" }}>
        {isOptionSelected ? (
          <TextField
            value={currentUcd.name}
            readOnly
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => onChangeProductContent(pc, null, null)}>
                    <CloseIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        ) : (
          <>
            {pc.column_name in editableFields ? (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TextField
                  value={editableFields[pc.column_name]}
                  onChange={e => onChangeAlias(pc, e.target.value)}
                  // onBlur={(e) => {
                  //   console.log("onBlur: ", `${pc.column_name}:${e.target.value}`)
                  //   // console.log(`${pc.column_name}: ${editableFields[pc.column_name]}`)
                  //   // onChangeAlias(pc, editableFields[pc.column_name])
                  // }}
                  // onKeyPress={event => {
                  //   if (event.key === 'Enter') {
                  //     console.log("onKeyPress Enter: ", `${pc.column_name}: ${editableFields[pc.column_name]}`)
                  //     editFieldRefs.current[pc.column_name].blur()
                  //   }
                  // }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => handleCancelEdit(pc)}>
                          <CloseIcon />
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                  // inputRef={ref => {
                  //   editFieldRefs.current[pc.column_name] = ref
                  // }}
                  autoFocus
                />
              </Box>
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TextField
                  select
                  value={pc.ucd || ''}
                  onChange={e => onSelectUcd(pc, e.target.value)}
                // onChange={e => onChangeProductContent(pc, e.target.value)}
                >
                  {avoptions.map(ucd => (
                    <MenuItem
                      key={`${pc.column_name}_${ucd.name}`}
                      value={ucd.value}
                    >
                      {ucd.name}
                    </MenuItem>
                  ))}
                </TextField>
                <IconButton
                  onClick={() => handleEdit(pc)}
                >
                  <EditIcon />
                </IconButton>
              </Box>
            )}
          </>
        )}
      </Box>
    )
  }

  const createFields = pc => {
    return (
      <Stack
        direction="row"
        spacing={2}
        key={`fields_${pc.column_name}`}
        mb={2}
      >
        <FormControl>
          <TextField value={pc.column_name} />
        </FormControl>
        <FormControl>{createSelect(pc)}</FormControl>
      </Stack>
    )
  }

  const catchFormError = data => {
    let msg =
      'There was a failure, please try again later, if the problem persists, please contact support.'
    if (data.error) {
      msg = data.error
    }
    setFormError(msg)
  }

  const handleFormError = () => {
    return (
      <Alert variant="outlined" severity="error" sx={{ mt: 2 }}>
        {formError}
      </Alert>
    )
  }

  return (
    <React.Fragment>
      {isLoading && <Loading isLoading={isLoading} />}
      <Typography paragraph variant="body">
        Please associate the column names of your file with those expected by
        the tool.
      </Typography>
      <Typography paragraph variant="body">
        It is okay to leave columns unassociated.
      </Typography>
      <Typography paragraph variant="body">
        Skip this step if the data is not tabular.
      </Typography>

      <Box
        component="form"
        sx={{
          '& .MuiTextField-root': { width: '25ch' }
        }}
        autoComplete="off"
      >
        {productColumns.map(pc => {
          return createFields(pc)
        })}
      </Box>
      {formError !== '' && handleFormError()}
      <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
        <Button
          variant="contained"
          color="secondary"
          onClick={handlePrev}
          sx={{ mr: 1 }}
        >
          Prev
        </Button>
        <Box sx={{ flex: '1 1 auto' }} />
        <Button variant="contained" color="primary" onClick={handleSubmit}>
          Next
        </Button>
      </Box>
    </React.Fragment>
  )
}

NewProductStep3.propTypes = {
  productId: PropTypes.number,
  onNext: PropTypes.func.isRequired,
  onPrev: PropTypes.func.isRequired
}
