#!/usr/bin/env python3
"""
Cold Run Analysis Module for Code Generation Process

This module performs a comprehensive analysis of codebases to determine:
1. Programming language identification
2. Architecture pattern detection
3. Project structure analysis

It integrates with the existing AI client for intelligent analysis.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse

# Add the platform src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from client import AzureOpenAIClient


@dataclass
class FileInfo:
    """Information about a single file in the project."""

    path: str
    name: str
    extension: str
    size_bytes: int
    is_directory: bool
    language: Optional[str] = None


@dataclass
class ProjectStructure:
    """Complete project structure analysis."""

    root_path: str
    total_files: int
    total_directories: int
    file_extensions: List[str]
    languages_detected: List[str]
    files: List[FileInfo]
    architecture_hints: List[str]
    framework_indicators: List[str]


class ColdRunAnalyzer:
    """Professional cold run analyzer for code generation projects."""

    def __init__(self, ai_client: Optional[AzureOpenAIClient] = None):
        """Initialize the analyzer with optional AI client."""
        self.ai_client = ai_client
        self._setup_logging()

        # Language detection patterns
        self.language_patterns = {
            "python": [".py", ".pyi", ".pyx", ".pyw"],
            "typescript": [".ts", ".tsx"],
            "javascript": [".js", ".jsx", ".mjs"],
            "java": [".java", ".class"],
            "csharp": [".cs", ".csproj"],
            "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
            "c": [".c", ".h"],
            "go": [".go"],
            "rust": [".rs"],
            "php": [".php"],
            "ruby": [".rb"],
            "swift": [".swift"],
            "kotlin": [".kt", ".kts"],
            "scala": [".scala"],
            "r": [".r", ".R"],
            "matlab": [".m"],
            "perl": [".pl", ".pm"],
            "shell": [".sh", ".bash", ".zsh", ".fish"],
            "powershell": [".ps1"],
            "yaml": [".yml", ".yaml"],
            "json": [".json"],
            "xml": [".xml"],
            "html": [".html", ".htm"],
            "css": [".css", ".scss", ".sass", ".less"],
            "sql": [".sql"],
            "docker": ["Dockerfile", ".dockerignore"],
            "terraform": [".tf", ".tfvars"],
            "kubernetes": [".yaml", ".yml"],
        }

        # Architecture detection patterns
        self.architecture_patterns = {
            "mvc": ["controller", "model", "view", "service"],
            "mvvm": ["viewmodel", "model", "view"],
            "clean_architecture": ["domain", "usecase", "repository", "presentation"],
            "hexagonal": ["port", "adapter", "domain"],
            "layered": ["layer", "tier", "presentation", "business", "data"],
            "microservices": ["service", "microservice", "gateway", "discovery"],
            "monolithic": ["monolith", "single", "unified"],
            "event_driven": ["event", "listener", "publisher", "subscriber"],
            "cqs": ["command", "query", "handler"],
            "ddd": ["domain", "aggregate", "entity", "valueobject"],
            "repository": ["repository", "dao", "dataaccess"],
            "factory": ["factory", "builder", "creator"],
            "observer": ["observer", "subject", "notify"],
            "strategy": ["strategy", "algorithm", "policy"],
            "adapter": ["adapter", "wrapper", "bridge"],
            "decorator": ["decorator", "wrapper"],
            "proxy": ["proxy", "surrogate"],
            "singleton": ["singleton", "instance"],
            "command": ["command", "action", "operation"],
            "template_method": ["template", "algorithm"],
        }

        # Framework detection patterns
        self.framework_patterns = {
            "django": ["django", "settings.py", "urls.py", "views.py"],
            "flask": ["flask", "app.py", "blueprint"],
            "fastapi": ["fastapi", "uvicorn", "app.py"],
            "spring": ["spring", "application.java", "controller"],
            "express": ["express", "app.js", "server.js"],
            "react": ["react", "jsx", "component"],
            "angular": ["angular", "component", "service"],
            "vue": ["vue", "component", "template"],
            "laravel": ["laravel", "artisan", "routes"],
            "rails": ["rails", "gemfile", "controller"],
            "aspnet": ["aspnet", "web.config", "global.asax"],
            "dotnet": [".csproj", ".sln", "program.cs"],
            "flutter": ["flutter", "pubspec.yaml", "main.dart"],
            "react_native": ["react-native", "metro.config.js"],
            "xamarin": ["xamarin", ".csproj"],
            "ionic": ["ionic", "angular.json"],
            "cordova": ["cordova", "config.xml"],
            "electron": ["electron", "main.js", "package.json"],
            "tauri": ["tauri", "tauri.conf.json"],
            "nextjs": ["next", "next.config.js"],
            "nuxt": ["nuxt", "nuxt.config.js"],
            "gatsby": ["gatsby", "gatsby-config.js"],
            "svelte": ["svelte", "svelte.config.js"],
            "solid": ["solid", "solid.config.js"],
            "qwik": ["qwik", "qwik.config.js"],
        }

    def _setup_logging(self):
        """Setup professional logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("cold_run_analysis.log"),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def analyze_project_structure(self, project_path: Path) -> ProjectStructure:
        """
        Analyze the complete project structure.

        Args:
            project_path: Path to the project root

        Returns:
            ProjectStructure object with complete analysis
        """
        self.logger.info(f"Starting project structure analysis for: {project_path}")

        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        # Collect file information
        files_info = []
        extensions = set()
        languages = set()

        # Walk through the project
        for item in project_path.rglob("*"):
            # Skip common ignored directories
            if any(
                ignored in str(item)
                for ignored in [
                    ".git",
                    "__pycache__",
                    "node_modules",
                    ".venv",
                    "venv",
                    "dist",
                    "build",
                ]
            ):
                continue

            file_info = FileInfo(
                path=str(item.relative_to(project_path)),
                name=item.name,
                extension=item.suffix.lower(),
                size_bytes=item.stat().st_size if item.is_file() else 0,
                is_directory=item.is_dir(),
            )

            # Detect language from extension
            if item.is_file():
                file_info.language = self._detect_language_from_extension(item.suffix)
                if file_info.language:
                    languages.add(file_info.language)

                if item.suffix:
                    extensions.add(item.suffix.lower())

            files_info.append(file_info)

        # Analyze architecture and framework patterns
        architecture_hints = self._detect_architecture_patterns(files_info)
        framework_indicators = self._detect_framework_patterns(files_info)

        project_structure = ProjectStructure(
            root_path=str(project_path),
            total_files=len([f for f in files_info if not f.is_directory]),
            total_directories=len([f for f in files_info if f.is_directory]),
            file_extensions=sorted(list(extensions)),
            languages_detected=sorted(list(languages)),
            files=files_info,
            architecture_hints=architecture_hints,
            framework_indicators=framework_indicators,
        )

        self.logger.info(
            f"Analysis complete. Found {len(languages)} languages, {len(extensions)} file types"
        )
        return project_structure

    def _detect_language_from_extension(self, extension: str) -> Optional[str]:
        """Detect programming language from file extension."""
        ext_lower = extension.lower()
        for language, patterns in self.language_patterns.items():
            if ext_lower in patterns:
                return language
        return None

    def _detect_architecture_patterns(self, files_info: List[FileInfo]) -> List[str]:
        """Detect architecture patterns from file and directory names."""
        detected_patterns = []
        all_names = [f.name.lower() for f in files_info] + [f.path.lower() for f in files_info]

        for pattern_name, keywords in self.architecture_patterns.items():
            if any(keyword in " ".join(all_names) for keyword in keywords):
                detected_patterns.append(pattern_name)

        return detected_patterns

    def _detect_framework_patterns(self, files_info: List[FileInfo]) -> List[str]:
        """Detect framework patterns from file and directory names."""
        detected_frameworks = []
        all_names = [f.name.lower() for f in files_info] + [f.path.lower() for f in files_info]

        for framework_name, keywords in self.framework_patterns.items():
            if any(keyword in " ".join(all_names) for keyword in keywords):
                detected_frameworks.append(framework_name)

        return detected_frameworks

    def generate_ai_analysis(self, project_structure: ProjectStructure) -> Dict[str, Any]:
        """
        Use AI to analyze the project structure and generate insights.

        Args:
            project_structure: The analyzed project structure

        Returns:
            AI-generated analysis results
        """
        if not self.ai_client:
            self.logger.warning("No AI client available, skipping AI analysis")
            return {"status": "no_ai_client", "message": "AI analysis not available"}

        try:
            # Create a comprehensive prompt for AI analysis
            prompt = self._build_ai_analysis_prompt(project_structure)

            # Get AI analysis
            result = self.ai_client.ask_question(
                question=prompt,
                system_prompt="You are an expert software architect and developer. Analyze the provided project structure and provide detailed insights about the programming language and architecture patterns used.",
                max_tokens=2000,
                temperature=0.1,
            )

            if result["status"] == "success":
                # Try to parse JSON from AI response
                try:
                    # Extract JSON from the response (AI might wrap it in markdown)
                    response_text = result["answer"]
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        json_content = response_text[json_start:json_end].strip()
                    elif "```" in response_text:
                        json_start = response_text.find("```") + 3
                        json_end = response_text.find("```", json_start)
                        json_content = response_text[json_start:json_end].strip()
                    else:
                        json_content = response_text

                    ai_analysis = json.loads(json_content)
                    ai_analysis["status"] = "success"
                    ai_analysis["tokens_used"] = result["usage"]["total_tokens"]
                    return ai_analysis

                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse AI response as JSON: {e}")
                    return {
                        "status": "parse_error",
                        "raw_response": result["answer"],
                        "tokens_used": result["usage"]["total_tokens"],
                    }
            else:
                return {
                    "status": "ai_error",
                    "error": result.get("error", "Unknown AI error"),
                    "tokens_used": 0,
                }

        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return {"status": "exception", "error": str(e), "tokens_used": 0}

    def _build_ai_analysis_prompt(self, project_structure: ProjectStructure) -> str:
        """Build a comprehensive prompt for AI analysis."""
        prompt = f"""
Please analyze this project structure and provide a JSON response with the following information:

1. **Programming Language Analysis:**
   - Primary programming language(s) used
   - Secondary languages if any
   - Confidence level in language detection (0-100%)

2. **Architecture Pattern Analysis:**
   - Main architecture pattern(s) detected
   - Supporting patterns
   - Confidence level in architecture detection (0-100%)

3. **Framework Analysis:**
   - Main framework(s) used
   - Supporting libraries/frameworks
   - Version indicators if detectable

4. **Project Type Classification:**
   - Web application, mobile app, desktop app, library, etc.
   - Development approach (monolithic, microservices, etc.)

5. **Code Quality Indicators:**
   - Project structure quality
   - Testing presence
   - Documentation indicators

6. **Recommendations:**
   - Suggested improvements
   - Best practices to follow
   - Potential refactoring opportunities

**Project Structure:**
- Root: {project_structure.root_path}
- Total Files: {project_structure.total_files}
- Total Directories: {project_structure.total_directories}
- Languages Detected: {', '.join(project_structure.languages_detected)}
- File Extensions: {', '.join(project_structure.file_extensions[:20])}
- Architecture Hints: {', '.join(project_structure.architecture_hints)}
- Framework Indicators: {', '.join(project_structure.framework_indicators)}

**Sample Files:**
{chr(10).join([f"- {f.path} ({f.language or 'unknown'})" for f in project_structure.files[:50]])}

Please provide your analysis in valid JSON format with the structure above. Be specific and confident in your assessments.
"""
        return prompt

    def save_analysis_results(
        self, project_structure: ProjectStructure, ai_analysis: Dict[str, Any], output_path: Path
    ) -> None:
        """
        Save the complete analysis results to JSON file.

        Args:
            project_structure: The analyzed project structure
            ai_analysis: AI-generated analysis results
            output_path: Path to save the results
        """
        # Prepare the complete results
        results = {
            "metadata": {
                "analysis_timestamp": str(Path().cwd()),
                "analyzer_version": "1.0.0",
                "project_path": project_structure.root_path,
            },
            "project_structure": asdict(project_structure),
            "ai_analysis": ai_analysis,
            "summary": {
                "primary_language": ai_analysis.get("primary_language", "unknown"),
                "architecture_pattern": ai_analysis.get("architecture_pattern", "unknown"),
                "framework": ai_analysis.get("framework", "unknown"),
                "project_type": ai_analysis.get("project_type", "unknown"),
                "confidence_score": ai_analysis.get("confidence_score", 0),
            },
        }

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Analysis results saved to: {output_path}")

    def run_complete_analysis(self, project_path: Path, output_path: Path) -> Dict[str, Any]:
        """
        Run the complete cold run analysis.

        Args:
            project_path: Path to the project to analyze
            output_path: Path to save the analysis results

        Returns:
            Complete analysis results
        """
        self.logger.info("Starting complete cold run analysis")

        try:
            # Step 1: Analyze project structure
            project_structure = self.analyze_project_structure(project_path)

            # Step 2: Generate AI analysis
            ai_analysis = self.generate_ai_analysis(project_structure)

            # Step 3: Save results
            self.save_analysis_results(project_structure, ai_analysis, output_path)

            # Step 4: Return summary
            summary = {
                "status": "success",
                "project_path": str(project_path),
                "output_path": str(output_path),
                "languages_detected": project_structure.languages_detected,
                "architecture_hints": project_structure.architecture_hints,
                "framework_indicators": project_structure.framework_indicators,
                "ai_analysis_status": ai_analysis.get("status", "unknown"),
                "total_files_analyzed": project_structure.total_files,
            }

            self.logger.info("Cold run analysis completed successfully")
            return summary

        except Exception as e:
            error_msg = f"Cold run analysis failed: {str(e)}"
            self.logger.error(error_msg)
            return {"status": "error", "error": error_msg}


