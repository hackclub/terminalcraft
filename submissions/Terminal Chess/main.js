function isGameOver(chess) {
    const turn = chess.turn();
    if (chess.in_check() && chess.moves().length === 0) {
        return { over: true, reason: "Checkmate" };
    }
    if (!chess.in_check() && chess.moves().length === 0) {
        return { over: true, reason: "Stalemate" };
    }
    if (chess.insufficient_material()) {
        return { over: true, reason: "Draw by Insufficient Material" };
    }
    if (chess.half_moves >= 100) { 
        return { over: true, reason: "Draw by 50-Move Rule" };
    }
    if (chess.in_threefold_repetition()) {
        return { over: true, reason: "Draw by Threefold Repetition" };
    }
    return { over: false };
}

import { Chess } from "chess.js";

import { Select, Input } from "https://deno.land/x/cliffy@v0.25.7/prompt/mod.ts";

const menu = `
Engines List:
    1. My Random Chess Engine (Random but valid moves)
    2. SamannoyB Chess Engine (Deepthink engine ELO=1300)
    3. Stockfish (ELO=3000, not adjustable single depth)
(1,2,3 to choose) Enter your desired engine: `;

const option = await Select.prompt({
    message: menu,
    options: ["1", "2", "3"]
});

switch (option) {
    case "1":
        randomEngine();
        break;
    case "2":
        samannoybEngine();
        break;
    case "3":
        stockfish();
        break;
}

async function randomEngine() {
    console.log("Welcome to Random Engine! Let's play random.......Lol \nInitializing the dumbest engine ever......");
    console.log("You play as White!");
    const chess = new Chess();
   
    function asciiFunc() {
        var ascii = chess.ascii();
        var output = "";
    
        for ( let char of ascii ) {
            if (char == "R") {
                output += "♖";
            } else if (char == "K") {
                output += "♔";
            } else if (char == "Q") {
                output += "♕";
            } else if (char == "B") {
                output += "♗";
            } else if (char == "N") {
                output += "♘";
            } else if (char == "P") {
                output += "♙";
            } else if (char == "p") {
                output += "♟";
            } else if (char == "k") {
                output += "♚";
            } else if (char == "q") {
                output += "♛";
            } else if (char == "b") {
                output += "♝";
                continue;
            } else if (char == "n") {
                output += "♞";
            } else if (char == "r") {
                output += "♜";
            } else output += char;
        }
        return output;
    }
    console.log("This is the starting position!");
    console.log(asciiFunc());

    while (!chess.isGameOver()) {
        const move = await Input.prompt("Make a move (ex: e4, d4, Nc3, etc.):");
        chess.move(move);
        console.log(asciiFunc());
        if (chess.isGameOver()) {
            if (chess.isCheckmate()) {
                console.log("Checkmate! Run this program again to play a new game.");
            } else if (chess.isDraw()) {
                console.log("Draw! Run this program again to play a new game");
            }
            break;
        } 
        console.log("Black's Turn!");
        console.log("Thinking.....");
        await new Promise(resolve => setTimeout(resolve, 3000));
        const randomMove = chess.moves()[Math.floor(Math.random() * chess.moves().length)];
        chess.move(randomMove);
        console.log(asciiFunc());
    }
}

