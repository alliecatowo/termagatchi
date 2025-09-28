"""Development scripts for Termagatchi."""

import subprocess
import sys


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("stdout:", e.stdout)
        if e.stderr:
            print("stderr:", e.stderr)
        return False


def lint() -> None:
    """Run linting tools."""
    success = True
    success &= run_command(["ruff", "check", "src/"], "Running Ruff linter")
    success &= run_command(["mypy", "src/"], "Running MyPy type checker")

    if success:
        print("✅ All linting checks passed!")
    else:
        print("❌ Some linting checks failed")
        sys.exit(1)


def format() -> None:
    """Format code."""
    success = True
    success &= run_command(["ruff", "check", "--fix", "src/"], "Fixing Ruff issues")
    success &= run_command(["ruff", "format", "src/"], "Formatting with Ruff")

    if success:
        print("✅ Code formatted successfully!")
    else:
        print("❌ Formatting failed")
        sys.exit(1)


def check() -> None:
    """Run all checks."""
    print("🚀 Running full check suite...")
    lint()
    print("✅ All checks passed! Ready to commit! 🎉")


if __name__ == "__main__":
    # Allow running as a module
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "lint":
            lint()
        elif cmd == "format":
            format()
        elif cmd == "check":
            check()
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    else:
        print("Available commands: lint, format, check")
