/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  basePath: '/ai-schedule-planner',
  assetPrefix: '/ai-schedule-planner',
}

module.exports = nextConfig
