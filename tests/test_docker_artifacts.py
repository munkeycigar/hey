"""Verify the Docker app image contract without requiring Docker."""

from pathlib import Path
import stat
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DockerArtifactTests(unittest.TestCase):
    def test_docker_app_image_files_are_defined(self):
        dockerignore_path = PROJECT_ROOT / ".dockerignore"
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        entrypoint_path = PROJECT_ROOT / "docker" / "entrypoint.sh"

        self.assertTrue(dockerignore_path.exists(), ".dockerignore is required")
        self.assertTrue(dockerfile_path.exists(), "Dockerfile is required")
        self.assertTrue(entrypoint_path.exists(), "docker/entrypoint.sh is required")

        dockerignore = dockerignore_path.read_text()
        for pattern in [
            ".git",
            ".env",
            ".env.*",
            "!.env.example",
            ".worktrees/",
            ".attachments/",
            ".alfreds-*.pid",
        ]:
            self.assertIn(pattern, dockerignore)

        dockerfile = dockerfile_path.read_text()
        self.assertIn("FROM python:3.12-slim", dockerfile)
        self.assertIn("COPY requirements.txt .", dockerfile)
        self.assertIn("pip install -r requirements.txt", dockerfile)
        self.assertIn("COPY . .", dockerfile)
        self.assertIn("ENTRYPOINT [\"/app/docker/entrypoint.sh\"]", dockerfile)

        entrypoint = entrypoint_path.read_text()
        self.assertTrue(entrypoint.startswith("#!/bin/sh\nset -eu\n"))
        self.assertIn("python manage.py migrate --noinput", entrypoint)
        self.assertIn("python manage.py collectstatic --noinput", entrypoint)
        self.assertIn("exec gunicorn config.wsgi:application", entrypoint)
        self.assertIn("--bind \"0.0.0.0:${PORT:-8000}\"", entrypoint)
        self.assertTrue(entrypoint_path.stat().st_mode & stat.S_IXUSR)


if __name__ == "__main__":
    unittest.main()
