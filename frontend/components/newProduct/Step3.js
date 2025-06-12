import CloseIcon from '@mui/icons-material/Close'
import EditIcon from '@mui/icons-material/Edit'
import {
  Alert,
  Box,
  Button,
  FormControl,
  MenuItem,
  Stack,
  TextField,
  Typography
} from '@mui/material'
import IconButton from '@mui/material/IconButton'
import InputAdornment from '@mui/material/InputAdornment'
import debounce from 'lodash/debounce'
import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import {
  contentAssociation,
  getProduct,
  getProductContents
} from '../../services/product'
import Loading from '../Loading'

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

const ucdRaAndDec = [
  'pos.eq.ra;meta.main',
  'pos.eq.dec;meta.main'
]

const mandatoryUcds = ['src.redshift']
mandatoryUcds.push.apply(mandatoryUcds, ucdRaAndDec)

export function InputReadOnly({ name, value, onClear }) {
  return (
    <FormControl>
      <TextField
        name={name}
        value={value}
        readOnly
        InputProps={
          onClear !== undefined
            ? {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={onClear}>
                      <CloseIcon />
                    </IconButton>
                  </InputAdornment>
                )
              }
            : null
        }
      />
    </FormControl>
  )
}
InputReadOnly.propTypes = {
  value: PropTypes.string.isRequired,
  name: PropTypes.string,
  onClear: PropTypes.func
}

export function InputUcd({ pc, options, onChange, onChangeInputType }) {
  const [value, setValue] = useState('')

  const handleChange = e => {
    setValue(e.target.value)
    onChange(pc, e.target.value)
  }
  const handleChangeType = () => {
    onChangeInputType(pc.column_name)
  }
  return (
    <FormControl>
      <Stack direction="row" spacing={2}>
        <TextField select value={value} onChange={handleChange}>
          {options.map(ucd => (
            <MenuItem key={`${pc.column_name}_${ucd.name}`} value={ucd.value}>
              {`${ucd.name} (${ucd.value})`}
            </MenuItem>
          ))}
        </TextField>
        <IconButton onClick={handleChangeType}>
          <EditIcon />
        </IconButton>
      </Stack>
    </FormControl>
  )
}
InputUcd.propTypes = {
  pc: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  onChangeInputType: PropTypes.func.isRequired,
  options: PropTypes.array.isRequired
}

export function InputAlias({ pc, onChange, onChangeInputType }) {
  const [value, setValue] = useState(pc.alias !== null ? pc.alias : '')

  const handleChange = e => {
    const inputValue = e.target.value
    setValue(inputValue)
  }

  const handleClear = () => {
    setValue('')
    onChange(pc, null)
  }

  // Using lodash debounce to Delay search by 800ms
  // Exemplo: https://www.upbeatcode.com/react/how-to-use-lodash-in-react/
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedEdit = useCallback(
    debounce(updatedValue => {
      if (updatedValue.trim() !== '') {
        onChange(pc, updatedValue)
      }
    }, 800),
    []
  )

  useEffect(() => {
    debouncedEdit(value)
  }, [value, debouncedEdit])

  const handleChangeType = () => {
    onChangeInputType(pc.column_name)
  }

  return (
    <FormControl>
      <Stack direction="row" spacing={2}>
        <TextField
          value={value}
          onChange={handleChange}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={handleClear}>
                  <CloseIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
        />
        <IconButton onClick={handleChangeType}>
          <EditIcon color="primary" />
        </IconButton>
      </Stack>
    </FormControl>
  )
}
InputAlias.propTypes = {
  pc: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  onChangeInputType: PropTypes.func.isRequired
}

