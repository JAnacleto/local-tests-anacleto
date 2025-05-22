import argparse
import re
import sys
from html import escape

from git import Repo


def get_commits_info(version: str) -> dict[str, list[str]]:
    """
    Get the commit messages and ticket IDs between the two latest tags in v0.0.0 format.
    This function uses the GitPython library to access the git repository.
    """

    # Get all tags from the repository and sort them by most recent commit date
    repo = Repo(search_parent_directories=True)
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_date)
    tags.reverse()

    # Filter tags to only include those that match the v0.0.0 format
    filtered_tags = [
        tag for tag in tags if re.match(r"^v\d+\.\d+\.\d+(-\d+-[a-z\d]+)?$", tag.name)
    ]

    # Initialize a set to store unique ticket IDs
    ticket_ids = set()
    commit_messages = []

    # If there are at least two tags, get the commit history between the two most recent tags
    if len(filtered_tags) >= 2:
        latest_tag, previous_tag = filtered_tags[:2]

        print(f"Getting commits between {previous_tag} and {latest_tag}")

        assert latest_tag.name == version, "Latest tag does not match provided version."

        # Get the commit history between the two tags
        commits = list(repo.iter_commits(f"{previous_tag}..{latest_tag}"))

    # If there is only one tag, get the commit history from that tag to the current HEAD
    elif len(filtered_tags) == 1:
        latest_tag = filtered_tags[0]

        print(f"Getting commits from {latest_tag}")

        assert latest_tag.name == version, "Latest tag does not match provided version."
        commits = list(repo.iter_commits(latest_tag))
    else:
        print("No tags found in the repository.")
        sys.exit(1)

    # Iterate through the commits and extract ticket IDs from each commit messages
    for commit in commits:
        commit_message = commit.message.replace("\n", "")

        commit_messages.append(escape(commit_message))

        if ticket := re.match(r"^E3AUDEDH-[0-9]+:", commit_message):
            ticket_ids.add(ticket.group(0).split(":")[0])

    # Remove the ticket ID "E3AUDEDH-0" if it exists
    ticket_ids.discard("E3AUDEDH-0")
    print(f"Ticket IDs found: {ticket_ids}")

    return {"ticket_ids": list(ticket_ids), "commit_messages": commit_messages}


def main(application: str, version: str):

    commits_info = get_commits_info(version)


if __name__ == "__main__":

    applications = ["doa", "odc"]

    parser = argparse.ArgumentParser(description="Confluence Page Creator")

    parser.add_argument(
        "--application",
        type=str,
        choices=applications,
        required=True,
        help="Application name (doa or odc)",
    )
    parser.add_argument(
        "--version", type=str, required=True, help="Application version"
    )

    main(**parser.parse_args().__dict__)