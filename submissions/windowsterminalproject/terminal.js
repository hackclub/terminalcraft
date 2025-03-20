const readline = require('readline');
const chalk = require('chalk');

let inGame = false;
let currency = 100;
let animalsCaught = [];
let waitingForBet = false;
let currentGame = "";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log(chalk.green("Welcome to Windows Terminal by Stevens Antony!"));
console.log(chalk.green("Type 'help' to get a list of commands."));

function prompt() {
  if (inGame) {
    rl.question(`Game> `, handleGameCommand);
  } else {
    rl.question(`C:\\User\\> `, executeCommand);
  }
}

// COMMAND HANDLING
function executeCommand(command) {
  switch (command.toLowerCase()) {
    case 'help':
      console.log(chalk.green("Available commands:"));
      console.log(chalk.green("help - Shows all the list of commands"));
      console.log(chalk.green("clear - Clears the terminal"));
      console.log(chalk.green("owo - Starts the OwO game"));
      console.log(chalk.green("exit - Closes the terminal"));
      break;
    case 'clear':
      console.clear();
      break;
    case 'owo':
      startGame();
      return;
    case 'exit':
      exitAnimation();
      return;
    default:
      console.log(chalk.red(`Command not found: ${command}`));
  }
  prompt();
}

// GAME FUNCTIONS
function startGame() {
  inGame = true;
  currency = 100;
  animalsCaught = [];
  console.log(chalk.green("Welcome to the OwO Game!"));
  console.log("Type 'hunt', 'sell', 'balance', 'crates', 'blackjack', 'slots', 'coinflip', or 'stop' to quit.");
  prompt();
}

function handleGameCommand(command) {
  if (waitingForBet) {
    handleBetInput(command);
    return;
  }

  switch (command.toLowerCase()) {
    case 'hunt':
      let animal = "Cute Animal " + (animalsCaught.length + 1);
      animalsCaught.push(animal);
      console.log(chalk.green(`You caught a ${animal}!`));
      break;
    case 'sell':
      if (animalsCaught.length > 0) {
        let animal = animalsCaught.pop();
        currency += 10;
        console.log(chalk.green(`You sold ${animal} for 10 coins. Balance: ${currency} coins.`));
      } else {
        console.log(chalk.red("No animals to sell!"));
      }
      break;
    case 'balance':
      console.log(chalk.green(`Your current balance: ${currency} coins.`));
      break;
    case 'crates':
      findCrate();
      return;
    case 'blackjack':
      currentGame = "blackjack";
      waitingForBet = true;
      console.log("Enter your bet for Blackjack:");
      break;
    case 'slots':
      currentGame = "slots";
      waitingForBet = true;
      console.log("Enter your bet for Slots:");
      break;
    case 'coinflip':
      currentGame = "coinflip";
      waitingForBet = true;
      console.log("Choose 'heads' or 'tails' followed by bet (e.g., 'heads 10'):");
      break;
    case 'stop':
      console.log(chalk.green("You left the OwO game."));
      inGame = false;
      break;
    default:
      console.log(chalk.red("Invalid action!"));
  }
  prompt();
}

function handleBetInput(input) {
  if (currentGame === "blackjack" || currentGame === "slots") {
    let bet = parseInt(input);
    if (isNaN(bet) || bet <= 0 || bet > currency) {
      console.log(chalk.red(`Invalid bet amount. Enter number between 1 and ${currency}.`));
    } else {
      if (currentGame === "blackjack") startBlackjack(bet);
      else startSlots(bet);
      waitingForBet = false;
    }
  } else if (currentGame === "coinflip") {
    let parts = input.split(" ");
    if (parts.length !== 2) {
      console.log(chalk.red("Invalid format. Use: 'heads 10' or 'tails 20'"));
    } else {
      let choice = parts[0].toLowerCase();
      let bet = parseInt(parts[1]);
      if (!["heads", "tails"].includes(choice)) {
        console.log(chalk.red("Invalid choice. Use 'heads' or 'tails'."));
      } else if (isNaN(bet) || bet <= 0 || bet > currency) {
        console.log(chalk.red(`Invalid bet amount. Enter number between 1 and ${currency}.`));
      } else {
        startCoinflip(choice, bet);
        waitingForBet = false;
      }
    }
  }
  prompt();
}

