import { existsSync, mkdirSync } from 'fs'
import { pathToFileURL } from 'bun'
import { defineConfig } from 'drizzle-kit'
import { DataDirectoryPath, DatabasePath } from './src/constants'

if (!existsSync(DataDirectoryPath)) mkdirSync(DataDirectoryPath)

export default defineConfig({
    dialect: 'sqlite',
    schema: './src/db/schema.ts',
    casing: 'snake_case',
    dbCredentials: {
        url: `file:${pathToFileURL(DatabasePath).href}`,
    },
})
