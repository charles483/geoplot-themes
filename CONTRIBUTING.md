# Contributing to GeoPlot-Themes 🤝

Thank you for your interest in contributing to **GeoPlot-Themes**! We welcome contributions from the community, whether they are bug fixes, new themes, custom colormaps, documentation updates, or feature requests.

Follow this guide to set up your local development environment and submit your changes.

---

## 🛠️ Local Development Setup

We recommend using **`uv`** for fast and reproducible dependency management and packaging.

### 1. Clone the Repository
Clone the repository and enter the directory:
```bash
git clone https://github.com/charles483/geoplot-themes.git
cd geoplot-themes
```

### 2. Set Up the Virtual Environment
Using `uv`:
```bash
# Create and activate environment automatically
uv venv
# On Windows PowerShell:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```
Using standard `venv`:
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Package in Editable Mode
Install the package along with its development dependencies:
```bash
# Using uv
uv pip install -e ".[dev]"

# Or using standard pip
pip install -e ".[dev]"
```

---

## 🧪 Testing

We use **`pytest`** to write and run unit tests. Make sure all tests pass before submitting a pull request.

To run the test suite:
```bash
# Using uv
uv run pytest

# Or directly via pytest if your venv is active
pytest
```

---

## 🎨 Style Guidelines

To keep the codebase clean and consistent:
* **Formatting**: We use **Black** for Python code formatting. Run it before committing:
  ```bash
  black src/ tests/
  ```
* **Type Hints**: Please write type annotations for all new functions and public APIs.
* **Docstrings**: Document all new modules, classes, and functions following the Sphinx or Google docstring format.

---

## 📥 Submitting a Pull Request (PR)

1. **Create a Branch**: Create a descriptive branch name for your work:
   ```bash
   git checkout -b feature/my-cool-theme
   ```
2. **Commit Your Changes**: Keep your commits small and write clear, descriptive commit messages.
3. **Keep it Synchronized**: Rebase or merge from the upstream `main` branch regularly to avoid merge conflicts.
4. **Push and Open PR**: Push your branch to GitHub and open a Pull Request against the `main` branch.

---

## 📧 Questions & Support

If you have questions or need assistance during development, feel free to open a GitHub Issue or reach out to us directly at **info@perurgeospatial.com**.

*Thank you for making GeoPlot-Themes better!*
