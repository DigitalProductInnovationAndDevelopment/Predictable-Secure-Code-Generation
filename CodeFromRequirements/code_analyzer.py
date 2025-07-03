import os
import ast
import json
import fnmatch
from typing import Dict, List, Any, Set
from pathlib import Path
from config import Config
import logging


class CodeAnalyzer:
    """Analyzes existing codebase structure and identifies required changes"""

    def __init__(self):
        self.config = Config()
        self.codebase_root = self.config.CODEBASE_ROOT
        self.supported_extensions = self.config.SUPPORTED_EXTENSIONS
        self.exclude_dirs = self.config.EXCLUDE_DIRS

    def analyze_codebase(self) -> Dict[str, Any]:
        """
        Analyze the current codebase structure

        Returns:
            Dict containing file structure, functions, classes, and dependencies
        """
        logging.info("Starting codebase analysis...")

        structure = {
            "files": {},
            "directories": [],
            "functions": {},
            "classes": {},
            "imports": {},
            "dependencies": set(),
            "file_count": 0,
            "total_lines": 0,
        }

        try:
            for root, dirs, files in os.walk(self.codebase_root):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

                rel_root = os.path.relpath(root, self.codebase_root)
                if rel_root != ".":
                    structure["directories"].append(rel_root)

                for file in files:
                    if self._should_analyze_file(file):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, self.codebase_root)

                        file_info = self._analyze_file(file_path)
                        if file_info:
                            structure["files"][rel_path] = file_info
                            structure["file_count"] += 1
                            structure["total_lines"] += file_info.get("line_count", 0)

                            # Merge functions and classes
                            structure["functions"].update(
                                file_info.get("functions", {})
                            )
                            structure["classes"].update(file_info.get("classes", {}))
                            structure["imports"].update(file_info.get("imports", {}))
                            structure["dependencies"].update(
                                file_info.get("dependencies", set())
                            )

            # Convert set to list for JSON serialization
            structure["dependencies"] = list(structure["dependencies"])

            logging.info(
                f"Analyzed {structure['file_count']} files, {structure['total_lines']} total lines"
            )
            return structure

        except Exception as e:
            logging.error(f"Error analyzing codebase: {str(e)}")
            return structure

    def _should_analyze_file(self, filename: str) -> bool:
        """Check if a file should be analyzed based on extension and ignore patterns"""
        # Check file extension
        if not any(filename.endswith(ext) for ext in self.supported_extensions):
            return False

        # Check ignore patterns
        ignore_patterns = self.config.get_ignored_patterns()
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False

        return True

    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file and extract metadata"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            file_info = {
                "path": file_path,
                "size": len(content),
                "line_count": len(content.splitlines()),
                "functions": {},
                "classes": {},
                "imports": {},
                "dependencies": set(),
                "last_modified": os.path.getmtime(file_path),
            }

            # Analyze Python files with AST
            if file_path.endswith(".py"):
                file_info.update(self._analyze_python_file(content))
            else:
                # For other files, do basic analysis
                file_info.update(self._analyze_generic_file(content))

            return file_info

        except Exception as e:
            logging.warning(f"Error analyzing file {file_path}: {str(e)}")
            return None

    def _analyze_python_file(self, content: str) -> Dict[str, Any]:
        """Analyze Python file using AST"""
        analysis = {
            "functions": {},
            "classes": {},
            "imports": {},
            "dependencies": set(),
        }

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"][node.name] = {
                        "name": node.name,
                        "line_number": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                        "decorators": [
                            self._get_decorator_name(dec) for dec in node.decorator_list
                        ],
                    }

                elif isinstance(node, ast.ClassDef):
                    analysis["classes"][node.name] = {
                        "name": node.name,
                        "line_number": node.lineno,
                        "bases": [self._get_base_name(base) for base in node.bases],
                        "methods": [],
                        "docstring": ast.get_docstring(node),
                    }

                    # Get class methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            analysis["classes"][node.name]["methods"].append(item.name)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"][alias.name] = {
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                        }
                        analysis["dependencies"].add(alias.name.split(".")[0])

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            import_key = f"{node.module}.{alias.name}"
                            analysis["imports"][import_key] = {
                                "type": "from_import",
                                "module": node.module,
                                "name": alias.name,
                                "alias": alias.asname,
                            }
                        analysis["dependencies"].add(node.module.split(".")[0])

        except SyntaxError as e:
            logging.warning(f"Syntax error in Python file: {str(e)}")
        except Exception as e:
            logging.warning(f"Error parsing Python file: {str(e)}")

        return analysis

    def _analyze_generic_file(self, content: str) -> Dict[str, Any]:
        """Basic analysis for non-Python files"""
        analysis = {
            "functions": {},
            "classes": {},
            "imports": {},
            "dependencies": set(),
        }

        # Basic pattern matching for common programming constructs
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            line = line.strip()

            # Look for function-like patterns
            if any(pattern in line for pattern in ["function ", "def ", "func "]):
                # Extract function name (basic regex would be better)
                parts = line.split()
                if len(parts) > 1:
                    analysis["functions"][f"line_{i}"] = {
                        "name": parts[1].split("(")[0],
                        "line_number": i,
                        "full_line": line,
                    }

            # Look for import patterns
            if any(pattern in line for pattern in ["import ", "require(", "#include"]):
                analysis["imports"][f"line_{i}"] = {"line_number": i, "full_line": line}

        return analysis

    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        else:
            return str(decorator)

    def _get_base_name(self, base) -> str:
        """Extract base class name from AST node"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{base.value.id}.{base.attr}"
        else:
            return str(base)

    def identify_changes(
        self,
        code_structure: Dict[str, Any],
        metadata: Dict[str, Any],
        requirements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Identify what changes need to be made based on requirements

        Returns:
            Dict containing files to modify, create, and specific changes needed
        """
        changes = {
            "files_to_modify": [],
            "files_to_create": [],
            "dependencies_to_add": [],
            "functions_to_add": [],
            "classes_to_add": [],
            "tests_to_create": [],
            "requirements_mapping": {},
        }

        for requirement in requirements:
            req_id = requirement.get("id", "")
            req_name = requirement.get("name", "")
            req_description = requirement.get("description", "")
            req_category = requirement.get("category", "General")

            logging.info(f"Analyzing requirement: {req_id} - {req_name}")

            # Map requirement to potential changes
            req_changes = self._map_requirement_to_changes(
                requirement, code_structure, metadata
            )

            changes["requirements_mapping"][req_id] = req_changes

            # Merge changes
            changes["files_to_modify"].extend(req_changes.get("files_to_modify", []))
            changes["files_to_create"].extend(req_changes.get("files_to_create", []))
            changes["dependencies_to_add"].extend(
                req_changes.get("dependencies_to_add", [])
            )
            changes["functions_to_add"].extend(req_changes.get("functions_to_add", []))
            changes["classes_to_add"].extend(req_changes.get("classes_to_add", []))
            changes["tests_to_create"].extend(req_changes.get("tests_to_create", []))

        # Remove duplicates
        for key in changes:
            if isinstance(changes[key], list) and key != "requirements_mapping":
                changes[key] = list(set(changes[key]))

        return changes

    def _map_requirement_to_changes(
        self,
        requirement: Dict[str, Any],
        code_structure: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Map a single requirement to specific code changes"""
        req_changes = {
            "files_to_modify": [],
            "files_to_create": [],
            "dependencies_to_add": [],
            "functions_to_add": [],
            "classes_to_add": [],
            "tests_to_create": [],
        }

        req_name = requirement.get("name", "").lower()
        req_description = requirement.get("description", "").lower()
        req_category = requirement.get("category", "").lower()

        # Simple heuristics based on keywords (can be enhanced with ML/NLP)

        # Authentication-related requirements
        if any(
            keyword in req_name or keyword in req_description
            for keyword in ["auth", "login", "user", "jwt", "token"]
        ):
            req_changes["files_to_create"].extend(
                [
                    "auth/authentication.py",
                    "auth/models.py",
                    "tests/test_authentication.py",
                ]
            )
            req_changes["dependencies_to_add"].extend(["pyjwt", "bcrypt"])

        # Database-related requirements
        if any(
            keyword in req_name or keyword in req_description
            for keyword in ["database", "db", "migration", "sql"]
        ):
            req_changes["files_to_create"].extend(
                [
                    "database/migrations.py",
                    "database/models.py",
                    "tests/test_database.py",
                ]
            )
            req_changes["dependencies_to_add"].extend(["sqlalchemy", "alembic"])

        # API-related requirements
        if any(
            keyword in req_name or keyword in req_description
            for keyword in ["api", "endpoint", "rest", "http"]
        ):
            req_changes["files_to_modify"].extend(["function_app.py"])
            req_changes["files_to_create"].extend(
                [
                    f'api/{req_name.replace(" ", "_")}.py',
                    f'tests/test_{req_name.replace(" ", "_")}.py',
                ]
            )

        # General new feature
        if not req_changes["files_to_create"] and not req_changes["files_to_modify"]:
            feature_name = req_name.replace(" ", "_").replace("-", "_")
            req_changes["files_to_create"].extend(
                [f"features/{feature_name}.py", f"tests/test_{feature_name}.py"]
            )

        return req_changes
