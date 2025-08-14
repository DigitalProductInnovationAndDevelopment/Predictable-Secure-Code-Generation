# Handle Platform (S1/S2/S3)

Enterprise-grade skeleton for:
- **S1**: Code generation from requirements
- **S2**: Metadata generation from code
- **S3**: Validation (syntax → tests → AI logic checks)

## Quickstart

```bash
# from the project root
pip install -e .
python -m platform.interfaces.cli.main --help

# Example commands
python -m platform.interfaces.cli.main s2-metadata examples/projects/sample_python_lib -o metadata.json
python -m platform.interfaces.cli.main s3-validate examples/projects/sample_python_lib --run-tests False --ai-check False
python -m platform.interfaces.cli.main s1-generate -r examples/requirements/sample_requirements.json -l python -o out
```
