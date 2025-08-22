class ChessValidator {
    constructor(fen) {
      this.board = Array(8).fill().map(() => Array(8).fill(0));
      this.castlingRights = Array(4).fill(false);
      this.parseFEN(fen);
    }
    parseFEN(fen) {
      const parts = fen.split(' ');
      const position = parts[0];
      let rank = 0;
      let file = 0;
      for (const c of position) {
        if (c === '/') { rank++; file = 0; }
        else if (!isNaN(c)) { file += parseInt(c); }
        else { this.board[rank][file] = c; file++; }
      }
      this.whiteToMove = parts[1] === 'w';
      if (parts[2] !== '-') {
        for (const c of parts[2]) {
          switch (c) {
            case 'K': this.castlingRights[0] = true; break;
            case 'Q': this.castlingRights[1] = true; break;
            case 'k': this.castlingRights[2] = true; break;
            case 'q': this.castlingRights[3] = true; break;
          }
        }
      }
      if (parts[3] !== '-') {
        this.enPassantSquare = [
          '8'.charCodeAt(0) - parts[3].charAt(1).charCodeAt(0),
          parts[3].charCodeAt(0) - 'a'.charCodeAt(0)
        ];
      } else { this.enPassantSquare = null; }
      this.halfMoveClock = parseInt(parts[4]);
      this.fullMoveNumber = parseInt(parts[5]);
    }
    getBoard() { return this.board.map(row => [...row]); }
    makeMove(move) {
      const startFile = move.charCodeAt(0) - 'a'.charCodeAt(0);
      const startRank = '8'.charCodeAt(0) - move.charCodeAt(1);
      const endFile = move.charCodeAt(2) - 'a'.charCodeAt(0);
      const endRank = '8'.charCodeAt(0) - move.charCodeAt(3);
      const piece = this.board[startRank][startFile];
      const capturedPiece = this.board[endRank][endFile];
      if (piece.toLowerCase() === 'p' || capturedPiece !== 0) { this.halfMoveClock = 0; } else { this.halfMoveClock++; }
      if (piece.toLowerCase() === 'p' &&
          this.enPassantSquare &&
          endFile === this.enPassantSquare[1] &&
          endRank === this.enPassantSquare[0])
        { this.board[startRank][endFile] = 0; }
      if (piece.toLowerCase() === 'k' && Math.abs(endFile - startFile) === 2) {
        const rookStartFile = endFile > startFile ? 7 : 0;
        const rookEndFile = endFile > startFile ? endFile - 1 : endFile + 1;
        const rook = this.board[startRank][rookStartFile];
        this.board[startRank][rookStartFile] = 0;
        this.board[startRank][rookEndFile] = rook;
      }
      this.updateCastlingRights(startRank, startFile, endRank, endFile);
      this.board[endRank][endFile] = piece;
      this.board[startRank][startFile] = 0;
      if (piece.toLowerCase() === 'p' && Math.abs(startRank - endRank) === 2) { this.enPassantSquare = [(startRank + endRank) / 2, startFile]; }
      else { this.enPassantSquare = null; }
      if (!this.whiteToMove) { this.fullMoveNumber++; }
      this.whiteToMove = !this.whiteToMove;
    }
    updateCastlingRights(startRank, startFile, endRank, endFile) {
      if (this.board[startRank][startFile] === 'K') { this.castlingRights[0] = false; this.castlingRights[1] = false; }
      else if (this.board[startRank][startFile] === 'k') { this.castlingRights[2] = false; this.castlingRights[3] = false; }
      if (startRank === 0 && startFile === 0) this.castlingRights[3] = false;
      if (startRank === 0 && startFile === 7) this.castlingRights[2] = false;
      if (startRank === 7 && startFile === 0) this.castlingRights[1] = false;
      if (startRank === 7 && startFile === 7) this.castlingRights[0] = false;
      if (endRank === 0 && endFile === 0) this.castlingRights[3] = false;
      if (endRank === 0 && endFile === 7) this.castlingRights[2] = false;
      if (endRank === 7 && endFile === 0) this.castlingRights[1] = false;
      if (endRank === 7 && endFile === 7) this.castlingRights[0] = false;
    }
    getFEN() {
      let fen = '';
      for (let rank = 0; rank < 8; rank++) {
        let emptyCount = 0;
        for (let file = 0; file < 8; file++) {
          if (this.board[rank][file] === 0) { emptyCount++; }
          else {
            if (emptyCount > 0) { fen += emptyCount; emptyCount = 0; }
            fen += this.board[rank][file];
          }
        }
        if (emptyCount > 0) { fen += emptyCount; }
        if (rank < 7) { fen += '/'; }
      }
      fen += ' ' + (this.whiteToMove ? 'w' : 'b');
      fen += ' ';
      let hasCastling = false;
      if (this.castlingRights[0]) { fen += 'K'; hasCastling = true; }
      if (this.castlingRights[1]) { fen += 'Q'; hasCastling = true; }
      if (this.castlingRights[2]) { fen += 'k'; hasCastling = true; }
      if (this.castlingRights[3]) { fen += 'q'; hasCastling = true; }
      if (!hasCastling) { fen += '-'; }
      fen += ' ';
      if (this.enPassantSquare !== null) {
        fen += String.fromCharCode('a'.charCodeAt(0) + this.enPassantSquare[1]);
        fen += String.fromCharCode('8'.charCodeAt(0) - this.enPassantSquare[0]);
      } else { fen += '-'; }
      fen += ' ' + this.halfMoveClock;
      fen += ' ' + this.fullMoveNumber;
      return fen;
    }
    printBoard() {
      console.log('  a b c d e f g h');
      for (let rank = 0; rank < 8; rank++) {
        process.stdout.write(`${8 - rank} `);
        for (let file = 0; file < 8; file++) {
          const piece = this.board[rank][file];
          process.stdout.write(`${piece === 0 ? '.' : piece} `);
        }
        console.log(8 - rank);
      }
      console.log('  a b c d e f g h');
      console.log(`Current turn: ${this.whiteToMove ? 'White' : 'Black'}`);
    }
    algebraic(r, c) { return String.fromCharCode(97 + c) + (8 - r).toString(); }
    generateMoves() {
      let moves = [];
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
          let piece = this.board[r][c];
          if (piece === 0) continue;
          let isWhitePiece = piece === piece.toUpperCase();
          if (this.whiteToMove !== isWhitePiece) continue;
          switch (piece.toLowerCase()) {
            case 'p': this.generatePawnMoves(r, c, moves); break;
            case 'n': this.generateKnightMoves(r, c, moves); break;
            case 'b': this.generateSlidingMoves(r, c, moves, [[-1, -1], [-1, 1], [1, -1], [1, 1]]); break;
            case 'r': this.generateSlidingMoves(r, c, moves, [[0, 1], [0, -1], [1, 0], [-1, 0]]); break;
            case 'q': this.generateSlidingMoves(r, c, moves, [[-1, -1], [-1, 1], [1, -1], [1, 1], [0, 1], [0, -1], [1, 0], [-1, 0]]); break;
            case 'k': this.generateKingMoves(r, c, moves); break;
          }
        }
      }
      let legal = [];
      for (let m of moves) {
        let copy = this.clone();
        try { copy.makeMove(m); } catch (e) { continue; }
        if (!copy.isKingInCheck(this.whiteToMove ? 'w' : 'b')) legal.push(m);
      }
      return legal;
    }
    generatePawnMoves(r, c, moves) {
      let piece = this.board[r][c];
      let dir = piece === 'P' ? -1 : 1;
      let start = piece === 'P' ? 6 : 1;
      let r1 = r + dir;
      if (r1 >= 0 && r1 < 8 && this.board[r1][c] === 0) {
        moves.push(this.algebraic(r, c) + this.algebraic(r1, c));
        if (r === start && this.board[r1 + dir][c] === 0) moves.push(this.algebraic(r, c) + this.algebraic(r1 + dir, c));
      }
      for (let dc of [-1, 1]) {
        let nc = c + dc;
        if (nc < 0 || nc > 7) continue;
        if (r1 >= 0 && r1 < 8) {
          if (this.board[r1][nc] !== 0) {
            let target = this.board[r1][nc];
            if ((piece === 'P' && target === target.toLowerCase()) || (piece === 'p' && target === target.toUpperCase()))
              moves.push(this.algebraic(r, c) + this.algebraic(r1, nc));
          } else if (this.enPassantSquare && this.enPassantSquare[0] === r1 && this.enPassantSquare[1] === nc)
            moves.push(this.algebraic(r, c) + this.algebraic(r1, nc));
        }
      }
    }
    generateKnightMoves(r, c, moves) {
      let piece = this.board[r][c];
      let offs = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]];
      for (let off of offs) {
        let nr = r + off[0], nc = c + off[1];
        if (nr < 0 || nr > 7 || nc < 0 || nc > 7) continue;
        let target = this.board[nr][nc];
        if (target === 0 || (piece === piece.toUpperCase() ? target === target.toLowerCase() : target === target.toUpperCase()))
          moves.push(this.algebraic(r, c) + this.algebraic(nr, nc));
      }
    }
    generateSlidingMoves(r, c, moves, dirs) {
      let piece = this.board[r][c];
      for (let d of dirs) {
        let nr = r, nc = c;
        while (true) {
          nr += d[0];
          nc += d[1];
          if (nr < 0 || nr > 7 || nc < 0 || nc > 7) break;
          let target = this.board[nr][nc];
          if (target === 0) { moves.push(this.algebraic(r, c) + this.algebraic(nr, nc)); }
          else {
            if ((piece === piece.toUpperCase() ? target === target.toLowerCase() : target === target.toUpperCase()))
              moves.push(this.algebraic(r, c) + this.algebraic(nr, nc));
            break;
          }
        }
      }
    }
    generateKingMoves(r, c, moves) {
      let piece = this.board[r][c];
      for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
          if (dr === 0 && dc === 0) continue;
          let nr = r + dr, nc = c + dc;
          if (nr < 0 || nr > 7 || nc < 0 || nc > 7) continue;
          let target = this.board[nr][nc];
          if (target === 0 || (piece === piece.toUpperCase() ? target === target.toLowerCase() : target === target.toUpperCase()))
            moves.push(this.algebraic(r, c) + this.algebraic(nr, nc));
        }
      }
      if (piece === 'K' && r === 7 && c === 4) {
        if (this.castlingRights[0] && this.board[7][5] === 0 && this.board[7][6] === 0)
          moves.push("e1g1");
        if (this.castlingRights[1] && this.board[7][3] === 0 && this.board[7][2] === 0 && this.board[7][1] === 0)
          moves.push("e1c1");
      }
      if (piece === 'k' && r === 0 && c === 4) {
        if (this.castlingRights[2] && this.board[0][5] === 0 && this.board[0][6] === 0)
          moves.push("e8g8");
        if (this.castlingRights[3] && this.board[0][3] === 0 && this.board[0][2] === 0 && this.board[0][1] === 0)
          moves.push("e8c8");
      }
    }
    isSquareAttacked(r, c, attackerColor) {
      let dirs = [[-1, -1], [-1, 1], [1, -1], [1, 1], [0, 1], [0, -1], [1, 0], [-1, 0]];
      for (let d of dirs) {
        let nr = r, nc = c;
        while (true) {
          nr += d[0];
          nc += d[1];
          if (nr < 0 || nr > 7 || nc < 0 || nc > 7) break;
          let piece = this.board[nr][nc];
          if (piece !== 0) {
            if ((attackerColor === 'w' && piece === piece.toUpperCase()) || (attackerColor === 'b' && piece === piece.toLowerCase())) {
              let p = piece.toLowerCase();
              if ((d[0] === 0 || d[1] === 0) && (p === 'r' || p === 'q')) return true;
              if (d[0] !== 0 && d[1] !== 0 && (p === 'b' || p === 'q')) return true;
              break;
            } else break;
          }
        }
      }
      let knights = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]];
      for (let off of knights) {
        let nr = r + off[0], nc = c + off[1];
        if (nr < 0 || nr > 7 || nc < 0 || nc > 7) continue;
        let piece = this.board[nr][nc];
        if (piece !== 0 && ((attackerColor === 'w' && piece === 'N') || (attackerColor === 'b' && piece === 'n')))
          return true;
      }
      if (attackerColor === 'w') {
        if (r - 1 >= 0 && c - 1 >= 0) { let piece = this.board[r - 1][c - 1]; if (piece === 'P') return true; }
        if (r - 1 >= 0 && c + 1 <= 7) { let piece = this.board[r - 1][c + 1]; if (piece === 'P') return true; }
      } else {
        if (r + 1 <= 7 && c - 1 >= 0) { let piece = this.board[r + 1][c - 1]; if (piece === 'p') return true; }
        if (r + 1 <= 7 && c + 1 <= 7) { let piece = this.board[r + 1][c + 1]; if (piece === 'p') return true; }
      }
      for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
          if (dr === 0 && dc === 0) continue;
          let nr = r + dr, nc = c + dc;
          if (nr < 0 || nr > 7 || nc < 0 || nc > 7) continue;
          let piece = this.board[nr][nc];
          if (piece !== 0 && ((attackerColor === 'w' && piece === 'K') || (attackerColor === 'b' && piece === 'k')))
            return true;
        }
      }
      return false;
    }
    isKingInCheck(color) {
      let kingPos = null;
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
          let piece = this.board[r][c];
          if (piece !== 0 && ((color === 'w' && piece === 'K') || (color === 'b' && piece === 'k'))) { kingPos = [r, c]; break; }
        }
        if (kingPos) break;
      }
      if (!kingPos) return true;
      return this.isSquareAttacked(kingPos[0], kingPos[1], color === 'w' ? 'b' : 'w');
    }
    clone() { return new ChessValidator(this.getFEN()); }
    evaluate() {
      let vals = { p: 100, n: 320, b: 330, r: 500, q: 900, k: 20000 };
      let score = 0;
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
          let piece = this.board[r][c];
          if (piece !== 0) {
            let val = vals[piece.toLowerCase()];
            score += piece === piece.toUpperCase() ? val : -val;
          }
        }
      }
      return score;
    }
    minimax(depth, alpha, beta, maximizing) {
      if (depth === 0) return this.evaluate();
      let moves = this.generateMoves();
      if (moves.length === 0) return this.evaluate();
      if (maximizing) {
        let maxevaluation = -Infinity;
        for (let m of moves) {
          let copy = this.clone();
          try { copy.makeMove(m); } catch (e) { continue; }
          let evaluation = copy.minimax(depth - 1, alpha, beta, false);
          maxevaluation = Math.max(maxevaluation, evaluation);
          alpha = Math.max(alpha, evaluation);
          if (beta <= alpha) break;
        }
        return maxevaluation;
      } else {
        let minevaluation = Infinity;
        for (let m of moves) {
          let copy = this.clone();
          try { copy.makeMove(m); } catch (e) { continue; }
          let evaluation = copy.minimax(depth - 1, alpha, beta, true);
          minevaluation = Math.min(minevaluation, evaluation);
          beta = Math.min(beta, evaluation);
          if (beta <= alpha) break;
        }
        return minevaluation;
      }
    }
    getBestMove() {
      let moves = this.generateMoves();
      if (moves.length === 0) return 'none';
      let bestMove = moves[0];
      let bestEval = this.whiteToMove ? -Infinity : Infinity;
      for (let m of moves) {
        let copy = this.clone();
        try { copy.makeMove(m); } catch (e) { continue; }
        let evaluation = copy.minimax(3, -Infinity, Infinity, !this.whiteToMove);
        if (this.whiteToMove && evaluation > bestEval) { bestEval = evaluation; bestMove = m; }
        if (!this.whiteToMove && evaluation < bestEval) { bestEval = evaluation; bestMove = m; }
      }
      return bestMove;
    }
  }
  module.exports = ChessValidator;
  