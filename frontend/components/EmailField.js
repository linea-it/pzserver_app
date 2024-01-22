import React, { useState, useEffect } from 'react'
import TextField from '@mui/material/TextField'
import PropTypes from 'prop-types'

function EmailField({ initialValue = '', onEmailChange, onClearForm }) {
  const [email, setEmail] = useState(initialValue)
  const [isValidEmail, setIsValidEmail] = useState(true)

  const handleEmailChange = event => {
    const newEmail = event.target.value
    setEmail(newEmail)
    onEmailChange(newEmail)
  }

  const handleBlur = () => {
    if (email.trim() !== '') {
      validateEmail(email)
    }
  }

  const validateEmail = value => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    const isValid = emailRegex.test(value)
    setIsValidEmail(isValid)
  }

  useEffect(() => {
    setEmail(initialValue)
    setIsValidEmail(true)
  }, [onClearForm, initialValue])

  return (
    <div>
      <TextField
        id="email"
        variant="outlined"
        value={email}
        onChange={handleEmailChange}
        onBlur={handleBlur}
        error={!isValidEmail}
        helperText={!isValidEmail ? 'Invalid email address' : ''}
      />
    </div>
  )
}

EmailField.propTypes = {
  initialValue: PropTypes.string,
  onEmailChange: PropTypes.func,
  onClearForm: PropTypes.func
}

export default EmailField
