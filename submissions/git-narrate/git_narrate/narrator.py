import json
import os
from typing import Dict, Any, List
import requests
from .utils import format_date, clean_commit_message
from dotenv import load_dotenv

class RepoNarrator:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key.strip() == "":
            self.api_key = None

    def generate_story(self) -> str:
        """Generate an AI-powered narrative of the repository's development."""
        if not self.api_key:
            return "An OpenAI API key is required to generate a story. Please set the OPENAI_API_KEY environment variable."

        # Step 1: Structure the story into chapters with detailed beats
        chapters = self._structure_chapters()
        if not chapters:
            return "Could not generate a story from the repository history."

        # Step 2: Get a thematic summary for each chapter from the AI
        chapter_summaries = []
        for chapter in chapters:
            summary = self._get_chapter_summary(chapter)
            if "Error" in summary:
                return summary # Propagate error
            chapter_summaries.append(f"## {chapter['title']}\n{summary}")

        # Step 3: Weave the chapter summaries into a final, cohesive narrative
        return self._weave_final_story(chapter_summaries)

    def _structure_chapters(self) -> List[Dict[str, Any]]:
        """Group commits into chapters."""
        commits = sorted(self.repo_data["commits"], key=lambda c: c["date"])
        if not commits:
            return []

        num_commits = len(commits)
        chapter_size = max(1, num_commits // 4)
        
        chapters = [
            {"title": "The Dawn of the Project", "commits": commits[0:chapter_size]},
            {"title": "Building the Foundation", "commits": commits[chapter_size:2*chapter_size]},
            {"title": "Trials and Triumphs", "commits": commits[2*chapter_size:3*chapter_size]},
            {"title": "The Horizon Beyond", "commits": commits[3*chapter_size:]}
        ]
        
        return [c for c in chapters if c["commits"]]

    def _get_chapter_summary(self, chapter: Dict[str, Any]) -> str:
        """Use AI to generate a thematic summary for a single chapter."""
        
        # Sanitize and limit data for the prompt
        commits_json = self._get_limited_json(chapter["commits"])

        prompt = f"""
You are a technical writer. Your task is to write a short, thematic summary of the following list of git commits. This is one chapter in a larger story. Focus on the main events and the overall theme of this period.

Chapter Title: {chapter['title']}
Commit Data:
```json
{commits_json}
```

Based on the data, write a concise summary of this chapter in the project's history.
"""
        return self._call_ai(prompt, 500)

    def _weave_final_story(self, chapter_summaries: List[str]) -> str:
        """Use AI to weave chapter summaries into a final narrative."""
        
        full_summary = "\n\n".join(chapter_summaries)

        prompt = f"""
You are a master storyteller. I have a series of chapter summaries from a project's history. Your task is to weave them into a single, cohesive, and engaging narrative. Smooth out the transitions between chapters and give the story a consistent, compelling voice.

Here are the chapter summaries:
---
{full_summary}
---

Now, write the final, complete story of the project.
"""
        return self._call_ai(prompt, 3000)

    def _get_limited_json(self, commits: List[Dict[str, Any]]) -> str:
        """Create a JSON string from commits, limited by character count."""
        sampled_commits = []
        total_chars = 0
        max_chars = 75000  # A safe limit for each chapter's data

        for commit in commits:
            # A simplified representation for the chapter summary prompt
            simplified_commit = {
                "author": commit["author"],
                "message": commit["message"],
                "category": commit["category"],
                "files_changed": len(commit["file_contents"]),
                "insertions": commit["insertions"],
                "deletions": commit["deletions"]
            }
            commit_str = json.dumps(simplified_commit, default=str)
            if total_chars + len(commit_str) > max_chars:
                break
            sampled_commits.append(simplified_commit)
            total_chars += len(commit_str)
        
        return json.dumps(sampled_commits, indent=2, default=str)

    def _call_ai(self, prompt: str, max_tokens: int) -> str:
        """A helper function to call the AI API."""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            payload = {
                "model": "glm-4.5-flash",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": max_tokens,
            }
            
            response = requests.post(
                "https://api.z.ai/api/paas/v4/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: An error occurred while communicating with the AI: {str(e)}"
