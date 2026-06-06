import json
import os
import urllib.request
import urllib.error

class AIDocsAgent:
    def __init__(self, analysis_file='repo_analysis.json', docs_dir='.github/docs'):
        self.analysis_file = analysis_file
        self.docs_dir = docs_dir
        self.data = {}
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def call_llm(self, prompt):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "This repository is continuously analyzed, documented, and maintained by an automated AI agent and CI/CD pipelines. (AI summarization disabled: no API key)."

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an expert technical writer and software architect."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000
        }

        try:
            req = urllib.request.Request(url, json.dumps(data).encode('utf-8'), headers)
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content'].strip()
        except urllib.error.URLError as e:
            print(f"Error calling LLM: {e}")
            return "Error generating AI summary."

    def generate_readme(self):
        """Generate a structured README based on repo analysis."""

        # Determine some basics
        dependencies = self.data.get('dependencies', {})
        frameworks = dependencies.get('frameworks', [])
        python_deps = dependencies.get('python', [])
        env_vars = dependencies.get('env_vars', [])

        repo_name = os.environ.get("GITHUB_REPOSITORY", "USER/REPO")

        readme_content = []
        readme_content.append("# Autonomous Repository\n")

        readme_content.append(f"![CI Status](https://img.shields.io/github/actions/workflow/status/{repo_name}/repo-automation.yml?branch=main)")
        readme_content.append("![Auto-Documented](https://img.shields.io/badge/Auto--Documented-Yes-success)\n")

        readme_content.append("## Project Overview")

        prompt = f"""
        Based on the following repository analysis, write a 2-3 paragraph Project Overview and Architecture Summary.
        Structure: {json.dumps(self.data.get('structure', {}))}
        Dependencies: {json.dumps(dependencies)}
        """
        ai_overview = self.call_llm(prompt)
        readme_content.append(ai_overview + "\n")

        readme_content.append("## Technology Stack")
        if frameworks:
            readme_content.append("**Frameworks:** " + ", ".join(frameworks))
        if python_deps:
            readme_content.append("**Python Dependencies:** " + ", ".join(python_deps[:10]) + ("..." if len(python_deps) > 10 else ""))
        readme_content.append("\n")

        readme_content.append("## Repository Structure")
        readme_content.append("```text")
        for path, info in self.data.get('structure', {}).items():
            if path:
                readme_content.append(f"/{path}")
            for f in info.get('files', []):
                indent = "  " if path else ""
                readme_content.append(f"{indent}├── {f}")
        readme_content.append("```\n")

        readme_content.append("## Environment Variables")
        if env_vars:
            readme_content.append("The following environment variables were detected in the codebase:")
            for ev in env_vars:
                readme_content.append(f"- `{ev}`")
        else:
            readme_content.append("No explicit environment variables detected.")
        readme_content.append("\n")

        readme_content.append("## Setup Instructions")
        readme_content.append("1. Clone the repository")
        if 'requirements.txt' in self.data.get('structure', {}).get('', {}).get('files', []):
            readme_content.append("2. Install dependencies: `pip install -r requirements.txt`")
        if env_vars:
            readme_content.append("3. Configure environment variables.")
        readme_content.append("\n")

        readme_content.append("## Architecture Diagrams")

        arch_file = os.path.join(self.docs_dir, 'architecture.md')
        if os.path.exists(arch_file):
            with open(arch_file, 'r') as f:
                content = f.read().replace('# Architecture Diagram\n\n', '')
                readme_content.append("### System Architecture")
                readme_content.append(content)

        dep_file = os.path.join(self.docs_dir, 'dependencies.md')
        if os.path.exists(dep_file):
            with open(dep_file, 'r') as f:
                content = f.read().replace('# Dependency Graph\n\n', '')
                readme_content.append("### Module Dependencies")
                readme_content.append(content)

        return "\n".join(readme_content)

    def update_readme(self):
        content = self.generate_readme()
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(content)
        print("README.md updated successfully.")

if __name__ == '__main__':
    agent = AIDocsAgent()
    agent.update_readme()
