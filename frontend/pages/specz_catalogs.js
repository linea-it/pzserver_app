import React, { useState } from 'react'
import {
  Typography,
  IconButton,
  Select,
  MenuItem,
  TextField
} from '@mui/material'
import InfoIcon from '@mui/icons-material/Info'
import SpeczData from '../components/SpeczData'

export default function SpeczCatalogs() {
  const [combinedCatalogName, setCombinedCatalogName] = useState('')
  const [selectedSpeczCatalogs, setSelectedSpeczCatalogs] = useState([])
  const [searchRadius, setSearchRadius] = useState('')

  const handleCatalogNameChange = event => {
    setCombinedCatalogName(event.target.value)
  }

  const handleSpeczCatalogsChange = event => {
    setSelectedSpeczCatalogs(event.target.value)
  }

  const handleSearchRadiusChange = event => {
    setSearchRadius(event.target.value)
  }

  return (
    <div>
      <Typography variant="h4" style={{ textAlign: 'center' }}>
        Combine Spec-z Catalogs
        <IconButton aria-label="info" title="Combine Spec-z Catalogs">
          <InfoIcon />
        </IconButton>
      </Typography>

      <div>
        <p>1. Combined catalog name:</p>
        <TextField
          id="combinedCatalogName"
          label="Combined catalog name"
          variant="outlined"
          value={combinedCatalogName}
          onChange={handleCatalogNameChange}
        />
      </div>

      <div>
        <p>2. Select the Spec-z Catalogs to include in your sample:</p>
        <Select
          multiple
          value={selectedSpeczCatalogs}
          onChange={handleSpeczCatalogsChange}
        >
          <MenuItem value="catalog1">teste 1</MenuItem>
          <MenuItem value="catalog2">teste 2</MenuItem>
        </Select>
        <TextField
          id="searchSpeczCatalogs"
          label="Search Spec-z Catalogs"
          variant="outlined"
        />
      </div>

      <SpeczData />

      <div>
        <p>3. Select the cross-matching configuration choices:</p>
        <TextField
          id="searchRadius"
          label="Search Radius (arcsec)"
          variant="outlined"
          value={searchRadius}
          onChange={handleSearchRadiusChange}
        />
      </div>
    </div>
  )
}
