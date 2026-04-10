const withTM = require('next-transpile-modules')([
  'react-markdown',
  'remark-gfm'
])

module.exports = withTM({
  reactStrictMode: true,
  async rewrites() {
    return [{ source: '/front-api/:path*', destination: '/api/:path*' }]
  },
})
