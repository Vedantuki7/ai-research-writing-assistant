# Contributing to AI-Powered Research & Writing Assistant

Thank you for your interest in contributing to this project! As a community-driven open source project, we welcome your contributions, bug reports, and suggestions.

To maintain a professional, high-quality codebase, please follow the guidelines below.

---

## 🛠️ Getting Started

### 1. Fork and Clone
First, fork the repository to your own GitHub account, and then clone your fork locally:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/ai-research-writing-assistant.git
cd ai-research-writing-assistant
```

### 2. Set Up the Development Environment
We recommend using Conda or a Python virtual environment to manage dependencies:

```bash
# Create and activate environment
conda create -n research-assistant-dev python=3.12 -y
conda activate research-assistant-dev

# Install dependencies (including dev and test requirements)
pip install -r requirements.txt
```

### 3. Configure API Keys
Copy the template configuration or create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

---

## 🌿 Branch Naming Conventions
To keep history organized, please use the following prefixes for branch names:

- `feature/` for new features (e.g., `feature/incremental-rag-updates`)
- `fix/` for bug fixes (e.g., `fix/agent-init-race-condition`)
- `docs/` for documentation updates (e.g., `docs/add-contributing-guide`)
- `test/` for adding or improving tests (e.g., `test/integration-tests-orchestrator`)

Example:
```bash
git checkout -b feature/parallel-orchestrator-execution
```

---

## 📝 Code Style & Guidelines
We target clean, maintainable, and well-documented Python code.

- **Style Standard**: Adhere to PEP 8 guidelines.
- **Formatting**: We use `black` for code formatting. Run it before committing:
  ```bash
  black src/ app.py
  ```
- **Linting**: Ensure your code is free of linting issues using `flake8`.
- **Docstrings**: Document all new modules, classes, and methods using Google-style docstrings:
  ```python
  def execute_workflow(self, topic: str, audience: str) -> str:
      """Executes the research and writing orchestrator pipeline.

      Args:
          topic: The subject to research.
          audience: The target reader level (general, academic, etc.).

      Returns:
          The generated and edited research article in markdown format.
      """
  ```

---

## 🚀 Submitting a Pull Request
1. Commit your changes locally with clear, descriptive commit messages.
2. Push your branch to your forked repository on GitHub.
3. Open a Pull Request (PR) from your fork's branch to the `main` branch of the upstream repository.
4. Ensure all automated checks (linting, tests) pass.
5. A maintainer will review your pull request and coordinate merging it.
