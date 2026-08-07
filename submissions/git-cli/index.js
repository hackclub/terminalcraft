#!/usr/bin/env node

const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');
const inquirer = require('inquirer');
const chalk = require('chalk');
const {
  createRepo,
  cloneRepo,
  pushChanges,
  syncRepo,
  manageStaging,
  setOrigin,
  configureCredentials,
  createGitignore,
  commitChanges,
  manageBranches,
  viewDiff,
  rebaseBranch
} = require('./lib/git-helpers');

async function mainMenu() {
  console.log(chalk.green.bold('\nGit Helper CLI\n'));
  const { action } = await inquirer.prompt([
    {
      type: 'list',
      name: 'action',
      message: 'What do you want to do?',
      choices: [
        { name: 'Create a new git repository', value: 'create' },
        { name: 'Clone a repository', value: 'clone' },
        { name: 'Manage staging area (add/remove files)', value: 'stage' },
        { name: 'Commit staged changes', value: 'commit' },
        { name: 'Push changes', value: 'push' },
        { name: 'Sync (pull & push)', value: 'sync' },
        { name: 'Manage branches', value: 'branch' },
        { name: 'View diff', value: 'diff' },
        { name: 'Rebase current branch', value: 'rebase' },
        { name: 'Set remote origin', value: 'origin' },
        { name: 'Create .gitignore file', value: 'gitignore' },
        { name: 'Configure credentials (user/PAT)', value: 'config' },
        { name: 'Exit', value: 'exit' }
      ]
    }
  ]);

  switch (action) {
    case 'create':
      await createRepo();
      break;
    case 'clone':
      await cloneRepo();
      break;
    case 'stage':
      await manageStaging();
      break;
    case 'commit':
      await commitChanges();
      break;
    case 'push':
      await pushChanges();
      break;
    case 'sync':
      await syncRepo();
      break;
    case 'branch':
      await manageBranches();
      break;
    case 'diff':
      await viewDiff();
      break;
    case 'rebase':
      await rebaseBranch();
      break;
    case 'origin':
      await setOrigin();
      break;
    case 'gitignore':
      await createGitignore();
      break;
    case 'config':
      await configureCredentials();
      break;
    case 'exit':
      console.log(chalk.blue('Goodbye!'));
      process.exit(0);
  }
  mainMenu();
}

const cli = yargs(hideBin(process.argv))
  .command('push', 'Commit and push changes', (yargs) => {
    return yargs
      .option('m', {
        alias: 'message',
        describe: 'Commit message',
        type: 'string',
      })
      .option('dir', {
        describe: 'Repository directory',
        type: 'string',
      });
  }, (argv) => {
    pushChanges({ msg: argv.m, dir: argv.dir });
  })
  .command('sync', 'Pull remote changes, commit and push', (yargs) => {
    return yargs.option('dir', {
      describe: 'Repository directory',
      type: 'string',
    });
  }, (argv) => {
    syncRepo({ dir: argv.dir });
  })
  .command('clone <repo> [dir]', 'Clone a repository', {}, (argv) => {
    cloneRepo({ repo: argv.repo, dir: argv.dir });
  })
  .command('stage', 'Manage staging area (interactive)', {}, () => {
    manageStaging();
  })
  .command('commit', 'Commit staged changes', (yargs) => {
    return yargs
      .option('m', {
        alias: 'message',
        describe: 'Commit message',
        type: 'string',
      })
      .option('dir', {
        describe: 'Repository directory',
        type: 'string',
      });
  }, (argv) => {
    commitChanges({ msg: argv.m, dir: argv.dir });
  })
  .command('branch', 'Manage branches (interactive)', {}, () => {
    manageBranches();
  })
  .command('diff', 'View diff of changes', (yargs) => {
    return yargs
      .option('staged', {
        describe: 'Show diff for staged changes',
        type: 'boolean'
      })
      .option('dir', {
        describe: 'Repository directory',
        type: 'string',
      });
  }, (argv) => {
    viewDiff({ staged: argv.staged, dir: argv.dir });
  })
  .command('rebase <branch>', 'Rebase current branch onto another branch', (yargs) => {
    return yargs.option('dir', {
      describe: 'Repository directory',
      type: 'string',
    });
  }, (argv) => {
    rebaseBranch({ branch: argv.branch, dir: argv.dir });
  })
  .command('origin <url>', 'Set remote origin URL', (yargs) => {
    return yargs.option('dir', {
      describe: 'Repository directory',
      type: 'string',
    });
  }, (argv) => {
    setOrigin({ url: argv.url, dir: argv.dir });
  })
  .command('config', 'Configure credentials (interactive or with flags)', (yargs) => {
    return yargs
      .option('username', { type: 'string', describe: 'GitHub username' })
      .option('token', { type: 'string', describe: 'GitHub Personal Access Token' });
  }, (argv) => {
    configureCredentials({ username: argv.username, token: argv.token });
  })
  .command('init', 'Create a new git repository', (yargs) => {
    return yargs.option('dir', {
      describe: 'Directory to initialize repo in',
      type: 'string',
    });
  }, (argv) => {
    createRepo({ dir: argv.dir });
  })
  .command('gitignore', 'Create a standard .gitignore file', (yargs) => {
    return yargs.option('dir', {
      describe: 'Directory to create .gitignore in',
      type: 'string',
    });
  }, (argv) => {
    createGitignore({ dir: argv.dir });
  })
  .help()
  .alias('h', 'help');

const argv = cli.argv;

// interactive cli if no command was given in the args
if (argv._.length === 0 && process.argv.length <= 2) {
  mainMenu();
}