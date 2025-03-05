/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_COMMIT_SHA: process.env.VERCEL_GIT_COMMIT_SHA 
      ? process.env.VERCEL_GIT_COMMIT_SHA.slice(0, 7)
      : require('child_process')
          .execSync('git rev-parse --short HEAD')
          .toString()
          .trim(),
  },
}

module.exports = nextConfig 