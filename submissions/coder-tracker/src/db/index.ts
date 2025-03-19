import { Database } from 'bun:sqlite'
import { existsSync, mkdirSync } from 'fs'
import { drizzle } from 'drizzle-orm/bun-sqlite'

import { DataDirectoryPath, DatabasePath } from '../constants'

import * as schema from './schema'

if (!existsSync(DataDirectoryPath)) mkdirSync(DataDirectoryPath)

export const sqlite = new Database(DatabasePath)
export const db = drizzle({ client: sqlite, schema, casing: 'snake_case' })
