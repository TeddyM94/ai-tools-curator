# AI Tools Curator 🤖

An automated system that discovers, evaluates, and promotes AI tools through Twitter with affiliate marketing integration.

## Features 🌟

- **Automated Discovery**: Continuously scans multiple sources for new AI tools
- **Quality Assessment**: Evaluates tools based on multiple criteria
- **Smart Posting**: A/B tested Twitter posts with optimal timing
- **Performance Optimization**: Resource-aware task management
- **Analytics Tracking**: Comprehensive performance and engagement metrics
- **Error Handling**: Robust error management and recovery
- **Affiliate Integration**: Automated affiliate link generation

## Installation 🚀

1. Clone the repository:
bash
git clone https://github.com/yourusername/ai-tools-curator.git
cd ai-tools-curator

2. Create and activate virtual environment:
bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

3. Install dependencies:
bash
pip install -r requirements.txt

## Configuration ⚙️

1. Create a `.env` file in the root directory:
env
Twitter API Credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
Affiliate IDs
GETRESPONSE_AFFILIATE_ID=your_getresponse_id
SYSTEME_AFFILIATE_ID=your_systeme_id

2. Adjust settings in `src/utils/config.py` if needed.

## Usage 🎯

Run the curator:
bash
python src/main.py

The system will:
1. Start discovering new AI tools
2. Evaluate their quality
3. Generate affiliate links
4. Post to Twitter
5. Track performance

## Directory Structure 📁
.
├── README.md
├── requirements.txt
└── src
├── affiliate_manager/ # Affiliate link management
├── analytics/ # Performance tracking
├── tools_discovery/ # AI tools discovery
├── twitter_poster/ # Twitter integration
├── utils/ # Utility modules
└── main.py # Main application

## Components 🔧

### Tools Discovery
- Scans multiple sources for AI tools
- Filters duplicates
- Extracts key information

### Quality Scorer
- Evaluates tool quality
- Checks description quality
- Validates features
- Ensures relevance

### Twitter Poster
- Creates engaging posts
- A/B tests formats
- Manages posting schedule
- Tracks engagement

### Analytics Tracker
- Monitors performance
- Tracks engagement
- Generates reports
- Identifies trends

### Performance Optimizer
- Manages resources
- Optimizes task execution
- Prevents overload
- Monitors system health

## Error Handling 🛠️

The system includes comprehensive error handling:
- Automatic retries
- Error logging
- Recovery mechanisms
- Alert system

## Monitoring 📊

Access performance metrics:
- Tool discovery rate
- Posting success rate
- Engagement metrics
- System performance
- Error rates

## Troubleshooting 🔍

Common issues and solutions:

1. **Rate Limiting**
   - Symptom: Too many requests errors
   - Solution: Adjust `MIN_HOURS_BETWEEN_POSTS` in config

2. **Memory Usage**
   - Symptom: High memory consumption
   - Solution: Adjust `max_concurrent_tasks` in performance optimizer

3. **API Errors**
   - Symptom: Twitter API connection issues
   - Solution: Verify API credentials in .env file

## Contributing 🤝

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

For support:
1. Check the troubleshooting guide
2. Review error logs in `logs/`
3. Open an issue on GitHub

## Acknowledgments 🙏

- Twitter API
- Beautiful Soup
- Tweepy
- Python Schedule