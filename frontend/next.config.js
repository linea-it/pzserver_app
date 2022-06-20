module.exports = {
  reactStrictMode: true,
  async rewrites() {
    return [{ source: '/front-api/:path*', destination: '/api/:path*' }]
  }
}