async function samannoybEngine() {
    console.log("Welcome to SamannoyB's Engine! Let's play cool.......Lol \nInitializing the most intermediate engine ever......");
    console.log("You play as White!");
    const chess = new Chess();

   
    function asciiFunc() {
        var ascii = chess.ascii();
        var output = "";
    
        for ( let char of ascii ) {
            if (char == "R") {
                output += "♖";
            } else if (char == "K") {
                output += "♔";
            } else if (char == "Q") {
                output += "♕";
            } else if (char == "B") {
                output += "♗";
            } else if (char == "N") {
                output += "♘";
            } else if (char == "P") {
                output += "♙";
            } else if (char == "p") {
                output += "♟";
            } else if (char == "k") {
                output += "♚";
            } else if (char == "q") {
                output += "♛";
            } else if (char == "b") {
                output += "♝";
                continue;
            } else if (char == "n") {
                output += "♞";
            } else if (char == "r") {
                output += "♜";
            } else output += char;
        }
        return output;
    }
    console.log("This is the starting position!");
    console.log(asciiFunc());

    while (!chess.isGameOver()) {
        const move = await Input.prompt("Make a move (ex: e4, d4, Nc3, etc.):");
        chess.move(move);
        console.log(asciiFunc());
        if (chess.isGameOver()) {
            if (chess.isCheckmate()) {
                console.log("Checkmate! Run this program again to play a new game.");
            } else if (chess.isDraw()) {
                console.log("Draw! Run this program again to play a new game");
            }
            break;
        } 
        console.log("Black's Turn!");
        console.log("Thinking.....");
        await new Promise(resolve => setTimeout(resolve, 3000));
        const moved = bestMove();
        chess.move(moved);
        console.log(asciiFunc());
    }
    function evaluateBoard(fen) {
        let evaluation = 0;
        const pieceValues = {
            'p': -1, 'r': -5, 'n': -3, 'b': -3, 'q': -9, 'k': 0,
            'P': 1, 'R': 5, 'N': 3, 'B': 3, 'Q': 9, 'K': 0
        }    
        const boardState = fen.split(' ')[0];
        for (let square of boardState) {
            if (pieceValues.hasOwnProperty(square)) {
                evaluation += pieceValues[square];     
            }
        }
        return evaluation;
    } 
    
    function minimax(depth, isMaximizing) {
        if (depth === 0 || chess.isGameOver()) {
            return evaluateBoard(chess.fen());
        }
        let moves = chess.moves();
        if (isMaximizing) {
            let maxEval = -Infinity;
            for (let move of moves) {
                chess.move(move);
                let evall = minimax(depth - 1, false);
                chess.undo();
                maxEval = Math.max(maxEval, evall);
            }
            return maxEval;
        } else {
            let minEval = Infinity;
            for (let move of moves) {
                chess.move(move);
                let evall = minimax(depth - 1, true);
                chess.undo();
                minEval = Math.min(minEval, evall);
            }
            return minEval;
        }
    }
    
    function bestMove() {
        let bestEval = -Infinity;
        let moveToPlay = null;
        let moves = chess.moves();
        for (let move of moves) {
            chess.move(move);
            let evall = minimax(3, false);
            chess.undo();
            if (evall > bestEval) {
                bestEval = evall;
                moveToPlay = move;
            }
        }
        return moveToPlay;
    }    
}


async function stockfish() {
    console.log("Welcome to Stockfish! This is gonna be interesting!");
    console.log("You play as White!");
    const chess = new Chess();
   
    function asciiFunc() {
        var ascii = chess.ascii();
        var output = "";
    
        for ( let char of ascii ) {
            if (char == "R") {
                output += "♖";
            } else if (char == "K") {
                output += "♔";
            } else if (char == "Q") {
                output += "♕";
            } else if (char == "B") {
                output += "♗";
            } else if (char == "N") {
                output += "♘";
            } else if (char == "P") {
                output += "♙";
            } else if (char == "p") {
                output += "♟";
            } else if (char == "k") {
                output += "♚";
            } else if (char == "q") {
                output += "♛";
            } else if (char == "b") {
                output += "♝";
                continue;
            } else if (char == "n") {
                output += "♞";
            } else if (char == "r") {
                output += "♜";
            } else output += char;
        }
        return output;
    }
    console.log("This is the starting position!");
    console.log(asciiFunc());

    while (!chess.isGameOver()) {
        const move = await Input.prompt("Make a move (ex: e4, d4, Nc3, etc.):");
        chess.move(move);
        console.log(asciiFunc());
        if (chess.isGameOver()) {
            if (chess.isCheckmate()) {
                console.log("Checkmate! Run this program again to play a new game.");
            } else if (chess.isDraw()) {
                console.log("Draw! Run this program again to play a new game");
            }
            break;
        } 
        console.log("Black's Turn!");
        console.log("Thinking.....");
        await new Promise(resolve => setTimeout(resolve, 3000));
        const moved = await getBestMove(chess.fen());
        chess.move(moved);
        console.log(asciiFunc());
    }

    async function getBestMove(fen) {
        try {
            const url = `https://lichess.org/api/cloud-eval?fen=${encodeURIComponent(fen)}`;
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.pvs && data.pvs.length > 0) {
                return data.pvs[0].moves.split(" ")[0];
            }
            return null;
        } catch (error) {
            console.error("Error fetching best move:", error);
            return null;
        }
    }
}