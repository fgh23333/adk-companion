# ADK Companion Agent

The ADK Companion Agent is a sophisticated, self-evolving software agent built with the Google Agent Development Kit (ADK). It is designed to assist in the development and maintenance of ADK-based projects, acting as both an expert on the framework and an automated engineer that keeps the project up-to-date with the latest changes.

## Features

- **Expert Guidance**: The agent can read its own source code and documentation to provide insights and guidance on the ADK framework.
- **Automated Evolution**: The agent can track upstream changes in the ADK framework, automatically update dependencies, and even generate pull requests with sample code for new features.
- **Dual-Agent Architecture**: The project uses a main agent for orchestration and a sub-agent for specialized tasks like pull request reviews. This separation of concerns ensures a robust and secure workflow.
- **Automated PR Management**: The agent can create, review, and merge pull requests. It can also be configured to automatically request reviews from other team members.

## Architecture

The ADK Companion Agent consists of two main components:

- **`adk_companion`**: The main agent, responsible for orchestrating the development and maintenance workflow. It has two primary roles:
    - **The Expert**: Provides guidance on the ADK framework by reading its own source code and documentation.
    - **The Evolver**: Automates the process of tracking upstream framework updates, upgrading dependencies, and generating demo code for new features.
- **`pr_reviewer`**: A sub-agent that is responsible for reviewing pull requests. It uses a separate GitHub token to ensure objectivity and to comply with repository rules that prevent users from approving their own pull requests.

## Tools

The ADK Companion Agent comes with a rich set of tools for interacting with the ADK framework and managing the development workflow. These tools include:

- `read_adk_codebase`: Search the ADK source code for a specific keyword.
- `check_upstream_release`: Check for the latest release of the ADK framework.
- `generate_pr`: Create a new pull request.
- `generate_evolution_pr`: Create a pull request to update the project to a new version of the ADK.
- `read_github_repo`: Read the contents of a file or directory in a GitHub repository.
- `review_pr`: Review a pull request.
- `merge_pr`: Merge a pull request.
- `list_prs`: List all pull requests in a repository.
- `list_branches`: List all branches in a repository.
- `check_pr_author`: Check the author of a pull request.
- `smart_review_pr`: Perform a "smart" review of a pull request, with the option to automatically merge it if it passes all checks.

## Getting Started

To get started with the ADK Companion Agent, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/fgh23333/adk-companion.git
    ```
2.  **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up your environment variables**:
    - Create a `.env` file in the root of the project.
    - Add the following environment variables to the `.env` file:
        - `GITHUB_TOKEN`: Your personal GitHub access token.
        - `REVIEW_GITHUB_TOKEN`: A separate GitHub access token for the `pr_reviewer` agent.
4.  **Run the application**:
    ```bash
    python main.py
    ```

The application will be available at `http://localhost:8080`.

## Usage

You can interact with the ADK Companion Agent by sending it prompts. For example, to ask the agent to check for a new release of the ADK framework, you could send it the following prompt:

> Check for the latest release of the ADK framework.

The agent will then use the `check_upstream_release` tool to check for the latest release and will respond with the version number.