def main():
    """Main entry point for command line usage."""
    parser = argparse.ArgumentParser(
        description="Cold Run Analysis for Code Generation Projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory and save to analysis.json
  python cold_run.py . analysis.json
  
  # Analyze specific project with verbose output
  python cold_run.py /path/to/project results/analysis.json --verbose
  
  # Test AI connection first
  python cold_run.py --test-ai
        """,
    )

    parser.add_argument(
        "project_path",
        nargs="?",
        type=Path,
        help="Path to the project to analyze (default: current directory)",
    )

    parser.add_argument(
        "output_path",
        nargs="?",
        type=Path,
        help="Path to save the analysis results (default: cold_run_analysis.json)",
    )

    parser.add_argument(
        "--test-ai", action="store_true", help="Test AI client connection before running analysis"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    parser.add_argument(
        "--no-ai", action="store_true", help="Skip AI analysis (structure analysis only)"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize AI client (optional)
        ai_client = None
        if not args.no_ai:
            try:
                ai_client = AzureOpenAIClient()
                if args.test_ai:
                    print("Testing AI connection...")
                    if ai_client.test_connection():
                        print("✅ AI connection successful!")
                    else:
                        print("❌ AI connection failed!")
                        return 1
            except Exception as e:
                print(f"⚠️  AI client initialization failed: {e}")
                print("Continuing without AI analysis...")
                ai_client = None

        # Initialize analyzer
        analyzer = ColdRunAnalyzer(ai_client)

        # Set default paths if not provided
        project_path = args.project_path or Path.cwd()
        output_path = args.output_path or Path("cold_run_analysis.json")

        # Run analysis
        print(f"🔍 Analyzing project: {project_path}")
        print(f"📁 Output will be saved to: {output_path}")
        print("-" * 50)

        results = analyzer.run_complete_analysis(project_path, output_path)

        if results["status"] == "success":
            print("✅ Analysis completed successfully!")
            print(f"📊 Languages detected: {', '.join(results['languages_detected'])}")
            print(f"🏗️  Architecture hints: {', '.join(results['architecture_hints'])}")
            print(f"🔧 Framework indicators: {', '.join(results['framework_indicators'])}")
            print(f"📄 Results saved to: {results['output_path']}")
            return 0
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
