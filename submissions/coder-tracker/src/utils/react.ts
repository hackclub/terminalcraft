// SolidJS-inspired primitives

import { useEffect, useState } from 'react'

export const onMount = (fn: () => void) => {
    useEffect(() => {
        fn()
    }, [])
}

export const onCleanup = (fn: () => void) => {
    useEffect(() => {
        return fn
    }, [])
}

export const useAsync = <T>(fn: () => Promise<T>, deps: unknown[] = []) => {
    const [state, setState] = useState<T | undefined>()

    useEffect(() => {
        fn().then(setState)
    }, deps)

    return state
}
