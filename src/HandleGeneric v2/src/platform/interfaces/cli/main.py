"""Main CLI application for the platform."""

import json
import typer
from pathlib import Path
from typing import List, Optional, Set
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from platform.kernel.di import build_app
from platform.domain.models.requirements import Requirement
from platform.app.s1_codegen.use_cases import GenerateFromRequirements
from platform.app.s2_metadata.use_cases import GenerateMetadata
from platform.app.s3_validation.use_cases import ValidationPipeline

app = typer.Typer(help="Enterprise-grade code generation platform with three first-class services")
console = Console()


def parse_requirements_json(content: str) -> List[Requirement]:
    """Parse requirements from JSON content."""
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return [Requirement(**req) for req in data]
        else:
            return [Requirement(**data)]
    except Exception as e:
        typer.echo(f"Error parsing requirements: {e}", err=True)
        raise typer.Exit(1)


@app.command("s1-generate")
def s1_generate(
    requirements_file: Path = typer.Argument(..., help="Path to requirements JSON file"),
    language: str = typer.Argument(..., help="Target language (python, typescript, etc.)"),
    output_dir: Path = typer.Option("./generated", "-o", "--output", help="Output directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode (no actual generation)"),
    context_file: Optional[Path] = typer.Option(None, "--context", help="Context JSON file"),
):
    """S1 - Generate code from requirements."""
    console.print(Panel("🚀 Starting Code Generation", style="bold blue"))

    try:
        # Load requirements
        if not requirements_file.exists():
            console.print(f"❌ Requirements file not found: {requirements_file}", style="red")
            raise typer.Exit(1)

        requirements_content = requirements_file.read_text()
        requirements = parse_requirements_json(requirements_content)

        console.print(f"📋 Loaded {len(requirements)} requirements")

        # Load context if provided
        context = {}
        if context_file and context_file.exists():
            context = json.loads(context_file.read_text())
            console.print("🔧 Loaded generation context")

        # Build app and get services
        services = build_app()

        # Create use case
        use_case = GenerateFromRequirements(
            llm_client=services.llm_client, artifact_writer=services.artifact_writer
        )

        if dry_run:
            console.print("🔍 [DRY RUN] Would generate code with the following:", style="yellow")
            for req in requirements:
                console.print(f"  - {req.id}: {req.title}")
            return

        # Execute generation
        with console.status("[bold green]Generating code..."):
            report = use_case.execute(requirements, language, output_dir, context)

        # Display results
        console.print("✅ Code generation completed!", style="green")
        console.print(f"📁 Output directory: {output_dir}")
        console.print(f"📄 Files generated: {len(report.files)}")
        console.print(f"💰 Tokens used: {report.cost_tokens}")
        console.print(f"⏱️  Generation time: {report.generation_time_seconds:.2f}s")

        # Show generated files table
        table = Table(title="Generated Files")
        table.add_column("File", style="cyan")
        table.add_column("Language", style="green")
        table.add_column("Size", style="yellow")

        for file in report.files:
            table.add_row(file.path, file.language or language, f"{len(file.content)} chars")

        console.print(table)

    except Exception as e:
        console.print(f"❌ Generation failed: {e}", style="red")
        raise typer.Exit(1)


