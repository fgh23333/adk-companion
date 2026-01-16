import httpx
from typing import Optional, List, Dict, Any
from .config import GITLAB_BASE_URL
import os
from dotenv import load_dotenv
load_dotenv()

# region Internal Functions
def _get_auth_headers() -> Dict[str, str]:
    return {
        "PRIVATE-TOKEN": os.getenv('GITLAB_PRIVATE_TOKEN'),
        "Content-Type": "application/json"
    }

def _request(method: str, endpoint: str, **kwargs):
    headers = _get_auth_headers()
    url = f"{GITLAB_BASE_URL}{endpoint}"
    with httpx.Client() as client:
        try:
            response = client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e), "response": e.response.text}
        except httpx.RequestError as e:
            return {"error": str(e)}
# endregion

# region Tool Functions
def get_projects(membership: bool = True, search: Optional[str] = None) -> Dict[str, Any]:
    """Lists projects accessible by the user."""
    params = {"membership": membership}
    if search:
        params["search"] = search
    return _request("get", "/gitlab/api/v1/git/projects", params=params)

def search_projects(name: str) -> Dict[str, Any]:
    """Searches for projects by name."""
    return _request("get", "/gitlab/api/v1/git/projects/search", params={"name": name})

def get_project(project_id: int) -> Dict[str, Any]:
    """Gets the details of a specific project."""
    return _request("get", "/gitlab/api/v1/git/project", params={"project_id": project_id})

def get_branches(project_id: int, search: Optional[str] = None) -> Dict[str, Any]:
    """Lists branches in a repository."""
    params = {"project_id": project_id}
    if search:
        params["search"] = search
    return _request("get", "/gitlab/api/v1/git/branches", params=params)

def create_branch(project_id: int, branch_name: str, base_ref: str) -> Dict[str, Any]:
    """Creates a new branch in a repository."""
    json_data = {"project_id": project_id, "branch_name": branch_name, "base_ref": base_ref}
    return _request("post", "/gitlab/api/v1/git/branches", json=json_data)

def get_commits(project_id: int, ref_name: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """Lists commits for a repository or a specific ref."""
    params = {"project_id": project_id, "limit": limit}
    if ref_name:
        params["ref_name"] = ref_name
    return _request("get", "/gitlab/api/v1/git/commits", params=params)

def get_file_content(project_id: int, file_path: str, ref: str) -> Dict[str, Any]:
    """Gets the content of a specific file in a repository."""
    params = {"project_id": project_id, "file_path": file_path, "ref": ref}
    return _request("get", "/gitlab/api/v1/git/files/raw", params=params)

def commit_changes(project_id: int, branch: str, commit_message: str, actions: List[Dict[str, Any]], work_item_id: str, author_name: str, author_email: str) -> Dict[str, Any]:
    """Creates a new commit in a branch."""
    json_data = {
        "project_id": project_id, "branch": branch, "commit_message": commit_message,
        "actions": actions, "work_item_id": work_item_id, "author_name": author_name,
        "author_email": author_email
    }
    return _request("post", "/gitlab/api/v1/git/commit", json=json_data)

def get_merge_requests(project_id: int, state: str = "opened", search: Optional[str] = None) -> Dict[str, Any]:
    """Lists Merge Requests for a project."""
    params = {"project_id": project_id, "state": state}
    if search:
        params["search"] = search
    return _request("get", "/gitlab/api/v1/git/merge_requests", params=params)

def create_merge_request(project_id: int, source_branch: str, target_branch: str, title: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Creates a new Merge Request."""
    json_data = {
        "project_id": project_id, "source_branch": source_branch, "target_branch": target_branch, "title": title,
    }
    if description:
        json_data["description"] = description
    return _request("post", "/gitlab/api/v1/git/merge_requests", json=json_data)

def get_merge_request(project_id: int, iid: int) -> Dict[str, Any]:
    """Gets the details of a specific Merge Request."""
    return _request("get", f"/gitlab/api/v1/git/merge_requests/{iid}", params={"project_id": project_id})

def get_merge_request_author(project_id: int, iid: int) -> Dict[str, Any]:
    """Gets the author of a Merge Request."""
    return _request("get", f"/gitlab/api/v1/git/merge_requests/{iid}/author", params={"project_id": project_id})

def create_review_note(project_id: int, iid: int, review_note: str) -> Dict[str, Any]:
    """Posts a review note (comment) on a Merge Request."""
    body = {
        "project_id": project_id,
        "iid": iid,
        "body": review_note
    }
    return _request("post", f"/gitlab/api/v1/git/merge_requests/{iid}/notes", json=body)

def get_merge_request_details(project_id: int, iid: int) -> Dict[str, Any]:
    """Gets the details of a specific Merge Request, including file changes."""
    return _request("get", f"/gitlab/api/v1/git/merge_requests/{iid}/details", params={"project_id": project_id})
# endregion
