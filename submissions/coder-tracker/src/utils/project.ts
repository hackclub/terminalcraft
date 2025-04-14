import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'fs'

import { join } from 'path'
import { ProjectConfigDirectoryName, ProjectConfigDirectoryPath, ProjectConfigPath } from '../constants'
import { DefaultProjectConfig, type ProjectConfig } from '../constants/project'

if (!existsSync(ProjectConfigDirectoryPath)) mkdirSync(ProjectConfigDirectoryPath)
if (!existsSync(ProjectConfigPath)) writeFileSync(ProjectConfigPath, JSON.stringify(DefaultProjectConfig, null, 2))

if (existsSync(join(process.cwd(), '.git'))) {
    const Header = '# added by coder-tracker'

    try {
        const excludesPath = join(process.cwd(), '.git', 'info', 'exclude')

        if (!existsSync(excludesPath)) throw 'Exclude file not found... did you not create this repository via Git?'

        const excludes = readFileSync(excludesPath, 'utf-8')

        if (!excludes.includes(Header)) {
            console.info('Excluding the project configuration file from version control.')
            writeFileSync(excludesPath, `${excludes}\n${Header}\n${ProjectConfigDirectoryName}\n`)
        }
    } catch (e) {
        console.error('Failed to exclude configuration files from version control:', e)
    }
}

export let ProjConfig = undefined! as ProjectConfig

export async function refreshConfig() {
    ProjConfig = await import(ProjectConfigPath, { with: { type: 'json' } }).then(m => m.default)
}
