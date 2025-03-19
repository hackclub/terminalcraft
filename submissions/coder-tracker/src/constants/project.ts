export const DefaultProjectConfig = {
    track: {
        exclude: ['node_modules', 'dist', 'build', '.*/**'],
        followGitIgnore: true,
    },
} satisfies ProjectConfig

export interface ProjectConfig {
    track?: {
        exclude?: string[]
        followGitIgnore?: boolean
    }
}
