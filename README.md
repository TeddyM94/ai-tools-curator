# AI Tools Curator 🤖

An automated system that discovers, evaluates, and publishes high-quality AI tools. Built with Python and GitHub Actions.

## Features ✨

- **Automated Discovery**: Daily scanning of multiple sources for new AI tools
- **Quality Scoring**: Advanced algorithm to evaluate tool quality and relevance
- **Static Site Generation**: Beautiful, fast-loading pages for discovered tools
- **Weekly Digests**: Automated summaries of the best new tools
- **GitHub Pages Integration**: Automatic deployment of the curated collection
- **Analytics**: Track tool popularity and user engagement

## Quick Start 🚀

1. **Clone the repository**
bash
git clone https://github.com/yourusername/ai-tools-curator.git
cd ai-tools-curator

2. **Install dependencies**
bash
python -m pip install -r requirements.txt

3. **Run locally**
bash
Discover new tools
python src/main.py --mode discover
Generate static site
python src/main.py --mode generate
Create weekly digest
python src/main.py --mode digest

## Configuration ⚙️

1. Create a `config.json` file:
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
},
"thresholds": {
"min_score": 0.6
}
},
"site": {
"title": "AI Tools Discovery",
"description": "Curated collection of the best AI tools"
}
}

2. Configure GitHub Actions:
   - Add `GITHUB_TOKEN` secret (automatically provided)
   - Optional: Add custom domain in GitHub Pages settings

## Project Structure 📁
ai-tools-curator/
├── data/ # Curated tools and digests
├── docs/ # Generated static site
├── src/ # Source code
├── templates/ # HTML templates
├── tests/ # Test suite
└── config.json # Configuration

## Development 🛠️

1. **Setup development environment**
bash
Create virtual environment
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
Install dev dependencies
pip install -r requirements.txt

2. **Run tests**
bash
pytest tests/

3. **Code style**
bash
Format code
black src/ tests/
Sort imports
isort src/ tests/
Type checking
mypy src/

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Built with Python and GitHub Actions
- Deployed with GitHub Pages
- Community contributions welcome!