import { blob, integer, sqliteTable, text } from 'drizzle-orm/sqlite-core'

export const users = sqliteTable('users', {
    id: text().primaryKey().notNull(),
    xp: integer().default(0).notNull(),
    // Prestiges
    resets: integer().default(0).notNull(),
    /*
      Each reset has 8 unlocks, and each unlock is represented as a bit.

      RESET #0  RESET #1  ...
      00000000  00000000  ...
    */
    unlocks: blob({ mode: 'buffer' }).default(Buffer.alloc(10).fill(0)).notNull(),
    /*
      Each theme can be represented as a uint8. The last 5 bits are the reset index, and the first 3 bits are the theme index.

      RESET #n  THEME BIT #b
      00000     000


      RESET #7  THEME BIT #3
      00111     011

      The above corresponds to an active custom theme in the 3rd bit of the 7th reset, which looks like this.

      UNLOCKS #7
      BIT INDEX:  7 6 5 4 3 2 1 0

                  0 0 0 0 1 0 0 0
                          ^ (3rd bit unlocked)
    */
    activeTheme: integer(),
    // As themes and badges share the same unlocking system, this integer represents the active badge with the same bit system as the above.
    activeBadge: integer(),
    activeSessionId: text(),
})

export const usersRelations = relations(users, ({ many }) => ({
    sessions: many(sessions),
    notifications: many(notifications),
}))

export const sessions = sqliteTable('sessions', {
    id: text().primaryKey().notNull(),
    name: text().notNull(),
    finished: integer({ mode: 'boolean' }).default(false).notNull(),

    start: integer({ mode: 'timestamp' })
        .$defaultFn(() => new Date())
        .notNull(),
    duration: integer().notNull(),
    actualDuration: integer(),
    procrastinationDuration: integer().default(0).notNull(),

    // Record<FileName, [SaveCount, LineCount]>
    files: text({ mode: 'json' }).$type<Record<string, [saves: number, lines: number] | null>>(),

    userId: text().notNull(),
})

export const sessionsRelations = relations(sessions, ({ many }) => ({
    goals: many(goals),
}))

export const goals = sqliteTable('goals', {
    id: text().primaryKey().notNull(),
    name: text().notNull(),
    finished: integer({ mode: 'boolean' }).default(false).notNull(),

    userId: text().notNull(),
    sessionId: text(),

    // duration: integer(),
    // plannedDuration: integer().notNull(),
})

export const goalsRelations = relations(goals, ({ one }) => ({
    session: one(sessions, {
        fields: [goals.sessionId],
        references: [sessions.id],
    }),
}))

export const notifications = sqliteTable('notifications', {
    id: text().primaryKey().notNull(),
    userId: text().notNull(),
    message: text().notNull(),
    read: integer({ mode: 'boolean' }).default(false).notNull(),
    timestamp: integer({ mode: 'timestamp' })
        .$defaultFn(() => new Date())
        .notNull(),
})

// https://github.com/drizzle-team/drizzle-orm/issues/695#issuecomment-1881454650

import { type BuildQueryResult, type DBQueryConfig, type ExtractTablesWithRelations, relations } from 'drizzle-orm'
import type * as schema from './schema'

type Schema = typeof schema
type TSchema = ExtractTablesWithRelations<Schema>

export type IncludeRelation<TableName extends keyof TSchema> = DBQueryConfig<
    'one' | 'many',
    boolean,
    TSchema,
    TSchema[TableName]
>['with']

export type IncludeColumns<TableName extends keyof TSchema> = DBQueryConfig<
    'one' | 'many',
    boolean,
    TSchema,
    TSchema[TableName]
>['columns']

export type InferResultType<
    TableName extends keyof TSchema,
    With extends IncludeRelation<TableName> | undefined = undefined,
    Columns extends IncludeColumns<TableName> | undefined = undefined,
> = BuildQueryResult<
    TSchema,
    TSchema[TableName],
    {
        columns: Columns
        with: With
    }
>
