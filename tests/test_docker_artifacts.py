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

    def test_compose_defines_app_and_persistent_postgres_deployment(self):
        compose_path = PROJECT_ROOT / "docker-compose.yml"
        env_example_path = PROJECT_ROOT / ".env.example"

        compose = compose_path.read_text()
        self.assertIn("name: hey", compose)
        self.assertIn("  db:", compose)
        self.assertIn("image: postgres:16-alpine", compose)
        self.assertIn("pg_isready -U ${POSTGRES_USER:-hey} -d ${POSTGRES_DB:-hey}", compose)
        self.assertIn("- postgres_data:/var/lib/postgresql/data", compose)
        self.assertIn("  app:", compose)
        self.assertIn("condition: service_healthy", compose)
        self.assertIn('"127.0.0.1:9600:8000"', compose)
        self.assertIn("DATABASE_URL: ${DATABASE_URL:-postgres://hey:hey-local-change-me@db:5432/hey}", compose)
        self.assertIn("CSRF_TRUSTED_ORIGINS: ${CSRF_TRUSTED_ORIGINS:-https://hey.leorey.es,http://localhost:9600,http://127.0.0.1:9600}", compose)
        self.assertIn("volumes:\n  postgres_data:", compose)

        env_example = env_example_path.read_text()
        for variable in [
            "POSTGRES_DB=hey",
            "POSTGRES_USER=hey",
            "POSTGRES_PASSWORD=change-me-to-a-long-random-string",
            "WEB_CONCURRENCY=2",
            "WEB_TIMEOUT=60",
            "SECURE_SSL_REDIRECT=False",
            "CSRF_TRUSTED_ORIGINS=https://hey.leorey.es,http://localhost:9600,http://127.0.0.1:9600",
            "DATABASE_URL=postgres://hey:change-me-to-a-long-random-string@db:5432/hey",
        ]:
            self.assertIn(variable, env_example)


if __name__ == "__main__":
    unittest.main()
