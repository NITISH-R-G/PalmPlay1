import os
import json
import re

IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.github'}
IGNORE_FILES = {'.DS_Store', 'repo_analysis.json'}

class RepoAnalyzer:
    def __init__(self, root_dir='.'):
        self.root_dir = root_dir
        self.files = []
        self.structure = {}
        self.dependencies = {
            'python': [],
            'node': [],
            'frameworks': set(),
            'env_vars': set(),
            'services': set()
        }

    def walk_repo(self):
        """Walk the repository directory tree and collect structure."""
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            # Mutate dirnames to ignore specific directories
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

            rel_dir = os.path.relpath(dirpath, self.root_dir)
            if rel_dir == '.':
                rel_dir = ''

            self.structure[rel_dir] = {
                'dirs': dirnames,
                'files': [f for f in filenames if f not in IGNORE_FILES]
            }

            for file in filenames:
                if file not in IGNORE_FILES:
                    filepath = os.path.join(dirpath, file)
                    rel_filepath = os.path.relpath(filepath, self.root_dir)
                    self.files.append(rel_filepath)

        return self.structure

    def detect_dependencies(self):
        """Parse requirement files and detect dependencies/frameworks."""
        # Python dependencies
        req_file = os.path.join(self.root_dir, 'requirements.txt')
        if os.path.exists(req_file):
            with open(req_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        pkg = re.split(r'[=<>~]', line)[0].strip()
                        if pkg:
                            self.dependencies['python'].append(pkg)
                            if pkg.lower() in ['django', 'flask', 'fastapi', 'pygame', 'mediapipe', 'opencv-python']:
                                self.dependencies['frameworks'].add(pkg.lower())

        # Node dependencies (if any)
        pkg_json = os.path.join(self.root_dir, 'package.json')
        if os.path.exists(pkg_json):
            with open(pkg_json, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    self.dependencies['node'] = list(deps.keys())
                    for pkg in deps:
                        if pkg.lower() in ['react', 'vue', 'express', 'next']:
                            self.dependencies['frameworks'].add(pkg.lower())
                except json.JSONDecodeError:
                    pass

        # Scan code for env vars
        env_pattern = re.compile(r'os\.environ\.get\([\'"]([A-Z0-9_]+)[\'"]\)|os\.getenv\([\'"]([A-Z0-9_]+)[\'"]\)')
        for filepath in self.files:
            if filepath.endswith('.py'):
                try:
                    with open(os.path.join(self.root_dir, filepath), 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = env_pattern.findall(content)
                        for match in matches:
                            self.dependencies['env_vars'].add(match[0] or match[1])
                except Exception:
                    pass

        # Convert sets to lists for JSON serialization
        self.dependencies['frameworks'] = list(self.dependencies['frameworks'])
        self.dependencies['env_vars'] = list(self.dependencies['env_vars'])
        self.dependencies['services'] = list(self.dependencies['services'])

    def build_knowledge_graph(self):
        """Analyze internal imports to build a module dependency graph."""
        graph = {}
        import_pattern = re.compile(r'^(?:from|import)\s+([a-zA-Z0-9_.]+)', re.MULTILINE)

        for filepath in self.files:
            if filepath.endswith('.py'):
                try:
                    with open(os.path.join(self.root_dir, filepath), 'r', encoding='utf-8') as f:
                        content = f.read()
                        imports = import_pattern.findall(content)
                        # Filter for internal modules (very basic heuristic)
                        module_name = os.path.splitext(os.path.basename(filepath))[0]
                        graph[module_name] = list(set(imports))
                except Exception:
                    pass
        return graph

    def generate_analysis(self):
        self.walk_repo()
        self.detect_dependencies()
        graph = self.build_knowledge_graph()

        analysis = {
            'structure': self.structure,
            'dependencies': self.dependencies,
            'knowledge_graph': graph,
            'files_count': len(self.files)
        }

        output_file = os.path.join(self.root_dir, 'repo_analysis.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        print(f"Analysis saved to {output_file}")

if __name__ == '__main__':
    analyzer = RepoAnalyzer()
    analyzer.generate_analysis()
