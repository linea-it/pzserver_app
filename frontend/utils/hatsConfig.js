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

  if (config.input && typeof config.input === 'object') {
    config.input = {
      ...config.input,
      input_col_type: magOrFlux.toLowerCase(),
      compute_magnitude: Boolean(useMagnitude),
      compute_dereddening: usesDereddening
    }
  }

  if (config.dust && typeof config.dust === 'object') {
    config.dust = {
      ...config.dust,
      use_dustmap: replacements.dereddening
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
