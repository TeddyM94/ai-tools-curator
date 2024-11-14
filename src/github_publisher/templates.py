"""
GitHub Publishing Templates
Contains templates for generating GitHub content.

Templates:
- README
- Tool pages
- Weekly digest
"""

README_TEMPLATE = """
# AI Tools Discovery 🤖

Automatically curated list of the latest AI tools and resources. Updated daily!

![Last Updated](https://img.shields.io/badge/Last%20Updated-{last_updated}-blue)
![Tools Count](https://img.shields.io/badge/Tools%20Count-{tools_count}-brightgreen)
![Categories](https://img.shields.io/badge/Categories-{categories_count}-orange)

## 🔥 Latest Discoveries

{latest_tools}

## 📊 Categories

{categories_section}

## 🌟 Top Rated

{top_rated_tools}

## 📈 Weekly Trends

{weekly_trends}

## 🔍 About

This repository is automatically updated daily with new AI tools and resources. Each tool is:
- ✅ Automatically discovered
- ✅ Quality checked
- ✅ Categorized
- ✅ Regularly updated

## 📫 Stay Updated

- ⭐ Star this repository
- 👀 Watch for updates
- 📧 [Subscribe to weekly digest](link-to-signup)

## 🤝 Contributing

Found a great AI tool? [Submit it here](link-to-submission)
"""

TOOL_TEMPLATE = """
# {tool_name}

{tool_description}

## Features

{features_list}

## Details

- **Category:** {category}
- **Added:** {added_date}
- **Last Updated:** {last_updated}
- **URL:** [{url_display}]({url})

## Reviews & Metrics

{metrics_section}

## Similar Tools

{similar_tools}
"""

WEEKLY_DIGEST_TEMPLATE = """
# AI Tools Weekly Digest - Week {week_number}, {year}

## 🎯 This Week's Highlights

{highlights}

## 🆕 New Discoveries

{new_tools}

## 📈 Trending Tools

{trending_tools}

## 🏆 Top Rated

{top_rated}

## 📊 Category Updates

{category_updates}

## 🔮 What's Next

{upcoming_features}

---
*This digest is automatically generated every week. [Subscribe here](link-to-signup) to receive it in your inbox.*
"""

def format_tool_entry(tool: dict) -> str:
    """Format a tool entry for README"""
    return f"""
### [{tool['name']}]({tool['url']})
{tool['description'][:150]}...
- Category: {tool['category']}
- Added: {tool['added_date'][:10]}
"""

def format_category_section(tools_by_category: dict) -> str:
    """Format the categories section"""
    sections = []
    for category, tools in tools_by_category.items():
        tools_list = "\n".join([f"- [{t['name']}]({t['url']})" for t in tools[:5]])
        sections.append(f"""
### {category}
{tools_list}
[View all {len(tools)} tools in {category}](link-to-category)
""")
    return "\n".join(sections)

def format_metrics_section(metrics: dict) -> str:
    """Format metrics section for tool page"""
    return f"""
- 👍 Likes: {metrics.get('likes', 0)}
- 🔄 Shares: {metrics.get('shares', 0)}
- 💬 Comments: {metrics.get('comments', 0)}
- ⭐ Rating: {metrics.get('rating', '0.0')}/5.0
"""

def format_weekly_highlights(tools: list) -> str:
    """Format weekly highlights section"""
    return "\n".join([
        f"## {tool['name']}\n{tool['description'][:200]}...\n"
        f"[Learn more]({tool['url']})\n"
        for tool in tools
    ])