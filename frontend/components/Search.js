// import React, { useState, useEffect } from 'react'
// import InputLabel from '@mui/material/InputLabel'
// import MenuItem from '@mui/material/MenuItem'
// import FormControl from '@mui/material/FormControl'
// import Select from '@mui/material/Select'
// import { getProductTypes } from '../services/product'

// TODO: Criar um campo de busca
// TODO: Utilizar lodash debounce para que a busca só aconteça quando o usuario parar de digitar.
// https://www.upbeatcode.com/react/how-to-use-lodash-in-react/
export default function Search() {
  // const [productTypes, setProductTypes] = useState([])
  // const [productType, setProductType] = React.useState('')
  // useEffect(() => {
  //   getProductTypes().then(res => {
  //     return setProductTypes(res.results)
  //   })
  // }, [])
  // const handleChange = event => {
  //   setProductType(event.target.value)
  // }
  // return (
  //   <div>
  //     <FormControl sx={{ m: 1, minWidth: 200 }}>
  //       <InputLabel id="product-type-select-label">Product Type</InputLabel>
  //       <Select
  //         labelId="product-type-select-label"
  //         id="product-type-select-helper"
  //         value={productType}
  //         label="Product Type"
  //         onChange={handleChange}
  //       >
  //         <MenuItem value="">
  //           <em>None</em>
  //         </MenuItem>
  //         {productTypes.map(row => (
  //           <MenuItem key={row.id} value={row.id}>
  //             {row.display_name}
  //           </MenuItem>
  //         ))}
  //       </Select>
  //     </FormControl>
  //   </div>
  // )
}
