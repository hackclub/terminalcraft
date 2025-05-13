const color = require('ansi-colors');
const readline = require('readline');
const axios = require('axios');
require('dotenv').config();


const theme = {
  title: color.bold.yellow,
  header: color.bold.green,
  alert: color.bold.red,
  damage: color.red,
  heal: color.green,
  mana: color.blue,
  npc: color.cyan,
  item: color.yellow,
  location: color.magenta,
  input: color.italic,
  reset: color.reset
};


const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});


const gameState = {
  playerName: '',
  playerClass: '',
  playerHealth: 100,
  playerMana: 50,
  playerInventory: [],
  currentLocation: 'Unknown',
  gameHistory: [],
  turnCount: 0
};


const GROQ_API_KEY = process.env.GROQ_API_KEY;
const GROQ_MODEL = "llama3-70b-8192";
const MAX_HISTORY = 20;

function getSystemPrompt() {
  return `
You are an expert text RPG Dungeon Master. Current game state:
- Player: ${gameState.playerName} the ${gameState.playerClass}
- Health: ${gameState.playerHealth}
- Mana: ${gameState.playerMana}
- Location: ${gameState.currentLocation}
- Inventory: ${gameState.playerInventory.join(', ') || 'Empty'}
- Turn: ${gameState.turnCount}

Rules:
1. Always provide detailed responses
2. Update game state logically
3. Include environmental details
4. Maintain consistent world logic
5. Limit responses to 3 paragraphs`;
}

async function callGroqAPI(userInput) {
  try {
    const messages = [
      { role: "system", content: getSystemPrompt() },
      ...gameState.gameHistory.slice(-MAX_HISTORY),
      { role: "user", content: userInput }
    ];

    let response;
    if (GROQ_API_KEY) {
      response = await axios.post(
        'https://api.groq.com/openai/v1/chat/completions',
        {
          model: GROQ_MODEL,
          messages: messages,
          temperature: 0.7,
          max_tokens: 1024
        },
        {
          headers: {
            'Authorization': `Bearer ${GROQ_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );
    } else {
      response = await axios.post(
        'https://ai.hackclub.com/chat/completions',
        { messages },
        { headers: { 'Content-Type': 'application/json' } }
      );
    }

    const aiResponse = response.data.choices[0].message.content;
    
    gameState.gameHistory.push(
      { role: "user", content: userInput },
      { role: "assistant", content: aiResponse }
    );

    return aiResponse;

  } catch (error) {
    console.error(theme.alert("API Error:"), error.response?.data || error.message);
    return "The arcane connection wavers... (Temporary disturbance)";
  }
}
function updateGameState(response) {
  const damageMatch = response.match(/lose (\d+) health/i);
  if (damageMatch) {
    gameState.playerHealth = Math.max(0, gameState.playerHealth - parseInt(damageMatch[1]));
  }
  const locations = ["forest", "castle", "dungeon", "village", "cave"];
  locations.forEach(loc => {
    if (response.toLowerCase().includes(loc)) {
      gameState.currentLocation = loc;
    }
  });

  if (response.includes("find") || response.includes("obtain")) {
    const items = ["sword", "potion", "key", "gold", "map"];
    items.forEach(item => {
      if (response.toLowerCase().includes(item)) {
        gameState.playerInventory.push(item);
      }
    });
  }
}

async function processAction(action) {
  gameState.turnCount++;
  
  console.log(theme.npc("\nThe Dungeon Master ponders your action..."));
  
  let response;
  try {
    response = await callGroqAPI(action);
    if (!response || response.trim() === "") {
      throw new Error("Empty response from API");
    }
  } catch (error) {
    response = "You feel a strange disturbance in the air... (The DM seems distracted)";
  }
  
  console.log(`\n${theme.npc(response)}`);
  updateGameState(response);
  
  return response;
}

function displayStatus() {
    
  }

async function startGame() {
  console.clear();
  console.log(theme.title(String.raw`
    _____     __  __     __   __     ______     ______     ______     __   __   
   /\  __-.  /\ \/\ \   /\ "-.\ \   /\  ___\   /\  ___\   /\  __ \   /\ "-.\ \  
   \ \ \/\ \ \ \ \_\ \  \ \ \-.  \  \ \ \__ \  \ \  __\   \ \ \/\ \  \ \ \-.  \ 
    \ \____-  \ \_____\  \ \_\\"\_\  \ \_____\  \ \_____\  \ \_____\  \ \_\\"\_\
     \/____/   \/_____/   \/_/ \/_/   \/_____/   \/_____/   \/_____/   \/_/ \/_/
                                                                                
    __    __     ______     ______     ______   ______     ______               
   /\ "-./  \   /\  __ \   /\  ___\   /\__  _\ /\  ___\   /\  == \              
   \ \ \-./\ \  \ \  __ \  \ \___  \  \/_/\ \/ \ \  __\   \ \  __<              
    \ \_\ \ \_\  \ \_\ \_\  \/\_____\    \ \_\  \ \_____\  \ \_\ \_\            
     \/_/  \/_/   \/_/\/_/   \/_____/     \/_/   \/_____/   \/_/ /_/            
   `));
   
  gameState.playerName = await askQuestion(theme.input("\nEnter your character's name: "));
  console.log(theme.header("\nChoose class:"));
  console.log("1. Warrior  2. Wizard  3. Rogue  4. Bard");
  gameState.playerClass = ["Warrior", "Wizard", "Rogue", "Bard"][
    parseInt(await askQuestion(theme.input("Select (1-4): ")) - 1)
  ] || 'Adventurer';

  const opening = await processAction(
    `Create opening scene for ${gameState.playerClass} ${gameState.playerName} in a fantasy setting`
  );
  
  while (gameState.playerHealth > 0) {
    displayStatus();
    
    const action = await askQuestion(theme.input("\nWhat do you do? > "));
    
    if (action.toLowerCase() === 'quit') {
      console.log(theme.header("\nThanks for playing!"));
      process.exit();
    }
    
    if (action.toLowerCase() === 'help') {
      console.log(theme.header("\nAvailable commands:"));
      console.log("- move [direction]  - examine [object]");
      console.log("- use [item]        - attack [target]");
      console.log("- cast [spell]      - inventory");
      console.log("- quit              - help");
      continue;
    }
    
    await processAction(action);
  }
  
  console.log(theme.alert("\nGAME OVER - Your journey ends here..."));
  process.exit();
}

function askQuestion(prompt) {
  return new Promise(resolve => rl.question(prompt, resolve));
}


startGame().catch(err => {
  console.log(theme.alert("Fatal error:"), err);
  process.exit(1);
});
