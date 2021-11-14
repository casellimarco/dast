import os


VERSION_MAJOR = 0
VERSION_MINOR = 0


def get_version():
    commit_hashes = os.popen("(git rev-list HEAD)").read()
    version_patch = len(commit_hashes.split('\n')) - 1
    return f'{VERSION_MAJOR}.{VERSION_MINOR}.{version_patch}'


def push_tag_for_new_version():
    current_branch = os.popen("(git rev-parse --abbrev-ref HEAD)").read().rstrip()
    assert current_branch == "main", "You must be on main to push a new version"

    version = get_version()

    os.popen(f"(git tag {version})")
    os.popen(f"(git push -u origin {version})")

    print(f"tagged and pushed version: {version}")


if __name__ == "__main__":
    push_tag_for_new_version()
