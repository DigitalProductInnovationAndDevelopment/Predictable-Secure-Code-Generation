import json
import typer
from pathlib import Path
from platform.kernel.di import build_app
from platform.domain.models.requirements import Requirement

cli = typer.Typer(help="Handle Platform CLI")

@cli.command("s2-metadata")
def s2_metadata(project: str, out: str = "metadata.json"):
    sv = build_app()
    report = sv.s2_usecases.generate_metadata(project)
    Path(out).write_text(report.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(f"Wrote {out}")

@cli.command("s3-validate")
def s3_validate(project: str, run_tests: bool = True, ai_check: bool = False):
    sv = build_app()
    res = sv.s3_usecases.validate(project, run_tests=run_tests, ai_check=ai_check)
    typer.echo(json.dumps(res, indent=2))

@cli.command("s1-generate")
def s1_generate(requirements: str, lang: str, out_dir: str = "out"):
    sv = build_app()
    data = json.loads(Path(requirements).read_text(encoding="utf-8"))
    reqs = [Requirement(**r) for r in data]
    rep = sv.s1_usecases.generate(reqs, lang, out_dir)
    typer.echo(rep.model_dump_json(indent=2))

if __name__ == "__main__":
    cli()
