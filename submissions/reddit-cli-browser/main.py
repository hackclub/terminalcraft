import praw
import json
import webbrowser
import os
from rich.console import Console
from rich.table import Table

with open("config.json", "r") as file:
    config = json.load(file)

reddit = praw.Reddit(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    user_agent=config["user_agent"],
)

console = Console()
FAVOURITES_FILE = config["favourites_file"]
SAVED_POSTS_DIR = config["saved_posts_dir"]
os.makedirs(SAVED_POSTS_DIR, exist_ok=True)

def load_favourites():
    try:
        if os.path.exists(FAVOURITES_FILE):
            with open(FAVOURITES_FILE, "r") as file:
                return json.load(file)
    except Exception as e:
        console.print(f"[bold red]Error loading favourites: {e}[/bold red]")
    return []

def save_favourites(favourites):
    with open(FAVOURITES_FILE, "w") as file:
        json.dump(favourites, file)

def fetch_posts(subreddit, sort="hot", time_filter="all", limit=5):
    try:
        subreddit = reddit.subreddit(subreddit)
        match sort:
            case "new":
                posts = subreddit.new(limit=limit)
            case "top":
                posts = subreddit.top(time_filter=time_filter, limit=limit)
            case "rising":
                posts = subreddit.rising(limit=limit)
            case "controversial":
                posts = subreddit.controversial(time_filter=time_filter, limit=limit)
            case _:
                posts = subreddit.hot(limit=limit)
        return list(posts)
    except Exception as e:
        console.print(f"[bold red]Error fetching subreddit: {e}[/bold red]")
        return []

def search_posts(subreddit, query, sort="hot", time_filter="all", limit=5):
    try:
        subreddit = reddit.subreddit(subreddit)
        posts = subreddit.search(query, sort=sort, time_filter=time_filter, limit=limit)
        return list(posts)
    except Exception as e:
        console.print(f"[bold red]Error searching subreddit: {e}[/bold red]")
        return []

def print_posts(posts, subreddit, sort):
    table = Table(title=f"r/{subreddit} - {sort}", show_lines=True)
    table.add_column("#", justify="center", style="bold cyan")
    table.add_column("Title", style="bold yellow")
    table.add_column("Upvotes", justify="center", style="bold green")
    table.add_column("Comments", justify="center", style="bold blue")
    for idx, post in enumerate(posts, start=1):
        table.add_row(str(idx), post.title[:50], f"{post.score:,}", str(post.num_comments))
    console.print(table)

def view_post(post):
    console.print(f"\n[bold cyan]{post.title}[/bold cyan]\n")
    console.print(f"[bold magenta]Score:[/bold magenta] {post.score} | Comments: {post.num_comments}\n")
    if post.selftext:
        console.print(post.selftext[:1000])
    elif post.url:
        console.print(f"[bold blue]Media/Link Post:[/bold blue] {post.url}")
        open_choice = input("\nOpen in browser? (y/n) [default: n]: ").strip().lower()
        if open_choice == "" or open_choice == "n":
            pass
        elif open_choice == "y":
            webbrowser.open(post.url)
    else:
        console.print("[bold red]No text content available.[/bold red]")

    view_comments_choice = input("\nView comments? (y/n) [default: n]: ").strip().lower()
    if view_comments_choice == "" or view_comments_choice == "n":
        pass
    elif view_comments_choice == "y":
        display_comments(post)

    save_choice = input("\nSave this post to a file? (y/n/cancel to cancel saving): ").strip().lower()
    if save_choice == "y":
        while True:
            filename = input(f"Enter filename (default: {post.id}) or type 'cancel' to cancel: ").strip()
            if filename == "cancel":
                console.print("[bold red]Saving cancelled.[/bold red]")
                break
            if not filename:
                filename = post.id  
            filepath = os.path.join(SAVED_POSTS_DIR, f"{filename}.txt")
            if os.path.exists(filepath):
                console.print("[bold red]File already exists. Please choose a different filename.[/bold red]")
            else:
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"Title: {post.title}\n\n{post.selftext if post.selftext else post.url}\n\n")
                        save_comments(f, post)
                    console.print(f"[green]Saved as {filepath}[/green]")
                except Exception as e:
                    console.print(f"[bold red]Error saving post: {e}[/bold red]")
                finally:
                    break

def save_comments(file, post):
    comments = post.comments
    if not comments:
        console.print("[bold red]No comments to save.[/bold red]")
        return
    try:
        f.write(f"[bold green]Comments:[/bold green]\n")
        for idx, comment in enumerate(comments, start=1):
            if isinstance(comment, praw.models.MoreComments):
                continue
            file.write(f"Comment #{idx} by {comment.author}:\n{comment.body[:500]}\n\n")
            if len(comment.body) > 500:
                file.write("[bold red]Comment is too long, displaying first 500 characters.[/bold red]\n")
            file.write("\n")
    except Exception as e:
        console.print(f"[bold red]Error saving comments: {e}[/bold red]")
        return