function findCrate() {
  const crateItems = ["coin", "gem", "boost"];
  const itemFound = crateItems[Math.floor(Math.random() * crateItems.length)];
  switch (itemFound) {
    case "coin":
      currency += 20;
      console.log(chalk.green("You found a crate with coins! +20 coins."));
      break;
    case "gem":
      currency += 50;
      console.log(chalk.green("You found a crate with a gem! +50 coins."));
      break;
    case "boost":
      console.log(chalk.green("You found a crate with a boost! Next game will be lucky!"));
      break;
  }
  console.log(`Balance: ${currency} coins.`);
  prompt();
}

function startBlackjack(bet) {
  const playerCard1 = Math.floor(Math.random() * 10) + 1;
  const playerCard2 = Math.floor(Math.random() * 10) + 1;
  const dealerCard1 = Math.floor(Math.random() * 10) + 1;
  const dealerCard2 = Math.floor(Math.random() * 10) + 1;

  const playerTotal = playerCard1 + playerCard2;
  const dealerTotal = dealerCard1 + dealerCard2;

  console.log(`Your cards: ${playerCard1}, ${playerCard2} (Total: ${playerTotal})`);
  console.log(`Dealer's cards: ${dealerCard1}, ${dealerCard2} (Total: ${dealerTotal})`);

  if (playerTotal > dealerTotal || dealerTotal > 21) {
    currency += bet;
    console.log(chalk.green(`You win ${bet} coins!`));
  } else if (playerTotal === dealerTotal) {
    console.log(chalk.yellow(`It's a draw! No coins won or lost.`));
  } else {
    currency -= bet;
    console.log(chalk.red(`You lose ${bet} coins.`));
  }
  console.log(`Balance: ${currency} coins.`);
  prompt();
}

function startSlots(bet) {
  const symbols = ["🗿", "🪦", "💵", "☠️", "💩", "😂"];
  const slot1 = symbols[Math.floor(Math.random() * symbols.length)];
  const slot2 = symbols[Math.floor(Math.random() * symbols.length)];
  const slot3 = symbols[Math.floor(Math.random() * symbols.length)];

  console.log(`[${slot1}] [${slot2}] [${slot3}]`);

  if (slot1 === slot2 && slot2 === slot3) {
    const winnings = bet * 5;
    currency += winnings;
    console.log(chalk.green(`JACKPOT! You win ${winnings} coins!`));
  } else if (slot1 === slot2 || slot2 === slot3 || slot1 === slot3) {
    const winnings = bet * 2;
    currency += winnings;
    console.log(chalk.green(`Two matching symbols! You win ${winnings} coins!`));
  } else {
    currency -= bet;
    console.log(chalk.red(`No matches! You lose ${bet} coins.`));
  }
  console.log(`Balance: ${currency} coins.`);
  prompt();
}

function startCoinflip(choice, bet) {
  const result = Math.random() < 0.5 ? "heads" : "tails";
  console.log(`Coin flip result: ${result.toUpperCase()}`);

  if (choice === result) {
    currency += bet;
    console.log(chalk.green(`You win ${bet} coins!`));
  } else {
    currency -= bet;
    console.log(chalk.red(`You lose ${bet} coins.`));
  }
  console.log(`Balance: ${currency} coins.`);
  prompt();
}

function exitAnimation() {
  console.log(chalk.green("Logging out... Totally not sending your search history to FBI 👀"));
  console.log(chalk.green("Just kidding!... Or am I? 🤡"));
  setTimeout(() => {
    process.exit(0);
  }, 3000);
}

prompt();