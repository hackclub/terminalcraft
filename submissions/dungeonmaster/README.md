# Dungeon Master

Dungeon Master is a text-based RPG powered by AI, where you explore a fantasy world through interactive storytelling. This game dynamically generates events, updates the game state, and responds to player actions, making each adventure unique.


## Installation:

1. Install dependencies:
   ```sh
   npm install
   ```

2. Set up environment variables:
   - Create a `.env` file in the project root.
   - Add your Groq API key:
     ```sh
     GROQ_API_KEY=your_api_key_here
     ```

3. Start the game by running:
   ```sh
   node index.js
   ```

## Troubleshooting
- If you see `ERROR: Missing GROQ_API_KEY in .env`, ensure your `.env` file is correctly set up.
- Run `npm install` if dependencies are missing.
- If the API is unresponsive, check your internet connection and Groq API status.