def display_comments(post):
    console.print(f"\n[bold blue]Comments for '{post.title}'[/bold blue]:")
    comments = post.comments
    if len(comments) <= 5:
        if len(comments) == 0:
            console.print("[bold red]No comments found.[/bold red]")
            return
        for idx, comment in enumerate(comments, start=1):
            console.print(f"\n[bold cyan]Comment #{idx}:[/bold cyan]")
            console.print(f"[bold yellow]{comment.author}[/bold yellow] said: {comment.body[:500]}")
            if len(comment.body) > 500:
                console.print("[bold red]Comment is too long, displaying first 500 characters.[/bold red]")
            if isinstance(comment, praw.models.MoreComments):
                continue
    else:
        for idx, comment in enumerate(comments[:5], start=1):
            console.print(f"\n[bold cyan]Comment #{idx}:[/bold cyan]")
            console.print(f"[bold yellow]{comment.author}[/bold yellow] said: {comment.body[:500]}")
            if len(comment.body) > 500:
                console.print("[bold red]Comment is too long, displaying first 500 characters.[/bold red]")
            if isinstance(comment, praw.models.MoreComments):
                continue

        load_more_choice = input("\nWould you like to load more comments? (y/n): ").strip().lower()
        if load_more_choice == "y":
            for idx, comment in enumerate(comments[5:], start=6):
                console.print(f"\n[bold cyan]Comment #{idx}:[/bold cyan]")
                console.print(f"[bold yellow]{comment.author}[/bold yellow] said: {comment.body[:500]}")
                if len(comment.body) > 500:
                    console.print("[bold red]Comment is too long, displaying first 500 characters.[/bold red]")
                if isinstance(comment, praw.models.MoreComments):
                    continue


def browse_favourites():
    favourites = load_favourites()
    if not favourites:
        console.print("[bold red]No favourite subreddits found.[/bold red]")
        return
    console.print("[bold blue]Favourite Subreddits:[/bold blue]")
    for idx, sub in enumerate(favourites, start=1):
        console.print(f"{idx}. {sub}")
    choice = input("Select subreddit number to browse (0 to exit): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(favourites):
        browse_subreddit(favourites[int(choice) - 1])

def browse_subreddit(subreddit=None):
    if not subreddit:
        subreddit = input("Enter subreddit: ").strip()
    sort = input("Sort (hot, new, top, rising, controversial) [default: hot]: ").strip().lower() or "hot"
    time_filter = "all"
    if sort in ["top", "controversial"]:
        time_filter = input("Time filter (all, day, week, month, year) [default: all]: ").strip().lower() or "all"
    limit = input("Number of posts to fetch [default: 5]: ").strip()
    limit = int(limit) if limit.isdigit() else 5
    posts = fetch_posts(subreddit, sort, time_filter, limit)
    if not posts:
        console.print("[bold red]No posts found.[/bold red]")
        return
    print_posts(posts, subreddit, sort)
    while True:
        choice = input("Select post number to view (f to add to favourites, 0 to exit): ").strip()
        if choice == "0":
            break
        if choice == "f":
            favourites = load_favourites()
            if subreddit not in favourites:
                favourites.append(subreddit)
                save_favourites(favourites)
                console.print(f"[green]r/{subreddit} added to favourites.[/green]")
            else:
                console.print(f"[bold red]r/{subreddit} is already in favourites.[/bold red]")
        elif choice.isdigit() and 1 <= int(choice) <= len(posts):
            view_post(posts[int(choice) - 1])
            print_posts(posts, subreddit, sort)  
        else:
            console.print("[bold red]Invalid selection.[/bold red]")

def view_saved_posts():
    while True:
        saved_posts = os.listdir(SAVED_POSTS_DIR)
        if not saved_posts:
            console.print("[bold red]No saved posts found.[/bold red]")
            return
        
        console.print("[bold blue]Saved Posts:[/bold blue]")
        for idx, post_file in enumerate(saved_posts, start=1):
            console.print(f"{idx}. {post_file}")

        choice = input("Select post number to view (0 to exit): ").strip()
        if choice == "0":
            return

        if choice.isdigit() and 1 <= int(choice) <= len(saved_posts):
            post_file = saved_posts[int(choice) - 1]
            filepath = os.path.join(SAVED_POSTS_DIR, post_file)
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
            console.print(f"\n[bold cyan]Content of {post_file}[/bold cyan]:\n{content}")
        else:
            console.print("[bold red]Invalid selection. Please try again.[/bold red]")

def search_subreddit():
    subreddit = input("Enter subreddit to search in: ").strip()
    query = input("Enter search query: ").strip()
    sort = input("Sort (hot, new, top, rising, controversial) [default: hot]: ").strip().lower() or "hot"
    time_filter = "all"
    if sort in ["top", "controversial"]:
        time_filter = input("Time filter (all, day, week, month, year) [default: all]: ").strip().lower() or "all"
    limit = input("Number of posts to fetch [default: 5]: ").strip()
    limit = int(limit) if limit.isdigit() else 5
    posts = search_posts(subreddit, query, sort, time_filter, limit)
    if not posts:
        console.print("[bold red]No posts found.[/bold red]")
        return
    print_posts(posts, subreddit, sort)
    while True:

        choice = input("Select post number to view (f to add to favourites, 0 to exit): ").strip()
        if choice == "0":
            break
        if choice == "f":
            favourites = load_favourites()
            if subreddit not in favourites:
                favourites.append(subreddit)
                save_favourites(favourites)
                console.print(f"[green]r/{subreddit} added to favourites.[/green]")
            else:
                console.print(f"[bold red]r/{subreddit} is already in favourites.[/bold red]")
        elif choice.isdigit() and 1 <= int(choice) <= len(posts):
            view_post(posts[int(choice) - 1])
            print_posts(posts, subreddit, sort)  
        else:
            console.print("[bold red]Invalid selection.[/bold red]")

def main():
    while True:
        console.print("\n[bold blue]Reddit CLI Browser[/bold blue]")
        console.print("1. Browse a subreddit")
        console.print("2. Browse favourite subreddits")
        console.print("3. View saved posts")
        console.print("4. Search a subreddit")
        console.print("0. Exit")
        choice = input("Select an option: ").strip()
        match choice:
            case "1":
                browse_subreddit()
            case "2":
                browse_favourites()
            case "3":
                view_saved_posts()
            case "4":
                search_subreddit()
            case "0":
                break
            case _:
                console.print("[bold red]Invalid option. Try again.[/bold red]")

if __name__ == "__main__":
    main()
