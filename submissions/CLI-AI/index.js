#!/usr/bin/env node

const blessed = require('blessed');
const { Command } = require('commander');
const { OpenAI } = require('openai');
const { Anthropic } = require('@anthropic-ai/sdk');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');
const TOML = require('@iarna/toml');

dotenv.config();

// create history directory if it doesn't exist
const historyDir = path.join(__dirname, 'history');
if (!fs.existsSync(historyDir)) {
  fs.mkdirSync(historyDir);
}

const program = new Command();
program
  .name('ai-chat')
  .description('CLI tool for chatting with various AI providers')
  .version('1.0.0')
  .option('-p, --provider <provider>', 'AI provider to use (openai, claude, gemini, grok)', 'openai')
  .parse(process.argv);

const options = program.opts();

// create the main screen
const screen = blessed.screen({
  smartCSR: true,
  title: `AI Chat (${options.provider.toUpperCase()})`,
});

// create chat history box
const chatBox = blessed.box({
  top: 0,
  left: 0,
  width: '100%',
  height: '90%',
  scrollable: true,
  alwaysScroll: true,
  tags: true,
  border: {
    type: 'line',
  },
  style: {
    border: {
      fg: 'white', // make border white
    },
  },
});

// create input box - fix configuration to prevent character doubling
const inputBox = blessed.textbox({
  bottom: 0,
  left: 0,
  width: '100%',
  height: 3,
  inputOnFocus: true,
  keys: true,
  mouse: true,
  border: {
    type: 'line',
  },
  style: {
    border: {
      fg: 'white',
    },
    focus: {
      border: {
        fg: 'green',
      },
    },
  },
  // important: disable key handling in cbreak mode to prevent doubling
  cbreak: true
});

// create settings box with more height to accommodate API key inputs
const settingsBox = blessed.box({
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  label: ' settings ',
  border: {
    type: 'line',
  },
  style: {
    border: {
      fg: 'white',
    },
    focus: {
      border: {
        fg: 'white',
      },
    },
  },
  hidden: true,
  keys: true,
  mouse: true,
  tags: true,
  scrollable: true,
});

// add provider selection list to settings
const providerLabel = blessed.text({
  parent: settingsBox,
  top: 2,
  left: 4,
  content: 'choose provider:',
  style: {
    fg: 'white',
  },
});

const providers = ['openai', 'claude', 'gemini', 'grok'];
// fix providerList configuration to properly handle selection
const providerList = blessed.list({
  parent: settingsBox,
  top: 4,
  left: 6,
  width: '30%',
  height: providers.length + 2,
  items: providers.map(p => (p === options.provider ? `* ${p}` : `  ${p}`)),
  keys: true,
  mouse: true,
  interactive: true,  // ensure it's interactive
  style: {
    fg: 'white',
    selected: {
      bg: 'blue',
      fg: 'white',
    },
    item: {
      hover: {
        bg: 'gray'
      }
    }
  },
  border: {
    type: 'line',
    fg: 'white'
  },
  tags: true,
  vi: true,
});

// add model selection to settings
const modelLabel = blessed.text({
  parent: settingsBox,
  top: providers.length + 7,
  left: 4,
  content: 'choose model:',
  style: {
    fg: 'white',
  },
});

