# Deployment Guide for AI Tools Curator

This guide covers deploying the AI Tools Curator system using GitHub Actions and GitHub Pages.

## Prerequisites 🔧

1. GitHub account
2. Repository forked/cloned
3. Basic understanding of GitHub Actions
4. Python 3.11+ installed locally (for testing)

## Deployment Steps 🚀

### 1. Initial Setup
bash
Clone repository
git clone https://github.com/yourusername/ai-tools-curator.git
cd ai-tools-curator
Install dependencies
python -m pip install -r requirements.txt
Create necessary directories
mkdir -p data/tools
mkdir -p docs

### 2. Configuration

1. **Create config.json**
json
{
"discovery": {
"sources": {
"source_name": {
"url": "https://example.com",
"selector": "div.tool-listing"
}
},
"max_tools_per_source": 10
},
"quality": {
"weights": {
"description_quality": 0.3,
"feature_count": 0.2,
"url_quality": 0.2,
"content_uniqueness": 0.3
}
}
}

2. **GitHub Repository Settings**
- Go to repository Settings
- Navigate to Pages section
- Set source to "GitHub Actions"
- Enable "Read and write permissions" under Actions → General → Workflow permissions

### 3. GitHub Actions Setup

The workflow is already configured in `.github/workflows/gh-pages.yml`:
- Runs on push to main branch
- Runs daily for tool discovery
- Generates and deploys static site

### 4. Custom Domain (Optional)

If using a custom domain:

1. Add domain in GitHub Pages settings
2. Create/update `docs/CNAME`:
bash
echo "yourdomain.com" > docs/CNAME

3. Update DNS settings with your provider:
Type Name Value
A @ 185.199.108.153
A @ 185.199.109.153
A @ 185.199.110.153
A @ 185.199.111.153
CNAME www yourusername.github.io

### 5. Verify Deployment

1. **Local Testing**
bash
Test tool discovery
python src/main.py --mode discover
Test site generation
python src/main.py --mode generate
Test weekly digest
python src/main.py --mode digest

2. **Production Verification**
- Check GitHub Actions tab for workflow status
- Visit `https://yourusername.github.io/ai-tools-curator`
- Verify tools are being discovered and displayed
- Check weekly digest generation

## Maintenance 🛠️

### Daily Operations
- System automatically runs daily via GitHub Actions
- New tools are discovered and added
- Site is regenerated and deployed

### Weekly Operations
- Weekly digest is generated every Sunday
- Tool quality scores are updated
- Analytics data is processed

### Monthly Operations
- Review and clean old data
- Update source configurations if needed
- Check system performance metrics

## Troubleshooting 🔍

### Common Issues

1. **Workflow Failures**
bash
Check workflow logs in GitHub Actions
Verify config.json format
Ensure all dependencies are listed in requirements.txt

2. **Deployment Issues**
bash
Verify GitHub Pages settings
Check branch permissions
Validate workflow permissions

3. **Data Issues**
bash
Check data/tools.json format
Verify tool discovery logs
Ensure quality scoring is working

### Getting Help

1. Check existing issues on GitHub
2. Review the error logs
3. Open a new issue with:
   - Error description
   - Steps to reproduce
   - Relevant logs
   - System configuration

## Security Considerations 🔒

1. Keep `GITHUB_TOKEN` secure
2. Don't commit sensitive data
3. Regular security updates
4. Monitor access logs

## Performance Optimization 📈

1. **Site Generation**
   - Optimize image sizes
   - Minimize CSS/JS
   - Enable caching

2. **Tool Discovery**
   - Rate limiting
   - Efficient crawling
   - Data deduplication

## Backup and Recovery 💾

1. **Regular Backups**
bash
Automated via GitHub
Manual data exports recommended

2. **Recovery Process**
bash
Restore from GitHub history
Rebuild from backup data
Regenerate site

Need help? Open an issue on GitHub! 🚀