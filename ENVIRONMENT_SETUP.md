# Environment Setup Guide

This guide explains how to properly configure the environment variables for the automated code update system.

## Quick Setup

1. **Copy the template file:**

   ```bash
   cp env.template .env
   ```

2. **Edit the `.env` file:**
   Replace the placeholder values with your actual configuration:
   ```bash
   nano .env  # or use your preferred editor
   ```

## Required Environment Variables

### Azure OpenAI Configuration (Required)

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL

### Optional Configuration

- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-01)
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Deployment name (default: gpt-4o)

### Legacy OpenAI Configuration (Optional)

- `OPENAI_API_KEY`: Your OpenAI API key (for backward compatibility)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4)
- `REGION`: Azure region (default: swedencentral)

## Security Best Practices

1. **Never commit `.env` files to version control**

   - The `.env` file is already in `.gitignore`
   - Double-check with: `git status` (should not show `.env`)

2. **Use different `.env` files for different environments:**

   - `.env.development`
   - `.env.staging`
   - `.env.production`

3. **Rotate API keys regularly**
   - Update your Azure OpenAI keys periodically
   - Test the new keys before deploying

## Validation

The application automatically validates required environment variables on startup. If any required variables are missing, you'll see specific error messages indicating which variables need to be set.

Run the validation manually:

```python
from config import Config
errors = Config.validate_config()
if errors:
    for error in errors:
        print(f"Error: {error}")
else:
    print("Configuration is valid!")
```

## Environment File Structure

Your `.env` file should look like this:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_actual_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/

# Optional configurations...
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1
```

## Troubleshooting

- **Import Error**: Make sure you've activated your virtual environment
- **Missing Variables**: Check that all required variables are set in your `.env` file
- **Permission Issues**: Ensure the `.env` file has appropriate read permissions

## Azure Function Deployment

For Azure Functions, set environment variables in the Azure portal:

1. Go to your Function App
2. Navigate to Configuration > Application settings
3. Add each environment variable manually
4. Don't forget to save and restart the function app
