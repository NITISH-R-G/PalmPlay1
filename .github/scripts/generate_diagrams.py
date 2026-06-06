import json
import os

class DiagramGenerator:
    def __init__(self, analysis_file='repo_analysis.json'):
        self.analysis_file = analysis_file
        self.data = {}
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def generate_mermaid_architecture(self):
        """Generate a basic Mermaid architecture diagram."""
        if not self.data:
            return ""

        mermaid = ["```mermaid", "graph TD"]
        mermaid.append("    subgraph Repository")

        # Add files as nodes
        files = []
        for path, info in self.data.get('structure', {}).items():
            for f in info.get('files', []):
                if f.endswith('.py') or f.endswith('.js') or f.endswith('.ts'):
                    files.append(f)
                    node_id = f.replace('.', '_').replace('-', '_')
                    mermaid.append(f"        {node_id}[{f}]")

        mermaid.append("    end")

        # Add external dependencies
        frameworks = self.data.get('dependencies', {}).get('frameworks', [])
        if frameworks:
            mermaid.append("    subgraph Frameworks")
            for fw in frameworks:
                fw_id = f"fw_{fw.replace('-', '_')}"
                mermaid.append(f"        {fw_id}[{fw}]")
            mermaid.append("    end")

            # Link repository files to frameworks generally (simplified)
            for f in files:
                node_id = f.replace('.', '_').replace('-', '_')
                for fw in frameworks:
                    fw_id = f"fw_{fw.replace('-', '_')}"
                    # Just a dotted link to indicate use
                    mermaid.append(f"    {node_id} -.-> {fw_id}")

        mermaid.append("```")
        return "\n".join(mermaid)

    def generate_dependency_graph(self):
        """Generate a Mermaid dependency graph based on internal imports."""
        if not self.data:
            return ""

        mermaid = ["```mermaid", "graph LR"]
        kg = self.data.get('knowledge_graph', {})

        for module, imports in kg.items():
            mod_id = module.replace('.', '_').replace('-', '_')
            mermaid.append(f"    {mod_id}[{module}]")
            for imp in imports:
                imp_id = imp.replace('.', '_').replace('-', '_')
                mermaid.append(f"    {mod_id} --> {imp_id}[{imp}]")

        mermaid.append("```")
        return "\n".join(mermaid)

    def save_diagrams(self, output_dir='.github/docs'):
        os.makedirs(output_dir, exist_ok=True)

        arch_mermaid = self.generate_mermaid_architecture()
        with open(os.path.join(output_dir, 'architecture.md'), 'w', encoding='utf-8') as f:
            f.write("# Architecture Diagram\n\n")
            f.write(arch_mermaid)

        dep_mermaid = self.generate_dependency_graph()
        with open(os.path.join(output_dir, 'dependencies.md'), 'w', encoding='utf-8') as f:
            f.write("# Dependency Graph\n\n")
            f.write(dep_mermaid)

        print(f"Diagrams saved to {output_dir}")

if __name__ == '__main__':
    generator = DiagramGenerator()
    generator.save_diagrams()
