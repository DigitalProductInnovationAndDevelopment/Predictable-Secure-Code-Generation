"""
Requirement analyzer for identifying missing functionality and planning implementation.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

import sys

sys.path.append(str(Path(__file__).parent.parent))
from models.requirement_data import RequirementData, RequirementStatus
from models.generation_result import GenerationResult, GenerationStatus


class RequirementAnalyzer:
    """Analyzes requirements against existing codebase metadata."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the analyzer."""
        self.logger = logger or logging.getLogger(__name__)

    def analyze_requirements(
        self,
        requirements: Dict[str, str],
        metadata: Dict[str, Any],
        result: GenerationResult,
    ) -> List[RequirementData]:
        """
        Analyze requirements against metadata to determine implementation needs.

        Args:
            requirements: Dictionary of requirement_id -> description
            metadata: Project metadata from GenerateMetadataFromCode
            result: Generation result to update with analysis info

        Returns:
            List of RequirementData objects with analysis results
        """
        self.logger.info(f"Analyzing {len(requirements)} requirements against metadata")

        requirement_objects = []

        for req_id, description in requirements.items():
            try:
                req_data = self._analyze_single_requirement(
                    req_id, description, metadata
                )
                requirement_objects.append(req_data)
                self.logger.debug(
                    f"Analyzed requirement {req_id}: {req_data.status.value}"
                )

            except Exception as e:
                self.logger.error(f"Error analyzing requirement {req_id}: {str(e)}")
                req_data = RequirementData(
                    req_id, description, RequirementStatus.FAILED
                )
                req_data.mark_failed(f"Analysis failed: {str(e)}")
                requirement_objects.append(req_data)
                result.add_problem(
                    "error",
                    "requirement",
                    f"Failed to analyze requirement {req_id}: {str(e)}",
                    requirement_id=req_id,
                )

        # Update result with analysis statistics
        result.requirements_analyzed = len(requirement_objects)

        self.logger.info(
            f"Analysis complete. {len(requirement_objects)} requirements processed"
        )
        return requirement_objects

    def _analyze_single_requirement(
        self, req_id: str, description: str, metadata: Dict[str, Any]
    ) -> RequirementData:
        """Analyze a single requirement against the metadata."""
        req_data = RequirementData(req_id, description)

        # Extract keywords from requirement description
        keywords = self._extract_keywords(description)

        # Check if functionality already exists
        existing_coverage = self._check_existing_coverage(keywords, metadata)

        # Determine complexity and implementation strategy
        complexity = self._assess_complexity(description, keywords)
        req_data.complexity_score = complexity

        # Determine target files for implementation
        target_files = self._determine_target_files(
            keywords, metadata, existing_coverage
        )
        req_data.target_files = target_files

        # Set implementation notes
        req_data.implementation_notes = self._generate_implementation_notes(
            description, keywords, existing_coverage, target_files
        )

        # Determine dependencies
        dependencies = self._identify_dependencies(keywords, metadata)
        req_data.dependencies = dependencies

        self.logger.debug(
            f"Requirement {req_id} analysis: "
            f"complexity={complexity:.2f}, "
            f"targets={len(target_files)}, "
            f"deps={len(dependencies)}"
        )

        return req_data

    def _extract_keywords(self, description: str) -> List[str]:
        """Extract relevant keywords from requirement description."""
        # Simple keyword extraction - can be enhanced with NLP
        keywords = []

        # Math operations
        math_keywords = [
            "add",
            "addition",
            "sum",
            "subtract",
            "subtraction",
            "minus",
            "multiply",
            "multiplication",
            "times",
            "divide",
            "division",
            "calculate",
            "compute",
            "operation",
            "arithmetic",
        ]

        # Data structures
        data_keywords = [
            "list",
            "array",
            "string",
            "number",
            "integer",
            "float",
            "dictionary",
            "set",
            "tuple",
            "collection",
        ]

        # Actions
        action_keywords = [
            "create",
            "generate",
            "build",
            "implement",
            "add",
            "modify",
            "update",
            "delete",
            "remove",
            "validate",
            "check",
            "verify",
            "test",
            "parse",
            "format",
        ]

        # UI/Interface
        ui_keywords = [
            "interface",
            "ui",
            "user",
            "input",
            "output",
            "display",
            "menu",
            "option",
            "choice",
            "prompt",
            "cli",
            "command",
        ]

        all_keywords = math_keywords + data_keywords + action_keywords + ui_keywords

        description_lower = description.lower()
        for keyword in all_keywords:
            if keyword in description_lower:
                keywords.append(keyword)

        return list(set(keywords))  # Remove duplicates

    def _check_existing_coverage(
        self, keywords: List[str], metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check how much of the requirement is already covered by existing code."""
        coverage = {"functions": [], "classes": [], "files": [], "coverage_score": 0.0}

        if "files" not in metadata:
            return coverage

        total_matches = 0
        keyword_count = len(keywords)

        if keyword_count == 0:
            return coverage

        for file_info in metadata["files"]:
            file_path = file_info.get("path", "")

            # Check functions
            for func in file_info.get("functions", []):
                func_name = func.get("name", "").lower()
                func_doc = func.get("docstring", "").lower()

                matches = sum(1 for kw in keywords if kw in func_name or kw in func_doc)
                if matches > 0:
                    coverage["functions"].append(
                        {
                            "name": func.get("name"),
                            "file": file_path,
                            "matches": matches,
                            "docstring": func.get("docstring", ""),
                        }
                    )
                    total_matches += matches

            # Check classes
            for cls in file_info.get("classes", []):
                cls_name = cls.get("name", "").lower()
                cls_doc = cls.get("docstring", "").lower()

                matches = sum(1 for kw in keywords if kw in cls_name or kw in cls_doc)
                if matches > 0:
                    coverage["classes"].append(
                        {
                            "name": cls.get("name"),
                            "file": file_path,
                            "matches": matches,
                            "docstring": cls.get("docstring", ""),
                        }
                    )
                    total_matches += matches

                # Check methods
                for method in cls.get("methods", []):
                    method_name = method.get("name", "").lower()
                    method_doc = method.get("docstring", "").lower()

                    matches = sum(
                        1 for kw in keywords if kw in method_name or kw in method_doc
                    )
                    if matches > 0:
                        coverage["functions"].append(
                            {
                                "name": f"{cls.get('name')}.{method.get('name')}",
                                "file": file_path,
                                "matches": matches,
                                "docstring": method.get("docstring", ""),
                            }
                        )
                        total_matches += matches

        # Calculate coverage score
        coverage["coverage_score"] = min(
            total_matches / (keyword_count * 2), 1.0
        )  # Normalize

        return coverage

    def _assess_complexity(self, description: str, keywords: List[str]) -> float:
        """Assess the complexity of implementing the requirement."""
        complexity = 1.0  # Base complexity

        # Increase complexity based on keywords
        complexity_modifiers = {
            "validate": 0.3,
            "error": 0.3,
            "exception": 0.3,
            "test": 0.2,
            "interface": 0.4,
            "ui": 0.5,
            "database": 0.6,
            "api": 0.5,
            "async": 0.4,
            "thread": 0.4,
            "network": 0.5,
            "file": 0.2,
            "parse": 0.3,
            "format": 0.2,
            "sort": 0.2,
            "search": 0.3,
            "algorithm": 0.4,
        }

        for keyword in keywords:
            if keyword in complexity_modifiers:
                complexity += complexity_modifiers[keyword]

        # Increase complexity based on description length and complexity indicators
        if len(description.split()) > 20:
            complexity += 0.2

        if any(
            word in description.lower()
            for word in ["complex", "advanced", "sophisticated"]
        ):
            complexity += 0.3

        if any(
            word in description.lower() for word in ["multiple", "various", "different"]
        ):
            complexity += 0.2

        return min(complexity, 5.0)  # Cap at 5.0

    def _determine_target_files(
        self,
        keywords: List[str],
        metadata: Dict[str, Any],
        existing_coverage: Dict[str, Any],
    ) -> List[str]:
        """Determine which files should be targeted for implementation."""
        target_files = []

        # If there's existing coverage, prefer those files
        if existing_coverage["coverage_score"] > 0.3:
            covered_files = set()
            for func in existing_coverage["functions"]:
                covered_files.add(func["file"])
            for cls in existing_coverage["classes"]:
                covered_files.add(cls["file"])
            target_files.extend(list(covered_files))

        # Look for main implementation files
        if "files" in metadata:
            for file_info in metadata["files"]:
                file_path = file_info.get("path", "")

                # Prefer main implementation files over test files
                if not any(
                    test_dir in file_path
                    for test_dir in ["test", "tests", "__pycache__"]
                ):
                    # Check if file seems relevant based on name
                    file_name = Path(file_path).name.lower()
                    if any(kw in file_name for kw in keywords):
                        if file_path not in target_files:
                            target_files.append(file_path)

        # If no specific targets found, suggest main files
        if not target_files and "files" in metadata:
            main_files = []
            for file_info in metadata["files"]:
                file_path = file_info.get("path", "")
                if file_path.endswith("main.py") or file_path.endswith("__init__.py"):
                    continue
                if not any(
                    test_dir in file_path
                    for test_dir in ["test", "tests", "__pycache__"]
                ):
                    main_files.append(file_path)

            # Sort by file size (prefer files with more content)
            main_files.sort(
                key=lambda f: len(
                    [fi for fi in metadata["files"] if fi["path"] == f][0].get(
                        "functions", []
                    )
                    + [fi for fi in metadata["files"] if fi["path"] == f][0].get(
                        "classes", []
                    )
                ),
                reverse=True,
            )

            if main_files:
                target_files.append(main_files[0])  # Use the main implementation file

        return target_files

    def _generate_implementation_notes(
        self,
        description: str,
        keywords: List[str],
        existing_coverage: Dict[str, Any],
        target_files: List[str],
    ) -> str:
        """Generate implementation notes for the requirement."""
        notes = []

        if existing_coverage["coverage_score"] > 0.5:
            notes.append(
                "High existing coverage - consider extending existing functionality"
            )
        elif existing_coverage["coverage_score"] > 0.2:
            notes.append("Some existing coverage - can build upon existing code")
        else:
            notes.append("New functionality - implement from scratch")

        if target_files:
            notes.append(f"Suggested target files: {', '.join(target_files)}")
        else:
            notes.append("Create new file for implementation")

        # Add specific implementation hints based on keywords
        if "validate" in keywords or "error" in keywords:
            notes.append("Include proper error handling and validation")

        if "test" in keywords:
            notes.append("Generate comprehensive test cases")

        if "interface" in keywords or "ui" in keywords:
            notes.append("Consider user interface design and usability")

        return "; ".join(notes)

    def _identify_dependencies(
        self, keywords: List[str], metadata: Dict[str, Any]
    ) -> List[str]:
        """Identify potential dependencies for the requirement."""
        dependencies = []

        # Check existing dependencies in metadata
        if "dependencies" in metadata:
            external_deps = metadata["dependencies"].get("external_dependencies", [])
            internal_deps = metadata["dependencies"].get("internal_dependencies", [])

            # Suggest relevant existing dependencies
            for dep in external_deps + internal_deps:
                dep_lower = dep.lower()
                if any(kw in dep_lower for kw in keywords):
                    dependencies.append(dep)

        # Suggest new dependencies based on keywords
        dependency_suggestions = {
            "test": ["pytest", "unittest"],
            "validate": ["pydantic", "marshmallow"],
            "parse": ["argparse", "configparser"],
            "format": ["datetime", "json"],
            "file": ["pathlib", "os"],
            "network": ["requests", "urllib"],
            "database": ["sqlite3", "sqlalchemy"],
            "ui": ["tkinter", "PyQt", "streamlit"],
            "api": ["fastapi", "flask", "requests"],
        }

        for keyword in keywords:
            if keyword in dependency_suggestions:
                for dep in dependency_suggestions[keyword]:
                    if dep not in dependencies:
                        dependencies.append(dep)

        return dependencies
