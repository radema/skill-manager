import os
import shutil
import subprocess
import time
import unittest
from pathlib import Path
from unittest.mock import patch

# Import the module under test
import skm.logic

TEST_DIR = Path("/tmp/skm_bench_test")
MARKETPLACE_DIR = TEST_DIR / "marketplace"
UPSTREAM_DIR = TEST_DIR / "upstream"

def setup_git_repo(path, branch="main", content="initial"):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--initial-branch=" + branch], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "you@example.com"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Your Name"], cwd=path, check=True, capture_output=True)

    # Create necessary structure for skm (it expects some content)
    # The sparse checkout logic expects 'skills/' folder by default, but skm add_skill sets it up.
    # We should ensure the repo has a 'skills' folder so sparse checkout works and doesn't complain (optional but good practice)
    skills_dir = path / "skills"
    skills_dir.mkdir(exist_ok=True)
    (skills_dir / "test.txt").write_text(content)

    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=path, check=True, capture_output=True)

    # Allow push/pull
    subprocess.run(["git", "config", "receive.denyCurrentBranch", "ignore"], cwd=path, check=True, capture_output=True)

class Benchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if TEST_DIR.exists():
            shutil.rmtree(TEST_DIR)
        TEST_DIR.mkdir(parents=True)
        MARKETPLACE_DIR.mkdir()
        UPSTREAM_DIR.mkdir()

        # Create upstream repos
        setup_git_repo(UPSTREAM_DIR / "repo-main", branch="main")
        setup_git_repo(UPSTREAM_DIR / "repo-master", branch="master")
        setup_git_repo(UPSTREAM_DIR / "repo-dev", branch="develop")

    def setUp(self):
        # Clean marketplace before each test
        if MARKETPLACE_DIR.exists():
            shutil.rmtree(MARKETPLACE_DIR)
        MARKETPLACE_DIR.mkdir()

        # Patch MARKETPLACE_ROOT
        self.patcher = patch('skm.logic.MARKETPLACE_ROOT', MARKETPLACE_DIR)
        self.mock_root = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def run_benchmark(self, repo_name, expected_branch):
        repo_path = UPSTREAM_DIR / repo_name
        # skm.logic.add_skill expects a URL.
        # We construct a file URL.
        url = f"file://{repo_path}"

        # The logic parses owner/repo from url.
        # file:///tmp/skm_bench_test/upstream/repo-main
        # owner = upstream, repo = repo-main

        start_time = time.time()
        try:
            skm.logic.add_skill(url)
        except Exception as e:
            self.fail(f"add_skill failed: {e}")
        end_time = time.time()

        duration = end_time - start_time
        print(f"Benchmark {repo_name} ({expected_branch}): {duration:.4f}s")

        # Verify
        target_name = f"upstream-{repo_name}" # based on parse_github_url logic
        target_path = MARKETPLACE_DIR / target_name

        self.assertTrue(target_path.exists(), f"Target path {target_path} does not exist")

        # Check if the branch is correct
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=target_path, capture_output=True, text=True, check=True)
        actual_branch = res.stdout.strip()
        self.assertEqual(actual_branch, expected_branch, f"Expected branch {expected_branch}, got {actual_branch}")

        return duration

    def test_benchmark_main(self):
        self.run_benchmark("repo-main", "main")

    def test_benchmark_master(self):
        self.run_benchmark("repo-master", "master")

    def test_benchmark_develop(self):
        self.run_benchmark("repo-dev", "develop")

if __name__ == '__main__':
    unittest.main()
