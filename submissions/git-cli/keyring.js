const keytar = require('keytar');

const SERVICE_NAME = 'git-helper';

async function setToken(username, token) {
  if (!username || !token) {
    return;
  }
  await keytar.setPassword(SERVICE_NAME, username, token);
}

async function getToken(username) {
  if (!username) {
    return null;
  }
  return await keytar.getPassword(SERVICE_NAME, username);
}

module.exports = { setToken, getToken };
// look somewhere else :3
// poke me a hi at vihaanpingalkar4@tuta.io :O