import React, { useState, useEffect } from 'react'
import {
  Container,
  Grid,
  Typography,
  TextField,
  Checkbox,
  FormGroup,
  FormControl,
  FormControlLabel,
  Button,
  Box
} from '@mui/material'
import ProductTypeSelect from '../ProductTypeSelect'
import ReleaseSelect from '../ReleaseSelect'
import FileUploader from '../FileUploader'
import useStyles from '../../styles/pages/newproduct'
import MenuItem from '@mui/material/MenuItem'

import { getProductContents, contentAssociation } from '../../services/product'

export default function NewProductStep3({ record, onNext, onPrev }) {
  const classes = useStyles()

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
    }
  ]
  // const availableUcds = []

  const [product, setProduct] = React.useState(record)
  const [productColumns, setProductColumns] = React.useState([])
  // const [availableUcds, setAvailableUcds] = React.useState([])
  const [usedUcds, setUsedUcds] = React.useState([])

  useEffect(() => {
    getProductContents(product.id).then(res => {
      const rows = res.results

      // const useducds = []
      // rows.forEach(row => {
      //   if (row.ucd !== null) {
      //     useducds.push(row.ucd)
      //   }
      // })

      setProductColumns(rows)
      // setUsedUcds(useducds)
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const useducds = []
    productColumns.forEach(row => {
      if (row.ucd !== null) {
        useducds.push(row.ucd)
      }
    })
    setUsedUcds(useducds)
  }, [productColumns])

  const handleSubmit = e => {
    console.log('Step 3 Click')
    onNext(product)
  }
  const onChangeUcd = (pc, value) => {
    if (pc.ucd === value) {
      return
    }
    console.log('handleUcd')

    // eslint-disable-next-line semi
    console.log(value)
      ; (async () => {
        // setLoading(true)
        const response = await contentAssociation(pc.id, value)
        console.log(response)
        // setRows(response.results)
        // setRowCount(response.count)
        // setLoading(false)

        // // Force Reload
        const res = await getProductContents(product.id)
        setProductColumns(res.results)
      })()
  }

  const createSelect = pc => {
    // const availableUcds = []
    // ucds.forEach(row => {
    //   if (usedUcds.indexOf(row.value) === -1) {
    //     availableUcds.push(row)
    //   }
    // })

    console.log('UsedUcds: %o', usedUcds)
    console.log('ucds: %o', ucds)
    const avoptions = []
    ucds.forEach(ucd => {
      if (usedUcds.indexOf(ucd.value) === -1 || ucd.value === pc.ucd) {
        avoptions.push(ucd)
      }
    })

    return (
      <TextField
        select
        value={pc.ucd !== null ? pc.ucd : ''}
        onChange={e => onChangeUcd(pc, e.target.value)}
        defaultValue=""
      >
        {pc.ucd !== null && (
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
        )}

        {avoptions.map(ucd =>
        (
          <MenuItem key={`${pc.column_name}_${ucd.name}`} value={ucd.value}>
            {ucd.name}
          </MenuItem>
        ))}

        {/* {ucds.forEach(ucd => {
          if (usedUcds.indexOf(ucd.value) === -1 || ucd.value === pc.ucd) {
            return (
              <MenuItem key={`${pc.column_name}_${ucd.name}`} value={ucd.value}>
                {ucd.name}
              </MenuItem>
            )
          }
        })} */}
      </TextField>
    )
  }

  const createFields = pc => {
    return (
      <div>
        <FormControl>
          <TextField value={pc.column_name} />
        </FormControl>
        <FormControl>{createSelect(pc)}</FormControl>
      </div>
    )
  }

  return (
    <div>
      <Box
        component="form"
        sx={{
          // '& > :not(style)': { m: 1 }
          '& .MuiTextField-root': { m: 1, width: '25ch' }
        }}
        autoComplete="off"
        height="400px"
        alignItems="center"
        justifyContent="center"
        style={{
          // border: "2px solid black",
          overflow: 'hidden',
          overflowY: 'scroll' // added scroll
        }}
      // onSubmit={handleSubmit}
      >
        {productColumns.map((pc, index) => {
          return createFields(pc)
        })}
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
        <Button
          variant="contained"
          color="secondary"
          onClick={onPrev}
          sx={{ mr: 1 }}
        >
          Prev
        </Button>
        <Box sx={{ flex: '1 1 auto' }} />
        <Button
          // type="submit"
          variant="contained"
          color="primary"
          onClick={handleSubmit}
        >
          Next
        </Button>
      </Box>
    </div>
  )
}
