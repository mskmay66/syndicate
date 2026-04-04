# Contributing

Thanks for your interest in contributing to Syndicate! 🎉
We welcome bug reports, feature requests, and pull requests of all kinds.

## 🛠 Getting Started

1. Fork the repository and clone your fork:

```bash
git clone https://github.com/your-username/syndicate.git
cd syndicate
```

2. Set up your environment (we use uv):

```bash
uv sync
```

3. Install pre-commit hooks (required):

```bash
uv add pre-commit --dev
uv run pre-commit install
```

4. (Optional) Install additional development tools:

```bash
uv add pytest ruff --dev
```
## 🧪 Running Tests

Make sure all tests pass before submitting changes:

```bash
uv run pytest tests/*
```

## ✨ Making Changes

* Create a new branch:

```bash
git checkout -b feature/your-feature-name
```
* Keep changes focused and well-scoped
* Add or update tests when applicable
* Ensure code is formatted and linted (pre-commit will run automatically on commit):

```bash
uv run ruff check .
```

## 🚀 Submitting a Pull Request

1. Push your branch:

```bash
git push origin feature/your-feature-name
```

2. Open a pull request against main
3. Provide a clear description of:
  * What changed
  * Why it’s needed
  * Any relevant context or screenshots

## 🐛 Reporting Issues

If you find a bug or have a feature request, please open an issue and include:

* A clear description of the problem
* Steps to reproduce (if applicable)
* Expected vs actual behavior
* Environment details (Python version, OS, etc.)

See the `ISSUES.md` file for more information.

## 📌 Guidelines

* Follow existing code style and structure
* Write clear, concise commit messages
* Ensure pre-commit hooks pass before pushing changes
* Be respectful and constructive in discussions

Thanks for helping improve Syndicate!