// available models for each provider
const providerModels = {
  openai: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
  claude: ['claude-3-5-sonnet-20240620', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
  gemini: ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro'],
  grok: ['grok-1']
};

// track selected model for each provider
const selectedModels = {
  openai: 'gpt-4o',
  claude: 'claude-3-5-sonnet-20240620',
  gemini: 'gemini-1.5-pro',
  grok: 'grok-1'
};

// fix modelList configuration to properly handle selection
const modelList = blessed.list({
  parent: settingsBox,
  top: providers.length + 9,
  left: 6,
  width: '50%',
  height: 6, // show a few models at a time
  items: providerModels[options.provider].map(m => (m === selectedModels[options.provider] ? `* ${m}` : `  ${m}`)),
  keys: true,
  mouse: true,
  interactive: true,  // ensure it's interactive
  style: {
    fg: 'white',
    selected: {
      bg: 'blue',
      fg: 'white',
    },
    item: {
      hover: {
        bg: 'gray'
      }
    }
  },
  border: {
    type: 'line',
    fg: 'white'
  },
  tags: true,
  vi: true,
  scrollable: true,
});

// replace API key input section with simple message about editing .env file
const apiKeyLabel = blessed.text({
  parent: settingsBox,
  top: providers.length + 16,
  left: 4,
  content: 'api keys:',
  style: {
    fg: 'white',
  },
});

const apiKeyInstructions = blessed.text({
  parent: settingsBox,
  top: providers.length + 18,
  left: 6,
  width: '80%',
  content: 'to set API keys, edit the .env file in the project directory.\nexample:\nOPENAI_API_KEY=your_key_here\nCLAUDE_API_KEY=your_key_here',
  style: {
    fg: 'yellow',
  },
});

// append our boxes to the screen earlier to ensure they're initialized
screen.append(chatBox);
screen.append(inputBox);
screen.append(settingsBox);

// create history box
const historyBox = blessed.box({
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  label: ' chat history ',
  border: {
    type: 'line',
  },
  style: {
    border: {
      fg: 'white',
    },
    focus: {
      border: {
        fg: 'white',
      },
    },
  },
  hidden: true,
  keys: true,
  mouse: true,
  tags: true,
  scrollable: true,
});

// add chat history list
const historyList = blessed.list({
  parent: historyBox,
  top: 2,
  left: 4,
  width: '90%',
  height: '80%',
  keys: true,
  mouse: true,
  style: {
    fg: 'white',
    selected: {
      bg: 'blue',
      fg: 'white',
    },
    item: {
      hover: {
        bg: 'gray'
      }
    }
  },
  border: {
    type: 'line',
    fg: 'white'
  },
  tags: true,
  vi: true,
  scrollable: true,
});

// add new chat button
const newChatButton = blessed.button({
  parent: historyBox,
  bottom: 2,
  left: 4,
  width: 15,
  height: 3,
  content: 'New Chat',
  align: 'center',
  valign: 'middle',
  border: {
    type: 'line',
    fg: 'white'
  },
  style: {
    fg: 'white',
    focus: {
      fg: 'blue',
    },
    hover: {
      bg: 'blue',
      fg: 'white'
    }
  },
  mouse: true,
  keys: true,
});

// handle new chat button click
newChatButton.on('press', () => {
  startNewChat();
  historyBox.hide();
  inputBox.focus();
  screen.render();
});

// current chat session
let currentChat = {
  id: Date.now().toString(),
  title: 'New Chat',
  provider: options.provider,
  model: selectedModels[options.provider],
  messages: []
};

// function to start a new chat
function startNewChat() {
  chatHistory.length = 0;
  messageContext.length = 0;
  
  currentChat = {
    id: Date.now().toString(),
    title: 'New Chat',
    provider: options.provider,
    model: selectedModels[options.provider],
    messages: []
  };
  
  chatBox.setContent('');
  addMessage('system', `started new chat with ${options.provider} (${selectedModels[options.provider]})`);
}

// sae current chat to TOML file
function saveCurrentChat() {
  if (chatHistory.length <= 1) return; // don't save empty chats (just system message)
  
  // update current chat object
  currentChat.messages = messageContext;
  currentChat.provider = options.provider;
  currentChat.model = selectedModels[options.provider];
  
  // set title to first user message if not custom titled
  if (currentChat.title === 'New Chat' && messageContext.length > 0) {
    const firstUserMsg = messageContext.find(m => m.role === 'user');
    if (firstUserMsg) {
      currentChat.title = firstUserMsg.content.substring(0, 30) + (firstUserMsg.content.length > 30 ? '...' : '');
    }
  }
  
  try {
    const tomlStr = TOML.stringify(currentChat);
    const filename = path.join(historyDir, `${currentChat.id}.toml`);
    fs.writeFileSync(filename, tomlStr);
    return true;
  } catch (error) {
    addMessage('system', `error saving chat: ${error.message}`);
    return false;
  }
}

// load a chat from file
function loadChat(chatId) {
  try {
    const filename = path.join(historyDir, `${chatId}.toml`);
    const tomlStr = fs.readFileSync(filename, 'utf8');
    const chatData = TOML.parse(tomlStr);
    
    // update current chat
    currentChat = chatData;
    
    // set provider and model from saved chat
    if (providers.includes(chatData.provider)) {
      options.provider = chatData.provider;
      if (providerModels[options.provider].includes(chatData.model)) {
        selectedModels[options.provider] = chatData.model;
      }
    }
    
    // update screen title
    screen.title = `AI Chat (${options.provider.toUpperCase()})`;
    
    // clear existing chat
    chatHistory.length = 0;
    messageContext.length = 0;
    
    // reload messages
    chatBox.setContent('');
    addMessage('system', `loaded chat: ${chatData.title}`);
    
    // add saved messages to context and display
    if (Array.isArray(chatData.messages)) {
      for (const msg of chatData.messages) {
        const role = msg.role === 'user' ? 'user' : 'ai';
        addMessage(role, msg.content);
      }
    }
    
    // reinitialize clients with the chat's provider
    initClients();
    
    return true;
  } catch (error) {
    addMessage('system', `error loading chat: ${error.message}`);
    return false;
  }
}

// list all available chats
function listChats() {
  try {
    const files = fs.readdirSync(historyDir).filter(f => f.endsWith('.toml'));
    const chats = [];
    
    for (const file of files) {
      try {
        const tomlStr = fs.readFileSync(path.join(historyDir, file), 'utf8');
        const chatData = TOML.parse(tomlStr);
        chats.push({
          id: chatData.id,
          title: chatData.title || 'Untitled Chat',
          provider: chatData.provider || 'unknown',
          timestamp: parseInt(chatData.id) || 0
        });
      } catch (e) {
        // Skip invalid files
      }
    }
    
    // Sort by timestamp (newest first)
    chats.sort((a, b) => b.timestamp - a.timestamp);
    
    // Update history list
    historyList.setItems(chats.map(c => `${c.title} (${c.provider})`));
    historyList.selectedIndex = 0;
    
    // Store chat IDs for selection
    historyList.chatIds = chats.map(c => c.id);
    
    return chats;
  } catch (error) {
    addMessage('system', `error listing chats: ${error.message}`);
    return [];
  }
}

// handle history list selection
historyList.on('select', (item, idx) => {
  if (historyList.chatIds && historyList.chatIds[idx]) {
    loadChat(historyList.chatIds[idx]);
    historyBox.hide();
    inputBox.focus();
    screen.render();
  }
});

// reload history list when showing history box
screen.key(['C-h'], () => {
  // Save current chat before showing history
  saveCurrentChat();
  
  // show history box and list chats
  historyBox.show();
  activeScreen = 'history';
  focusIndex = 0; // reset focus to first history element
  listChats();
  
  // make sure we're focusing on the right element
  if (focusableElements.history && focusableElements.history.length > 0) {
    focusableElements.history[focusIndex].focus();
  }
  
  screen.render();
});

// close history with escape and reset focus
historyBox.key('escape', () => {
  historyBox.hide();
  activeScreen = 'chat';
  focusIndex = 0;
  inputBox.focus();
  screen.render();
});

// array to store chat history for display
const chatHistory = [];
// array to store message objects for context
const messageContext = [];
const CONTEXT_LIMIT = 10; // how many messages to keep in context

// function to add messages to chat history and context
function addMessage(role, content) {
  const timestamp = new Date().toLocaleTimeString();
  // user is yellow, ai is green, system is cyan
  let color = 'green-fg';
  if (role === 'user') color = 'yellow-fg';
  if (role === 'system') color = 'cyan-fg';
  // keep user message in chat style
  const message = `{${color}} ${timestamp} ${role}: {/}${content}`;
  chatHistory.push(message);
  // add to context if user or ai
  if (role === 'user' || role === 'ai') {
    messageContext.push({ role: role === 'ai' ? 'assistant' : 'user', content });
    // keep only last CONTEXT_LIMIT messages
    if (messageContext.length > CONTEXT_LIMIT) {
      messageContext.shift();
    }
    
    // auto-save chat after each message exchange
    if (messageContext.length > 0 && messageContext.length % 2 === 0) {
      saveCurrentChat();
    }
  }
  chatBox.setContent(chatHistory.join('\n\n'));
  chatBox.scrollTo(chatBox.getScrollHeight());
  screen.render();
}

// strip markdown from text
function stripMarkdown(text) {
  // remove code blocks
  text = text.replace(/```[\s\S]*?```/g, '');
  // remove headers
  text = text.replace(/#+\s+/g, '');
  // remove bold/italic
  text = text.replace(/(\*\*|__)(.*?)\1/g, '$2');
  text = text.replace(/(\*|_)(.*?)\1/g, '$2');
  // remove links
  text = text.replace(/\[(.*?)\]\(.*?\)/g, '$1');
  // remove images
  text = text.replace(/!\[(.*?)\]\(.*?\)/g, '$1');
  // remove blockquotes
  text = text.replace(/^\s*>\s+/gm, '');
  
  return text;
}

// initialize the ai clients based on provider
let openaiClient, claudeClient, geminiClient;

function initClients() {
  if (options.provider === 'openai' && process.env.OPENAI_API_KEY) {
    openaiClient = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  } else if (options.provider === 'claude' && process.env.ANTHROPIC_API_KEY) {
    claudeClient = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
  } else if (options.provider === 'gemini' && process.env.GEMINI_API_KEY) {
    geminiClient = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
  }
}

// function to send message to the selected ai provider
async function sendToAI(message) {
  try {
    let response;
    // build context for providers that support it
    const contextMessages = [...messageContext, { role: 'user', content: message }];
    switch (options.provider) {
      case 'openai':
        if (!openaiClient) {
          return 'OpenAI API key not configured. Please add it to your .env file.';
        }
        // pass context messages and use selected model
        const openaiCompletion = await openaiClient.chat.completions.create({
          model: selectedModels.openai,
          messages: contextMessages,
        });
        response = openaiCompletion.choices[0].message.content;
        break;
      case 'claude':
        if (!claudeClient) {
          return 'Claude API key not configured. Please add it to your .env file.';
        }
        // use selected model
        const claudeCompletion = await claudeClient.messages.create({
          model: selectedModels.claude,
          max_tokens: 1000,
          messages: contextMessages,
        });
        response = claudeCompletion.content[0].text;
        break;
      case 'gemini':
        if (!geminiClient) {
          return 'Gemini API key not configured. Please add it to your .env file.';
        }
        // use selected model
        const geminiModel = geminiClient.getGenerativeModel({ model: selectedModels.gemini });
        const contextText = contextMessages.map(m => `${m.role}: ${m.content}`).join('\n');
        const geminiResult = await geminiModel.generateContent(contextText);
        response = geminiResult.response.text();
        break;
      case 'grok':
        if (!process.env.GROK_API_KEY) {
          return 'Grok API key not configured. Please add it to your .env file.';
        }
        // use selected model
        const grokResponse = await axios.post('https://api.grok.x/v1/chat/completions', {
          model: selectedModels.grok,
          messages: contextMessages,
        }, {
          headers: {
            'Authorization': `Bearer ${process.env.GROK_API_KEY}`,
            'Content-Type': 'application/json',
          },
        });
        response = grokResponse.data.choices[0].message.content;
        break;
      default:
        response = "Unknown provider. Please select openai, claude, gemini, or grok.";
    }
    return stripMarkdown(response);
  } catch (error) {
    return `error: ${error.message}`;
  }
}

// remove duplicate tab key handler and combine functionality
// tab navigation: 0 = chat, 1 = settings
let tabIndex = 0;
const tabs = ['chat', 'settings'];

// append history box to screen
screen.append(historyBox);

// update focusable elements for tab navigation to include history elements
// group elements by their respective screens for better organization
const focusableElements = {
  chat: [inputBox],
  settings: [providerList, modelList],
  history: [historyList, newChatButton]
};

// track which screen is active
let activeScreen = 'chat';
let focusIndex = 0;

// handle tab key for navigation - improved handler with better screen awareness
screen.key('tab', () => {
  // determine which set of elements to cycle through based on active screen
  const currentElements = focusableElements[activeScreen];
  
  if (currentElements && currentElements.length > 0) {
    // move to next element in the current screen's element list
    focusIndex = (focusIndex + 1) % currentElements.length;
    currentElements[focusIndex].focus();
    screen.render();
  }
});

// use ctrl+s to toggle settings with improved focus management
screen.key(['C-s'], () => {
  if (settingsBox.hidden) {
    // switch to settings screen
    settingsBox.show();
    activeScreen = 'settings';
    focusIndex = 0; // reset focus to first settings element
    focusableElements.settings[focusIndex].focus();
  } else {
    // switch back to chat screen
    settingsBox.hide();
    activeScreen = 'chat';
    focusIndex = 0;
    inputBox.focus();
  }
  screen.render();
});

// close settings with esc and reset focus
settingsBox.key('escape', () => {
  settingsBox.hide();
  activeScreen = 'chat';
  focusIndex = 0;
  inputBox.focus();
  screen.render();
});

// update history navigation with improved focus management
screen.key(['C-h'], () => {
  // Save current chat before showing history
  saveCurrentChat();
  
  // Show history box and list chats
  historyBox.show();
  activeScreen = 'history';
  focusIndex = 0; // reset focus to first history element
  listChats();
  focusableElements.history[focusIndex].focus();
  screen.render();
});

// close history with escape and reset focus
historyBox.key('escape', () => {
  historyBox.hide();
  activeScreen = 'chat';
  focusIndex = 0;
  inputBox.focus();
  screen.render();
});

// handle new chat button click with focus reset
newChatButton.on('press', () => {
  startNewChat();
  historyBox.hide();
  activeScreen = 'chat';
  focusIndex = 0;
  inputBox.focus();
  screen.render();
});

// improve provider selection handler
providerList.on('select', function(item, idx) {
  // update provider option and re-init clients
  const selectedProvider = providers[idx];
  
  if (options.provider !== selectedProvider) {
    options.provider = selectedProvider;
    screen.title = `AI Chat (${options.provider.toUpperCase()})`;
    
    // update list display
    providerList.setItems(providers.map(p => 
      (p === options.provider ? `* ${p}` : `  ${p}`)
    ));
    
    // update model list for the new provider
    modelList.setItems(providerModels[options.provider].map(m => 
      (m === selectedModels[options.provider] ? `* ${m}` : `  ${m}`)
    ));
    
    initClients();
    addMessage('system', `provider changed to ${options.provider}`);
  }
  
  // make sure interface stays in settings
  activeScreen = 'settings';
  
  // ensure selected item is visible
  providerList.select(idx);
  
  screen.render();
});

// improve model selection handler
modelList.on('select', function(item, idx) {
  if (idx < 0 || idx >= providerModels[options.provider].length) return;
  
  const selectedModel = providerModels[options.provider][idx];
  
  if (selectedModels[options.provider] !== selectedModel) {
    // update selected model for current provider
    selectedModels[options.provider] = selectedModel;
    
    // update model list display
    modelList.setItems(providerModels[options.provider].map(m => 
      (m === selectedModels[options.provider] ? `* ${m}` : `  ${m}`)
    ));
    
    addMessage('system', `model changed to ${selectedModels[options.provider]}`);
  }
  
  // make sure interface stays in settings
  activeScreen = 'settings';
  
  // ensure selected item is visible
  modelList.select(idx);
  
  screen.render();
});

// add direct key handlers for ENTER on lists to force selection
providerList.key('enter', function() {
  const idx = this.selected;
  if (idx !== undefined && idx >= 0 && idx < providers.length) {
    this.emit('select', this.items[idx].content, idx);
  }
});

modelList.key('enter', function() {
  const idx = this.selected;
  if (idx !== undefined && idx >= 0 && idx < providerModels[options.provider].length) {
    this.emit('select', this.items[idx].content, idx);
  }
});

// handle input submission - ensure proper input handling and fix message display
inputBox.on('submit', async (text) => {
  const message = text;
  if (message.trim()) {
    // clear input
    inputBox.clearValue();
    screen.render();
    
    // don't capitalize first letter and don't correct grammar
    addMessage('user', message);
    
    // show thinking indicator as a temporary message without changing the history
    let thinkingMessage = `{cyan-fg}AI is thinking...{/}`;
    chatBox.setContent(chatHistory.join('\n\n') + '\n\n' + thinkingMessage);
    screen.render();
    
    // get response
    const response = await sendToAI(message);
    
    // replace thinking indicator with actual response by setting content directly
    addMessage('ai', response);
    
    // save chat after response
    saveCurrentChat();
  }
  
  inputBox.focus();
});

// this ensures we don't have key event duplication
// only use the single 'enter' key handler to submit
inputBox.key('enter', function() {
  const value = this.getValue();
  this.clearValue();
  this.submit(value);
});

// fix input handling to ensure no character doubling
inputBox.options.cbreak = false;
inputBox.options.keyable = true;

// clear and reset input handlers
inputBox.removeAllListeners('keypress');

// start the application with better instructions
initClients();
inputBox.focus();
addMessage('system', `welcome to CLI-AI chat! you're now chatting with ${options.provider} (${selectedModels[options.provider]}).
type your message and press enter to send.
press ctrl+c to quit.
press ctrl+s for settings.
press ctrl+h for chat history.
api keys should be configured in the .env file.`);
screen.render();

// Fix exit handling - ensure ctrl+c works properly
screen.key(['C-c'], function() {
  // Properly exit the process when ctrl+c is pressed
  process.exit(0);
});

// Make sure blessed captures these key events
screen.enableKeys();

// Enable direct control over input
inputBox.key(['C-c'], function() {
  process.exit(0);
});

// Set a global process handler as a fallback
process.on('SIGINT', function() {
  process.exit(0);
});
