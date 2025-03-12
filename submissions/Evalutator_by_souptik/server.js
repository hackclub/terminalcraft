const readline = require('readline');
const ChessValidator = require('./chess');

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const question = query => new Promise(resolve => rl.question(query, resolve));

let chess = null;

async function main() {
  while (true) {
    // Ask for input, which can be a FEN string, "move", "board", or "exit"
    const input = await question('Enter FEN position, "move", or "board" (or "exit" to quit): ');
    if (input.toLowerCase() === 'exit') break;
    
    if (input.toLowerCase() === 'move') {
      if (!chess) {
        console.log('No position loaded. Please enter a FEN first.');
        continue;
      }
      const move = await question('Enter move (in e2e4 format, or "exit" to quit): ');
      if (move.toLowerCase() === 'exit') break;
      if (move.length === 4) {
        try {
          chess.makeMove(move);
          console.log('Move done. New position:');
          chess.printBoard();
          console.log('New FEN:', chess.getFEN());
          console.log('Best move:', chess.getBestMove());
        } catch (e) {
          console.log('Invalid move');
          continue;
        }
      } else {
        console.log('Invalid move format. Use e2e4 format.');
      }
      continue;
    }
    
    if (input.toLowerCase() === 'board') {
      if (!chess) {
        console.log('No position loaded. Please enter a FEN first.');
        continue;
      }
      chess.printBoard();
      console.log('Current FEN:', chess.getFEN());
      console.log('Best move:', chess.getBestMove());
      continue;
    }
    
    // If the input is not "move", "board", or "exit", assume it is a FEN string.
    try {
      chess = new ChessValidator(input);
    } catch (e) {
      console.log('Invalid FEN');
      continue;
    }
    console.log('Current position:');
    chess.printBoard();
    console.log('Best move:', chess.getBestMove());
  }
  rl.close();
}

main();
