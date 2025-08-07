import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict
from pathlib import Path

class RepoVisualizer:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data
    
    def plot_timeline(self, output_path: Path):
        """Generate a timeline of repository activity."""
        commits = self.repo_data["commits"]
        if not commits:
            return
        
        # Group commits by month
        monthly_commits = defaultdict(int)
        for commit in commits:
            month_key = commit["date"].strftime("%Y-%m")
            monthly_commits[month_key] += 1
        
        # Prepare data for plotting
        months = sorted(monthly_commits.keys())
        counts = [monthly_commits[month] for month in months]
        dates = [datetime.strptime(month, "%Y-%m") for month in months]
        
        # Create plot
        plt.figure(figsize=(12, 6))
        plt.bar(dates, counts, width=20, color="#3498db", alpha=0.7)
        
        # Formatting
        plt.title(f"Commit Activity Timeline - {self.repo_data['repo_name']}", fontsize=14)
        plt.xlabel("Time", fontsize=12)
        plt.ylabel("Number of Commits", fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_contributors(self, output_path: Path):
        """Generate a contributor activity chart."""
        contributors = self.repo_data["contributors"]
        if not contributors:
            return
        
        # Prepare data
        names = list(contributors.keys())
        commit_counts = [contributors[name]["commits"] for name in names]
        
        # Sort by commit count
        sorted_data = sorted(zip(names, commit_counts), key=lambda x: x[1], reverse=True)
        names = [x[0] for x in sorted_data]
        commit_counts = [x[1] for x in sorted_data]
        
        # Create plot
        plt.figure(figsize=(10, max(6, len(names) * 0.4)))
        bars = plt.barh(names, commit_counts, color="#2ecc71", alpha=0.7)
        
        # Formatting
        plt.title(f"Contributor Activity - {self.repo_data['repo_name']}", fontsize=14)
        plt.xlabel("Number of Commits", fontsize=12)
        plt.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()