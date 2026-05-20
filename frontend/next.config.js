module.exports = {
  reactStrictMode: true,
  transpilePackages: ['react-markdown', 'remark-gfm'],
  distDir: process.env.NEXT_DIST_DIR || '.next',
  async rewrites() {
    return [{ source: '/front-api/:path*', destination: '/api/:path*' }]
  },
}
