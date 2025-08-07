import json
import os
from typing import Dict, Any, List
from datetime import datetime
import requests
from .utils import format_date
from dotenv import load_dotenv

class AINarrator:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data
        
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Get API key from environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        # Validate API key
        if not self.api_key or self.api_key.strip() == "":
            self.api_key = None
    
    def generate_story(self) -> str:
        """Generate an AI-powered narrative of the repository's development."""
        # Check if API key is available
        if not self.api_key:
            return self._generate_fallback_story()
        
        # Prepare data for AI
        story_data = self._prepare_story_data()
        
        # Create prompt for AI
        prompt = self._create_prompt(story_data)
        
        # Generate story with AI
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept-Language": "en-US,en",
                "Authorization": f"Bearer {self.api_key}",
            }
            payload = {
                "model": "glm-4.5-flash",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional technical writer and storyteller. Your task is to transform raw git repository data into a clear, concise, and accurate narrative about the project's development journey. Focus on factual reporting of milestones, features, and contributions, presented in a professional and engaging manner, without resorting to overly fictional or 'fancy' language. The story should be easy to understand for a technical audience.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7, # Slightly lower temperature for more factual output
                "max_tokens": 1500,
            }
            
            response = requests.post(
                "https://api.z.ai/api/paas/v4/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to the AI service. Please check your internet connection."
        except requests.exceptions.Timeout:
            return "Error: The request to the AI service timed out. Please try again later."
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return "Error: Invalid API key. Please check your OPENAI_API_KEY."
            elif e.response.status_code == 429:
                return "Error: API rate limit exceeded. Please wait and try again."
            else:
                return f"Error: An HTTP error occurred: {e.response.status_code} {e.response.reason}"
        except KeyError:
            return "Error: Unexpected response format from AI API. The story could not be generated."
        except Exception as e:
            return f"An unexpected error occurred while generating the AI story: {str(e)}"
    
    def _generate_fallback_story(self) -> str:
        """Generate a fallback story when API key is not available."""
        story_data = self._prepare_story_data()
        
        # Create a basic story without AI
        story = f"# The Story of {story_data['project_name']}\n\n"
        story += f"{story_data['project_name']} is a {story_data['setting']} that began its journey on "
        
        if story_data["timeline"]:
            first_event = story_data["timeline"][0]
            story += f"{format_date(first_event['date'])} with an initial commit by {first_event['description'].split('when ')[-1].split(' made the')[0]}."
        else:
            story += "an unknown date."
        
        story += "\n\n## Development Journey\n\n"
        
        # Add timeline events
        if story_data["timeline"]:
            for event in story_data["timeline"]:
                story += f"### {event['event']}\n"
                story += f"{event['description']}\n\n"
        
        # Add contributors
        if story_data["characters"]:
            story += "## Key Contributors\n\n"
            for char in story_data["characters"]:
                story += f"### {char['name']}\n"
                story += f"{char['name']} served as a {char['role']} and was a {char['impact'].lower()} on the project. "
                story += f"They made {char['contributions']} contributions from {char['first_appearance']} to {char['last_appearance']}.\n\n"
        
        story += "## Note\n\n"
        story += "This story was generated without AI assistance due to missing API key configuration. "
        story += "For more detailed storytelling, please set the OPENAI_API_KEY environment variable.\n"
        
        return story
    
    def _prepare_story_data(self) -> Dict[str, Any]:
        """Prepare repository data for AI storytelling."""
        # Extract key story elements
        story_data = {
            "project_name": self.repo_data["repo_name"],
            "project_description": self._get_project_description_from_readme(),
            "timeline": [],
            "characters": [],
            "plot_points": [],
            "setting": self._get_project_context(),
            "readme_content": self.repo_data.get("readme_content", "")
        }
        
        # Create timeline of major events
        if self.repo_data["commits"]:
            first_commit = min(self.repo_data["commits"], key=lambda c: c["date"])
            story_data["timeline"].append(
                {
                    "date": first_commit["date"],
                    "event": "Project Inception",
                    "description": f"The project was born on {format_date(first_commit['date'])} when {first_commit['author']} made the first commit.",
                    "significance": "beginning",
                }
            )
        
        # Add releases as major plot points
        for tag in self.repo_data["tags"]:
            if tag.get("date"):
                story_data["timeline"].append(
                    {
                        "date": tag["date"],
                        "event": f"Release {tag['name']}",
                        "description": f"The team celebrated the release of {tag['name']}, marking a significant milestone.",
                        "significance": "milestone",
                    }
                )
        
        # Add major merges as turning points
        for commit in self.repo_data["commits"]:
            if commit["is_merge"] and any(
                keyword in commit["message"].lower()
                for keyword in ["merge", "feature", "release"]
            ):
                story_data["timeline"].append(
                    {
                        "date": commit["date"],
                        "event": "Major Integration",
                        "description": f"A significant merge occurred: {commit['message'].splitlines()[0]}",
                        "significance": "turning_point",
                    }
                )
        
        # Sort timeline by date
        story_data["timeline"] = sorted(story_data["timeline"], key=lambda x: x["date"])
        
        # Create character profiles for contributors
        for author, stats in self.repo_data["contributors"].items():
            role = self._infer_contributor_role(stats)
            story_data["characters"].append(
                {
                    "name": author,
                    "role": role,
                    "contributions": stats["commits"],
                    "first_appearance": format_date(stats["first_commit"]),
                    "last_appearance": format_date(stats["last_commit"]),
                    "impact": self._describe_impact(stats),
                }
            )
        
        # Extract plot points from commit messages
        story_data["plot_points"] = self._extract_plot_points()
        
        return story_data
    
    def _get_project_description_from_readme(self) -> str:
        """Extract a concise project description from README.md content."""
        readme = self.repo_data.get("readme_content", "")
        if not readme:
            return "A software project."
        
        # Try to find the first paragraph or a summary after the main heading
        lines = readme.split('\n')
        description_lines = []
        in_description_section = False
        
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("#"): # Skip headings
                continue
            if stripped_line:
                if not in_description_section:
                    in_description_section = True
                description_lines.append(stripped_line)
                if len(" ".join(description_lines).split()) > 50: # Limit description length
                    break
            elif in_description_section: # Stop at first empty line after content
                break
        
        return " ".join(description_lines).strip() or "A software project."
    
    def _get_project_context(self) -> str:
        """Infer project context from repository data, prioritizing README content."""
        readme = self.repo_data.get("readme_content", "").lower()
        commit_messages = [c["message"].lower() for c in self.repo_data["commits"]]
        
        # Prioritize README for context
        if "web application" in readme or "api" in readme or "server" in readme:
            return "web application"
        elif "machine learning" in readme or "ai model" in readme:
            return "machine learning project"
        elif "mobile application" in readme or "android" in readme or "ios" in readme:
            return "mobile application"
        elif "game development" in readme or "unity" in readme or "engine" in readme:
            return "game development"
        
        # Fallback to commit messages if README doesn't provide clear context
        if any(keyword in msg for msg in commit_messages for keyword in ["web", "api", "server"]):
            return "web application"
        elif any(keyword in msg for msg in commit_messages for keyword in ["ml", "ai", "model"]):
            return "machine learning project"
        elif any(keyword in msg for msg in commit_messages for keyword in ["mobile", "android", "ios"]):
            return "mobile application"
        elif any(keyword in msg for msg in commit_messages for keyword in ["game", "unity", "engine"]):
            return "game development"
        else:
            return "software project"
    
    def _infer_contributor_role(self, stats: Dict[str, Any]) -> str:
        """Infer the role of a contributor based on their activity."""
        commits = stats["commits"]
        insertions = stats["insertions"]
        deletions = stats["deletions"]
        
        if commits > 50:
            return "Lead Developer"
        elif commits > 20:
            return "Core Contributor"
        elif insertions > deletions * 2:
            return "Feature Developer"
        elif deletions > insertions:
            return "Code Refiner"
        else:
            return "Contributor"
    
    def _describe_impact(self, stats: Dict[str, Any]) -> str:
        """Describe the impact of a contributor."""
        commits = stats["commits"]
        total_commits = sum(
            c["commits"] for c in self.repo_data["contributors"].values()
        )
        percentage = (commits / total_commits) * 100
        
        if percentage > 40:
            return "Architect of the project"
        elif percentage > 20:
            return "Major driving force"
        elif percentage > 10:
            return "Significant contributor"
        else:
            return "Valued team member"
    
    def _extract_plot_points(self) -> List[Dict[str, Any]]:
        """Extract plot points from commit messages."""
        plot_points = []
        
        for commit in self.repo_data["commits"]:
            msg = commit["message"].lower()
            
            # Look for significant events
            if any(keyword in msg for keyword in ["initial", "begin", "start"]):
                plot_points.append(
                    {
                        "type": "beginning",
                        "description": f"The project began with {commit['message'].splitlines()[0]}",
                        "date": commit["date"],
                    }
                )
            elif any(keyword in msg for keyword in ["feat:", "add", "implement"]):
                plot_points.append(
                    {
                        "type": "development",
                        "description": f"A new feature was added: {commit['message'].splitlines()[0]}",
                        "date": commit["date"],
                    }
                )
            elif any(keyword in msg for keyword in ["fix:", "bug", "issue"]):
                plot_points.append(
                    {
                        "type": "conflict",
                        "description": f"A challenge was overcome: {commit['message'].splitlines()[0]}",
                        "date": commit["date"],
                    }
                )
            elif any(keyword in msg for keyword in ["refactor", "rewrite", "improve"]):
                plot_points.append(
                    {
                        "type": "transformation",
                        "description": f"The codebase evolved: {commit['message'].splitlines()[0]}",
                        "date": commit["date"],
                    }
                )
        
        return plot_points[:10]  # Limit to top 10 plot points
    
    def _create_prompt(self, story_data: Dict[str, Any]) -> str:
        """Create a detailed prompt for the AI storyteller, incorporating README content."""
        project_name = story_data['project_name']
        project_description = story_data['project_description']
        setting = story_data['setting']
        readme_content = story_data['readme_content']
        
        prompt = f"""
        Generate a professional and accurate development story for the project "{project_name}", which is a {setting}.
        Project Overview: {project_description}
        ---
        **Story Structure:**
        1.  **Introduction:**
            *   Briefly introduce the project and its initial purpose.
            *   Mention the project's inception and early contributions.
        2.  **Development Phases:**
            *   Describe the key development periods, highlighting major features implemented, significant architectural changes, and refactoring efforts.
            *   Detail how challenges (e.g., bugs, technical hurdles) were addressed.
            *   Integrate major merges and releases as significant milestones, explaining their impact on the project's evolution.
        3.  **Contributors and Their Impact:**
            *   Introduce the main contributors and their roles.
            *   Summarize their key contributions and overall impact on the project.
        4.  **Conclusion:**
            *   Summarize the project's journey and its current state.
            *   Reflect on its growth and the collective effort involved.
        ---
        **Key Data to Incorporate:**
        **TIMELINE OF MAJOR EVENTS:**
        {self._format_timeline(story_data['timeline'])}
        **MAIN CONTRIBUTORS:**
        {self._format_characters(story_data['characters'])}
        **KEY DEVELOPMENT POINTS (from commit messages):**
        {self._format_plot_points(story_data['plot_points'])}
        **ADDITIONAL PROJECT CONTEXT (from README.md - use this for factual details about the project's purpose, features, and setup):**
        {readme_content if readme_content else "No README content available."}
        ---
        **Narrative Style:**
        *   **Tone:** Professional, factual, and informative.
        *   **Language:** Clear, concise, and direct. Avoid overly dramatic or fictionalized language.
        *   **Focus:** Emphasize the technical journey, problem-solving, and project evolution.
        *   **Word Count:** Aim for 500-800 words.
        Begin the development story of "{project_name}".
        """
        return prompt
    
    def _format_timeline(self, timeline: List[Dict[str, Any]]) -> str:
        """Format timeline for the prompt."""
        return "\n".join(
            [
                f"- {format_date(event['date'])}: {event['description']} (Significance: {event['significance']})"
                for event in timeline
            ]
        )
    
    def _format_characters(self, characters: List[Dict[str, Any]]) -> str:
        """Format character descriptions for the prompt."""
        return "\n".join(
            [
                f"- {char['name']}: {char['role']}, {char['impact']}. "
                f"First appeared: {char['first_appearance']}, Last seen: {char['last_appearance']}. "
                f"Made {char['contributions']} contributions."
                for char in characters
            ]
        )
    
    def _format_plot_points(self, plot_points: List[Dict[str, Any]]) -> str:
        """Format plot points for the prompt."""
        return "\n".join(
            [
                f"- {format_date(point['date'])} ({point['type']}): {point['description']}"
                for point in plot_points
            ]
        )
