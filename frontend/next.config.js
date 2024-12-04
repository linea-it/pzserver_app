module.exports = {
  reactStrictMode: true,
  images: {
    domains: ['identity.linea.org.br'],
  },
  async rewrites() {
    return [{ source: '/front-api/:path*', destination: '/api/:path*' }]
  },
}
