# TerminalCraft Website

A terminal-styled webiste showcasing amazing CLI applications built for Terminal Craft.

## Environment Setup

### GitHub API Token

To avoid rate limiting when loading projects, you'll need a GitHub Personal Access Token:

1. Create a `.env.local` file in the project root
2. Add your GitHub token:
   ```
   NEXT_PUBLIC_GITHUB_TOKEN=your_github_token_here
   ```

**Security Notes:**
- The `.env.local` file is automatically ignored by Git
- Never commit tokens to version control
- Use tokens with minimal required permissions (public repository read access)

### Rate Limits

- **Without token**: 60 requests/hour per IP
- **With token**: 5,000 requests/hour

## Getting Started

First, install dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the gallery.

## Features

- 🚀 **Live Demo Integration**: Launch projects directly in browser
- 📊 **Real-time Loading**: Fetches projects from GitHub submissions folder
- 🎨 **Terminal UI**: Authentic terminal styling throughout
- 💻 **Language Detection**: Automatically detects programming languages
- 📱 **Responsive Design**: Works on all device sizes
- 🔄 **Toast Notifications**: Real-time feedback for project launches

## Project Structure

- `app/page.tsx` - Main terminal interface
- `app/gallery/page.tsx` - Project gallery with GitHub integration
- `components/Navbar.tsx` - Terminal-styled navigation
- `components/Prompt.tsx` - Terminal prompt component

## API Integration

The gallery integrates with:
- **GitHub API**: Loads projects from hackclub/terminalcraft/submissions
- **TerminalCraft Deploy API**: Launches live demos at terminalcraft.josiasw.dev

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
