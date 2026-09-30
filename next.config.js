/** @type {import("next").NextConfig} */
const nextConfig = {
  output: "export",
  basePath: "/ai-schedule-planner",
  assetPrefix: "/ai-schedule-planner",
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;