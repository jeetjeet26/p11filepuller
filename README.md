# Dropbox Team File Search Tool

A Python tool for searching and downloading files across all team members' accounts in a Dropbox Business team. This tool allows you to search for files based on file extensions and keywords, with support for parallel searching across multiple team members' accounts.

## Features

- Search across all team members' Dropbox accounts simultaneously
- Filter files by extension (e.g., pdf, jpg, dco)
- Search for files containing specific keywords
- Download matching files automatically
- Progress tracking and detailed reporting
- Error handling and timeout management
- Parallel processing for faster searches

## Prerequisites

- Python 3.7 or higher
- Dropbox Business account with admin access
- Dropbox API access token with team member file access permissions

### Required Python Packages

```bash
pip install dropbox python-dotenv
```

## Setup

1. Create a Dropbox App:
   - Go to https://www.dropbox.com/developers
   - Click "Create app"
   - Choose "Scoped access"
   - Choose "Team member file access"
   - Name your app
   - Generate an access token with team member file access

2. Set up your environment:
   
   Option 1: Create a `.env` file in the project root (recommended for development):
   ```bash
   # Create and edit .env file
   cp .env.example .env
   # Edit .env and add your access token
   ```

   Option 2: Set environment variable directly:
   
   On Windows:
   ```cmd
   set DROPBOX_ACCESS_TOKEN=your_access_token_here
   ```

   On Unix/Linux:
   ```bash
   export DROPBOX_ACCESS_TOKEN=your_access_token_here
   ```

## Usage

1. Basic usage:
```python
python test.py
```

2. Customize search parameters in `main()`:
```python
# Example: Search for specific file types
keywords = ["floorplan", "architecture"]  # Optional keywords
file_types = ["pdf", "ai", "png", "jpg"]  # File extensions to search for
```

## Output Structure

Downloaded files are organized in the following structure:
```
downloads/
    Team Member Name/
        matched_file1.pdf
        matched_file2.jpg
    Another Member/
        matched_file3.png
```

## Features Explained

### File Searching
- Recursively searches through all folders
- Case-insensitive file extension matching
- Optional keyword filtering
- Progress updates every 100 files

### Error Handling
- Timeout protection (10 minutes per member)
- API rate limit handling
- Graceful interruption handling
- Detailed error reporting

### Performance
- Parallel processing (3 concurrent searches)
- Optimized for large Dropbox accounts
- Progress tracking and reporting

## Limitations

- Maximum 3 concurrent member searches to avoid rate limiting
- 10-minute timeout per member search
- API rate limits may apply based on your Dropbox Business plan

## Error Messages

Common error messages and their meanings:
- "No team members found": Check your access token and permissions
- "API error": Usually related to rate limiting or permissions
- "Search timeout": Member search exceeded 10 minutes
- "Error downloading file": Issues with file access or disk space

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the Dropbox API v2
- Inspired by the Dropbox Business API documentation 