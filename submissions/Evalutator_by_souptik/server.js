const readline = require('readline');
const ChessValidator = require('./chess');

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const question = query => new Promise(resolve => rl.question(query, resolve));
let chess = null;

async function main() {
  while (true) {
    if (!chess) {
      const fen = await question('Enter FEN position (or "exit" to quit): ');
      if (fen.toLowerCase() === 'exit') break;
      try { chess = new ChessValidator(fen); } catch (e) { console.log('Invalid FEN'); continue; }
      console.log('Current position:');
      chess.printBoard();
      console.log('Best move:', chess.getBestMove());
    }
    const input = await question('Enter move, or "fen" to input new position, "board" to show current board, or "exit": ');
    if (input.toLowerCase() === 'exit') break;
    if (input.toLowerCase() === 'fen') { chess = null; continue; }
    if (input.toLowerCase() === 'board') {
      chess.printBoard();
      console.log('Current FEN:', chess.getFEN());
      console.log('Best move:', chess.getBestMove());
      continue;
    }
    if (input.length === 4) {
      try { chess.makeMove(input); } catch (e) { console.log('Invalid move'); continue; }
      console.log('Move done. New position:');
      chess.printBoard();
      console.log('New FEN:', chess.getFEN());
      console.log('Best move:', chess.getBestMove());
    } else {
      console.log('Invalid move format. Use e2e4 format.');
    }
  }
  rl.close();
}

main();
