class JiraService:
    def __init__(self, base_url, email, api_token):
        # In a real scenario, we would set up the connection here
        self.base_url = base_url
        self.auth = (email, api_token)
        print(f"Mock Jira Service initialized for {base_url}")

    def get_in_progress_issues(self, project_key):
        """Fetches all issues that are 'in progress' for a project."""
        # This is MOCK DATA for now. We will replace this with a real API call.
        print(f"Mock: Fetching in-progress issues for project {project_key}")
        mock_issues = [
            {"id": "123", "key": "PROJ-1", "assignee": "john.doe@example.com", "summary": "Build the login page"},
            {"id": "124", "key": "PROJ-2", "assignee": "jane.smith@example.com", "summary": "Fix database bug"},
        ]
        return mock_issues