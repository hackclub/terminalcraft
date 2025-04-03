#!/usr/bin/env bun

import { migrate } from 'drizzle-orm/bun-sqlite/migrator'
import { db } from './db'

try {
    migrate(db, {
        migrationsFolder: `${import.meta.dir}/../drizzle`,
    })
} catch (e) {
    console.error('Database migration failed:', e)
    process.exit(1)
}

try {
    refreshConfig()
} catch (e) {
    console.error('Failed to refresh project configuration:', e)
    process.exit(1)
}

import { render } from 'ink'
import App from './app.js'

import { ErrorBoundary } from 'react-error-boundary'
import ErrorPage from './components/pages/ErrorPage'
import { refreshConfig } from './utils/project.js'

render(
    <ErrorBoundary fallbackRender={ErrorPage}>
        <App />
    </ErrorBoundary>,
)
