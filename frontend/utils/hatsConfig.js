import { dump, load } from 'js-yaml'

const PLACEHOLDERS = {
  '<FLUX>': values => values.flux,
  '<MAG_OR_FLUX>': values => values.magOrFlux,
  '<DEREDDENING>': values => values.dereddening
}

const replaceStringPlaceholders = (value, replacements) => {
  return Object.entries(PLACEHOLDERS).reduce(
    (result, [placeholder, select]) => {
      return result.split(placeholder).join(select(replacements))
    },
    value
  )
}

const replacePlaceholders = (value, replacements) => {
  if (typeof value === 'string') {
    return replaceStringPlaceholders(value, replacements)
  }

  if (Array.isArray(value)) {
    return value.map(item => replacePlaceholders(item, replacements))
  }

  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([key, child]) => [
        key,
        replacePlaceholders(child, replacements)
      ])
    )
  }

  return value
}

const createInvalidHandling = useMagnitude => {
  const replacementValue = useMagnitude ? 99.0 : null
  const createChannel = () => ({
    nonfinite_is_invalid: true,
    ...(useMagnitude
      ? {
          limit: {
            value: 99.0,
            comparison: 'greater_or_equal',
            use_absolute: true
          }
        }
      : {}),
    replacement: {
      value: replacementValue,
      when: 'invalid'
    }
  })

  return {
    value: createChannel(),
    error: createChannel()
  }
}

export const customizeHatsConfig = (
  template,
  { flux, dereddening, useMagnitude }
) => {
  if (!template) return null

  const magOrFlux = useMagnitude ? 'Mag' : 'Flux'
  const replacements = {
    flux: String(flux || ''),
    dereddening: String(dereddening || ''),
    magOrFlux
  }
  const config = replacePlaceholders(template, replacements)
  const usesDereddening =
    replacements.dereddening !== '' &&
    replacements.dereddening.toLowerCase() !== 'none'
  const outputType = `${useMagnitude ? 'mag' : 'flux'}${
    usesDereddening ? '_dered' : ''
  }`
  const dereddeningSuffix = usesDereddening
    ? `_${replacements.dereddening}`
    : ''
  const outputValuePattern = `BAND_${replacements.flux}${magOrFlux}${dereddeningSuffix}`
  const outputErrorPattern = `BAND_${replacements.flux}${magOrFlux}Err${dereddeningSuffix}`

  if (config.dust && typeof config.dust === 'object') {
    config.dust = {
      ...config.dust,
      use_dustmap: usesDereddening ? replacements.dereddening : null
    }
  }

  if (config.photometry && typeof config.photometry === 'object') {
    const measurements = Array.isArray(config.photometry.measurements)
      ? config.photometry.measurements.map(measurement => {
          if (!measurement || typeof measurement !== 'object') {
            return measurement
          }

          return {
            ...measurement,
            output: {
              ...(measurement.output || {}),
              type: outputType,
              value_pattern: outputValuePattern,
              error_pattern: outputErrorPattern
            }
          }
        })
      : config.photometry.measurements

    config.photometry = {
      ...config.photometry,
      measurements,
      invalid_handling: createInvalidHandling(Boolean(useMagnitude))
    }
  }

  return config
}

export const serializeHatsConfig = config => {
  if (!config) return ''

  return dump(config, {
    lineWidth: -1,
    noRefs: true,
    sortKeys: false
  })
}

export const parseHatsConfig = yaml => {
  const config = load(yaml)

  if (!config || typeof config !== 'object' || Array.isArray(config)) {
    throw new Error('The HATS configuration must be a YAML object.')
  }

  return config
}
