# Publishing This Showcase to GitHub

This environment prepared the project files, but creating a new repository under a personal GitHub account requires GitHub write access from your account.

## Recommended Repository Name

```text
custom-retriever-drones-qa
```

Alternative names:

```text
arangodb-custom-retriever-qa
drones-retriever-testing-report
custom-retriever-platform-qa
```

## Before Publishing

Confirm that the repository does not contain:

- passwords,
- API keys,
- JWT tokens,
- Slack links containing credentials,
- internal-only endpoint details if your company does not allow them,
- original article files unless you have permission to publish them,
- notebook outputs containing secrets.

## Option 1: Publish with GitHub CLI

From the parent directory of this project:

```bash
cd custom-retriever-drones-qa-showcase
git init
git add .
git commit -m "Add custom retriever drones QA showcase"
gh repo create custom-retriever-drones-qa --public --source=. --remote=origin --push
```

Use `--private` instead of `--public` if any details should remain private.

## Option 2: Publish Through GitHub Website

1. Go to <https://github.com/new>.
2. Create a repository named `custom-retriever-drones-qa`.
3. Do not initialize with a README if using the files from this project.
4. From your terminal, run:

```bash
cd custom-retriever-drones-qa-showcase
git init
git add .
git commit -m "Add custom retriever drones QA showcase"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/custom-retriever-drones-qa.git
git push -u origin main
```

## Suggested GitHub Description

```text
QA investigation and portfolio write-up for ArangoDB Custom Retriever testing over a Drones markdown corpus.
```

## Suggested Topics

```text
arangodb
python
qa-testing
rest-api
retrieval
genai
notebook
debugging
```