@app.command("s2-metadata")
def s2_metadata(
    project_path: Path = typer.Argument(..., help="Path to project directory"),
    output_file: Path = typer.Option(
        "metadata.json", "-o", "--output", help="Output metadata file"
    ),
    languages: Optional[str] = typer.Option(
        None, "-l", "--languages", help="Comma-separated list of languages to include"
    ),
    exclude_dirs: Optional[str] = typer.Option(
        None, "--exclude", help="Comma-separated list of directories to exclude"
    ),
):
    """S2 - Generate metadata from code files."""
    console.print(Panel("🔍 Starting Metadata Generation", style="bold green"))

    try:
        if not project_path.exists():
            console.print(f"❌ Project path not found: {project_path}", style="red")
            raise typer.Exit(1)

        # Parse options
        include_languages = set(languages.split(",")) if languages else None
        exclude_directories = set(exclude_dirs.split(",")) if exclude_dirs else None

        console.print(f"📂 Scanning project: {project_path}")
        if include_languages:
            console.print(f"🔧 Languages: {', '.join(include_languages)}")

        # Build app and get services
        services = build_app()

        # Create use case
        use_case = GenerateMetadata(file_system=services.file_system)

        # Execute metadata generation
        with console.status("[bold green]Extracting metadata..."):
            metadata = use_case.execute(
                project_path, include_languages=include_languages, exclude_dirs=exclude_directories
            )

        # Write metadata file
        output_file.write_text(metadata.model_dump_json(indent=2))

        # Display results
        console.print("✅ Metadata generation completed!", style="green")
        console.print(f"📄 Output file: {output_file}")
        console.print(f"🗂️  Files processed: {len(metadata.files)}")
        console.print(f"🏷️  Languages found: {', '.join(metadata.languages)}")

        # Show summary table
        table = Table(title="Project Summary")
        table.add_column("Language", style="cyan")
        table.add_column("Files", style="green")
        table.add_column("Functions", style="yellow")
        table.add_column("Classes", style="magenta")
        table.add_column("LOC", style="red")

        for lang in metadata.languages:
            lang_files = [f for f in metadata.files if f.language == lang]
            total_functions = sum(len(f.functions) for f in lang_files)
            total_classes = sum(len(f.classes) for f in lang_files)
            total_loc = sum(f.loc for f in lang_files)

            table.add_row(
                lang, str(len(lang_files)), str(total_functions), str(total_classes), str(total_loc)
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ Metadata generation failed: {e}", style="red")
        raise typer.Exit(1)


@app.command("s3-validate")
def s3_validate(
    project_path: Path = typer.Argument(..., help="Path to project directory"),
    requirements_file: Optional[Path] = typer.Option(
        None, "-r", "--requirements", help="Requirements file for AI logic check"
    ),
    metadata_file: Optional[Path] = typer.Option(
        None, "-m", "--metadata", help="Metadata file (from s2-metadata)"
    ),
    run_tests: bool = typer.Option(True, "--tests/--no-tests", help="Run tests"),
    ai_check: bool = typer.Option(False, "--ai-check", help="Enable AI logic validation"),
    output_file: Optional[Path] = typer.Option(
        None, "-o", "--output", help="Output validation report file"
    ),
):
    """S3 - Validate code (syntax → tests → AI logic)."""
    console.print(Panel("🔍 Starting Validation Pipeline", style="bold yellow"))

    try:
        if not project_path.exists():
            console.print(f"❌ Project path not found: {project_path}", style="red")
            raise typer.Exit(1)

        # Load optional inputs
        requirements = None
        if requirements_file and requirements_file.exists():
            requirements_content = requirements_file.read_text()
            requirements = parse_requirements_json(requirements_content)
            console.print(f"📋 Loaded {len(requirements)} requirements")

        metadata = None
        if metadata_file and metadata_file.exists():
            from platform.domain.models.metadata import ProjectMetadata

            metadata_content = json.loads(metadata_file.read_text())
            metadata = ProjectMetadata(**metadata_content)
            console.print(f"🗂️  Loaded metadata for {len(metadata.files)} files")

        console.print(f"📂 Validating project: {project_path}")
        console.print(f"🧪 Run tests: {'Yes' if run_tests else 'No'}")
        console.print(f"🤖 AI check: {'Yes' if ai_check else 'No'}")

        # Build app and get services
        services = build_app()

        # Create use case
        use_case = ValidationPipeline(
            file_system=services.file_system,
            test_runner=services.pytest_runner,
            sandbox=services.sandbox,
            llm_client=services.llm_client,
        )

        # Execute validation
        with console.status("[bold yellow]Running validation pipeline..."):
            report = use_case.execute(
                project_path,
                requirements=requirements,
                metadata=metadata,
                run_tests=run_tests,
                ai_check=ai_check,
            )

        # Display results
        status_style = {"passed": "green", "warnings": "yellow", "failed": "red"}.get(
            report.overall_status, "white"
        )

        console.print(
            f"🎯 Validation Status: {report.overall_status.upper()}", style=f"bold {status_style}"
        )

        # Syntax results
        syntax_issues = sum(len(r.issues) for r in report.syntax_results)
        console.print(
            f"📝 Syntax validation: {len(report.syntax_results)} files checked, {syntax_issues} issues"
        )

        # Test results
        if report.test_result:
            console.print(
                f"🧪 Tests: {report.test_result.passed} passed, {report.test_result.failed} failed, {report.test_result.errors} errors"
            )
        else:
            console.print("🧪 Tests: Not run")

        # AI logic results
        if report.ai_logic_report:
            supported = sum(1 for f in report.ai_logic_report.findings if f.verdict == "supported")
            contradicted = sum(
                1 for f in report.ai_logic_report.findings if f.verdict == "contradicted"
            )
            uncertain = sum(1 for f in report.ai_logic_report.findings if f.verdict == "uncertain")
            console.print(
                f"🤖 AI Logic: {supported} supported, {contradicted} contradicted, {uncertain} uncertain"
            )
        else:
            console.print("🤖 AI Logic: Not checked")

        # Save report if requested
        if output_file:
            report_data = {
                "overall_status": report.overall_status,
                "syntax_results": [r.model_dump() for r in report.syntax_results],
                "test_result": report.test_result.model_dump() if report.test_result else None,
                "ai_logic_report": (
                    report.ai_logic_report.model_dump() if report.ai_logic_report else None
                ),
            }
            output_file.write_text(json.dumps(report_data, indent=2))
            console.print(f"📄 Report saved: {output_file}")

        # Exit with appropriate code
        if report.overall_status == "failed":
            raise typer.Exit(1)
        elif report.overall_status == "warnings":
            raise typer.Exit(2)
        else:
            raise typer.Exit(0)

    except Exception as e:
        console.print(f"❌ Validation failed: {e}", style="red")
        raise typer.Exit(1)


@app.command("version")
def version():
    """Show version information."""
    console.print("🏗️  Platform v0.1.0")
    console.print("Enterprise-grade code generation platform")


@app.command("status")
def status():
    """Show platform status and available providers."""
    console.print(Panel("🏗️  Platform Status", style="bold blue"))

    try:
        services = build_app()
        registry = services.registry

        # Show available providers
        table = Table(title="Available Providers")
        table.add_column("Language", style="cyan")
        table.add_column("Code Generation", style="green")
        table.add_column("Metadata", style="yellow")
        table.add_column("Syntax Validation", style="red")

        all_languages = registry.get_supported_languages()
        for lang in sorted(all_languages):
            has_codegen = "✅" if registry.codegen.has_provider(lang) else "❌"
            has_metadata = "✅" if registry.metadata.has_provider(lang) else "❌"
            has_syntax = "✅" if registry.syntax.has_provider(lang) else "❌"

            table.add_row(lang, has_codegen, has_metadata, has_syntax)

        console.print(table)

        # Show configuration
        config = services.config
        console.print(f"\n🔧 Configuration:")
        console.print(f"  LLM Backend: {config.llm_backend}")
        console.print(f"  Model: {config.model}")
        console.print(f"  Temperature: {config.temperature}")
        console.print(f"  Max Tokens: {config.max_tokens}")
        console.print(f"  Dry Run: {config.dry_run}")

    except Exception as e:
        console.print(f"❌ Failed to get status: {e}", style="red")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
