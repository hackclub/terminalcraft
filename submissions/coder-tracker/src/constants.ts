import { homedir } from 'os'
import { join } from 'path'

const DataDirectoryName = '.cdrtkr'

export const DataDirectoryPath = join(homedir(), DataDirectoryName)
export const DatabasePath = join(DataDirectoryPath, 'app.db')

export const ProjectConfigDirectoryName = '.cdrtkr'
export const ProjectConfigDirectoryPath = join(process.cwd(), ProjectConfigDirectoryName)
export const ProjectConfigPath = join(ProjectConfigDirectoryPath, 'proj.json')
