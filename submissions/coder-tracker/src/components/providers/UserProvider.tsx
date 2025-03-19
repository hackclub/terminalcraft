import { userInfo } from 'os'
import { eq } from 'drizzle-orm'
import { type ReactNode, createContext, useCallback, useContext, useEffect, useState } from 'react'
import { db } from '../../db'
import { type InferResultType, users } from '../../db/schema'

export type User = InferResultType<'users'>

const UserContext = createContext<User & { refetch(): Promise<void> }>(undefined!)

export default function ThemeProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | undefined>(undefined)
    const uname = userInfo().username

    const refetch = useCallback(async () => {
        await db.query.users
            .findFirst({
                where: eq(users.id, uname),
            })
            .then(user => {
                if (user) {
                    setUser(user)
                } else {
                    db.insert(users)
                        .values({ id: uname, xp: 0 })
                        .returning()
                        .then(([user]) => setUser(user!))
                }
            })
    }, [uname])

    useEffect(() => {
        refetch()
    }, [refetch])

    return user && <UserContext.Provider value={{ ...user, refetch }}>{children}</UserContext.Provider>
}

export const useUser = () => useContext(UserContext)