export default function NewProductStep3({ productId, onNext, onPrev }) {
  const [productColumns, setProductColumns] = useState([])
  const [usedUcds, setUsedUcds] = useState([])
  const [isLoading, setLoading] = useState(false)
  const [formError, setFormError] = useState('')
  const [inputsType] = useState([])
  const [productType, setProductType] = useState(null)
  const [isValid, setIsValid] = useState(false)
  const [isValidTrainingSet, setIsValidTrainingSet] = useState(false)
  const [isValidObjectsCatalog, setIsValidObjectsCatalog] = useState(false)

  const loadProductById = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getProduct(productId)
      setProductType(res.product_type_name)
      setLoading(false)
    } catch (error) {
      setLoading(false)
      if (error.response && error.response.status === 500) {
        console.error('Internal Server Error:', error.response.data)
      } else {
        console.error('Error loading product by ID:', error.message)
      }
    }
  }, [productId])

  const loadContents = useCallback(async () => {
    setLoading(true)
    try {
      const response = await getProductContents(productId)

      setProductColumns(response.results)

      // Ao carregar as colunas identifica os campos que
      // sao do tipo alias e que ja tenham valor.
      response.results.forEach(pc => {
        if (pc.ucd === null && pc.alias !== null) {
          inputsType.push(pc.column_name)
        }
      })

      setLoading(false)
    } catch (error) {
      setLoading(false)
      if (error.response && error.response.status === 500) {
        catchFormError(error.response.data)
      }
    }
  }, [productId, inputsType])

  const changeProductContent = (pc, ucd, alias) => {
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

  useEffect(() => {
    loadProductById()
    loadContents()
  }, [loadProductById, loadContents])

  useEffect(() => {
    const useducds = []
    productColumns.forEach(row => {
      if (row.ucd !== null) {
        useducds.push(row.ucd)
      }
    })
    setUsedUcds(useducds)
  }, [productColumns])

  useEffect(() => {
    const checkValid = mandatoryUcds.every(ucd => usedUcds.includes(ucd))
    setIsValid(checkValid)
  }, [usedUcds])

  useEffect(() => {
    const checkValidTrainingSet = usedUcds.includes('src.redshift')
    setIsValidTrainingSet(checkValidTrainingSet)
  }, [usedUcds])

  useEffect(() => {
    const checkValidObjectsCatalog = ucdRaAndDec.every(ucd => usedUcds.includes(ucd))
    setIsValidObjectsCatalog(checkValidObjectsCatalog)
  }, [usedUcds])

  const handleSubmit = () => {
    onNext(productId)
  }
  const handlePrev = () => {
    onPrev(productId)
  }

  const onClear = pc => {
    changeProductContent(pc, null, null)
  }

  const onSelectUcd = (pc, ucd) => {
    changeProductContent(pc, ucd, getAliasByUcd(ucd))
  }

  const onChangeAlias = (pc, alias) => {
    changeProductContent(pc, null, alias)
  }

  const getAliasByUcd = ucd => {
    const result = ucds.find(o => o.value === ucd)
    return result ? result.name : null
  }

  const getAvailableUcds = () => {
    const avoptions = []
    ucds.forEach(ucd => {
      if (usedUcds.indexOf(ucd.value) === -1) {
        avoptions.push(ucd)
      }
    })
    return avoptions
  }

  const isInputTypeAlias = name => {
    // Se name estiver no array de input type
    // Entao Input é do tipo Alias.
    if (inputsType.indexOf(name) === -1) {
      return false
    }
    return true
  }

  function handleChangeInputType(columnName) {
    if (inputsType.indexOf(columnName) === -1) {
      inputsType.push(columnName)
    } else {
      inputsType.splice(inputsType.indexOf(columnName), 1)
    }
    loadContents(productId)
  }

  const createFields = pc => {
    const avoptions = getAvailableUcds()

    if (pc.ucd !== null) {
      return (
        <InputReadOnly
          name={pc.column_name}
          value={pc.alias}
          onClear={() => onClear(pc)}
        />
      )
    }

    // Campo de Texto para Alias
    if (isInputTypeAlias(pc.column_name)) {
      return (
        <InputAlias
          pc={pc}
          onChange={onChangeAlias}
          onChangeInputType={handleChangeInputType}
        />
      )
    }

    // Select para UCD
    return (
      <InputUcd
        pc={pc}
        options={avoptions}
        onChange={onSelectUcd}
        onChangeInputType={handleChangeInputType}
      />
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
        Please associate the column names from your file (left) with those
        expected by the tool (right).
      </Typography>
      <Typography paragraph variant="body">
        The redshift (z) is mandatory for Training Sets, and also, coordinates
        (RA, Dec) for Spec-z Catalogs.
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
          return (
            <Stack
              direction="row"
              spacing={2}
              key={`fields_${pc.column_name}`}
              mb={2}
            >
              <InputReadOnly value={pc.column_name} />
              {createFields(pc)}
            </Stack>
          )
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
        <Button
          variant="contained"
          color="primary"
          onClick={handleSubmit}
          disabled={
            (productType === 'Spec-z Catalog' && !isValid) ||
            (productType === 'Training Set' && !isValidTrainingSet) ||
            (productType === 'Objects Catalog' && !isValidObjectsCatalog)
          }
        >
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
