# eSIM Device Crawler

A robust web scraping solution for crawling eSIM compatible devices from Yesim.app and sending the data to a webhook.

## Features

- **Robust Error Handling**: Comprehensive error handling for network issues, file operations, and Scrapy failures
- **Logging**: Detailed logging to both file and console for debugging and monitoring
- **Retry Logic**: Automatic retry mechanism for webhook requests
- **Configuration Management**: Centralized configuration with environment variable support
- **Type Hints**: Full type annotations for better code maintainability
- **Timeout Protection**: Configurable timeouts to prevent hanging processes

## Project Structure

```
esimcrawl/
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── scrapy.cfg            # Scrapy configuration
├── esimcrawl/
│   ├── __init__.py
│   ├── config.py         # Centralized configuration
│   ├── main.py           # Main orchestration script
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── settings.py
│   └── spiders/
│       ├── __init__.py
│       └── scrap.py      # Scrapy spider implementation
```

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers** (required for scrapy-playwright):
   ```bash
   playwright install chromium
   ```

## Configuration

The application uses a centralized configuration system in `esimcrawl/config.py`. You can customize settings by:

### Environment Variables

- `WEBHOOK_URL`: Target webhook URL (default: https://n8n.gohub.cloud/webhook-test/eSIM_compatible)
- `WEBHOOK_TIMEOUT`: Request timeout in seconds (default: 30)
- `WEBHOOK_RETRIES`: Number of retry attempts (default: 3)
- `SCRAPY_TIMEOUT`: Scrapy process timeout in seconds (default: 300)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DEBUG`: Enable debug mode (default: False)

### Example Environment Setup

```bash
export WEBHOOK_URL="https://your-webhook-url.com/endpoint"
export WEBHOOK_TIMEOUT=60
export WEBHOOK_RETRIES=5
export LOG_LEVEL=DEBUG
```

## Usage

### Basic Usage

Run the crawler from the project root:

```bash
# From the esimcrawl directory
python esimcrawl/main.py

# Or from the parent directory
cd esimcrawl
python esimcrawl/main.py
```

### What the Script Does

1. **Runs Scrapy Spider**: Executes the `yesim_devices` spider to crawl device data
2. **Loads JSON Data**: Reads the scraped data from the output file
3. **Sends to Webhook**: Posts the data to the configured webhook URL with retry logic

### Output Files

- `yesim_devices.json`: Scraped device data
- `esim_crawler.log`: Application logs
- `rendered_page.html`: Debug HTML output from the spider

## Error Handling

The application includes comprehensive error handling:

- **Scrapy Failures**: Captures and logs Scrapy process errors
- **File Operations**: Handles missing files and JSON parsing errors
- **Network Issues**: Retries failed webhook requests with exponential backoff
- **Timeouts**: Prevents hanging processes with configurable timeouts

## Logging

Logs are written to both:
- **Console**: Real-time output for immediate feedback
- **File**: Persistent log file (`esim_crawler.log`) for debugging

Log levels: DEBUG, INFO, WARNING, ERROR

## Development

### Adding New Features

1. Update `esimcrawl/config.py` for new configuration options
2. Add new functions to `esimcrawl/main.py` with proper error handling
3. Update `requirements.txt` for new dependencies
4. Test with different log levels and error conditions

### Testing

Test the application with various scenarios:

```bash
# Test with debug logging
DEBUG=true python esimcrawl/main.py

# Test with custom webhook
WEBHOOK_URL="https://httpbin.org/post" python esimcrawl/main.py
```

## Troubleshooting

### Common Issues

1. **Scrapy not found**: Ensure Scrapy is installed and in PATH
2. **Playwright errors**: Run `playwright install chromium`
3. **Permission errors**: Check file write permissions in the project directory
4. **Network timeouts**: Increase timeout values in configuration
5. **Import errors**: Make sure you're running from the correct directory

### Debug Mode

Enable debug mode for detailed logging:

```bash
DEBUG=true LOG_LEVEL=DEBUG python esimcrawl/main.py
```

## Dependencies

- `requests`: HTTP client for webhook communication
- `scrapy`: Web scraping framework
- `scrapy-playwright`: Browser automation for JavaScript-heavy sites
- `playwright`: Browser automation engine
- `pathlib2`: Path manipulation utilities
- `typing-extensions`: Type hint support

## License

This project is for educational and development purposes.
