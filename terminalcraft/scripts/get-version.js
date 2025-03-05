const { execSync } = require('child_process');
const fs = require('fs');

// Get the short Git hash
const gitHash = execSync('git rev-parse --short HEAD').toString().trim();

// Create or update the .env.local file
fs.writeFileSync('.env.local', `NEXT_PUBLIC_COMMIT_SHA=${gitHash}\n`, { flag: 'a' }); 