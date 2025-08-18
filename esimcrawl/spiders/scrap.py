import scrapy
import json
import re
from scrapy_playwright.page import PageMethod


class YesimDevicesSpider(scrapy.Spider):
    name = "yesim_devices"
    start_urls = ["https://yesim.app/compatible-devices/"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-extensions",
                "--disable-plugins",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        },
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "FEEDS": {
            "yesim_devices.json": {"format": "jsonlines", "encoding": "utf8", "indent": 2},
        },
        "LOG_LEVEL": "INFO",
    }

    def start_requests(self):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        yield scrapy.Request(
            url=self.start_urls[0],
            headers=headers,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_coroutines": [
                    PageMethod("wait_for_load_state", "networkidle", timeout=60000),
                    PageMethod("wait_for_timeout", 10000),  # wait for Cloudflare to clear
                ],
            },
        )

    def parse(self, response):
        self.logger.info(f"Parsing response from {response.url}")
        self.logger.info(f"Response status: {response.status}")
        
        # Write rendered HTML to inspect what was actually loaded
        with open("rendered_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        self.logger.info("HTML written to rendered_page.html")

        # Check if we got blocked by Cloudflare
        if "cloudflare" in response.text.lower() or "aws waf" in response.text.lower():
            self.logger.warning("Detected Cloudflare/AWS WAF protection")
            yield {
                "status": "blocked",
                "error": "Cloudflare/AWS WAF protection detected",
                "url": response.url,
                "content_preview": response.text[:200]
            }
            return

        # Extract JSON-LD schema data
        json_ld_data = self.extract_json_ld_data(response)
        if json_ld_data:
            self.logger.info("Successfully extracted JSON-LD data")
            yield json_ld_data
        else:
            self.logger.warning("Failed to extract JSON-LD data, falling back to HTML parsing")
            # Fallback to HTML parsing if JSON-LD extraction fails
            fallback_data = list(self.parse_html_fallback(response))
            if fallback_data:
                yield fallback_data[0]  # Only yield the first fallback result
            else:
                yield {
                    "status": "no_data_found",
                    "error": "No device data could be extracted from any method",
                    "url": response.url
                }

    def extract_json_ld_data(self, response):
        """
        Extract device data from JSON-LD schema embedded in the page.
        """
        try:
            # Find all script tags with type="application/ld+json"
            json_ld_scripts = response.xpath('//script[@type="application/ld+json"]/text()').getall()
            
            for script_content in json_ld_scripts:
                try:
                    data = json.loads(script_content)
                    
                    # Look for the main entity that contains the device list
                    if isinstance(data, dict) and "mainEntity" in data:
                        main_entity = data["mainEntity"]
                        
                        if isinstance(main_entity, dict) and "itemListElement" in main_entity:
                            item_list = main_entity["itemListElement"]
                            
                            if isinstance(item_list, list) and len(item_list) > 0:
                                # Extract device names from the itemListElement
                                devices = []
                                for item in item_list:
                                    if isinstance(item, dict) and "name" in item:
                                        device_name = item["name"].strip()
                                        if device_name and len(device_name) > 2:
                                            devices.append(device_name)
                                
                                if devices:
                                    self.logger.info(f"Extracted {len(devices)} devices from JSON-LD")
                                    return {
                                        "category": "eSIM Compatible Devices",
                                        "devices": devices,
                                        "source": "json_ld_schema",
                                        "total_devices": len(devices),
                                        "url": response.url,
                                        "title": data.get("name", "eSIM Compatible Devices List")
                                    }
                                # Return immediately after finding valid data to prevent duplicates
                                break
                
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse JSON-LD script: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error extracting JSON-LD data: {e}")
        
        return None

    def parse_html_fallback(self, response):
        """
        Fallback method to parse device data from HTML elements.
        """
        self.logger.info("Using HTML fallback parsing method")
        
        # Try to find device lists in various HTML structures
        devices_found = []
        
        # Method 1: Look for list items that might be devices
        list_items = response.css("ul li, ol li")
        for item in list_items:
            text = item.css("::text").get()
            if text:
                text = text.strip()
                # Filter for likely device names
                if (len(text) > 3 and 
                    any(keyword in text.lower() for keyword in 
                        ["iphone", "samsung", "pixel", "oneplus", "xiaomi", "huawei", 
                         "motorola", "galaxy", "ipad", "watch", "surface", "thinkpad"])):
                    devices_found.append(text)
        
        # Method 2: Look for headings followed by device lists
        headings = response.css("h1, h2, h3, h4, h5, h6")
        for heading in headings:
            heading_text = heading.css("::text").get()
            if heading_text and any(keyword in heading_text.lower() for keyword in 
                                  ["device", "phone", "tablet", "compatible", "esim"]):
                # Look for lists following this heading
                following_lists = heading.xpath("following-sibling::ul[1] | following-sibling::ol[1]")
                for ul in following_lists:
                    items = ul.css("li::text").getall()
                    for item in items:
                        item = item.strip()
                        if item and len(item) > 3:
                            devices_found.append(item)
        
        # Remove duplicates and filter
        unique_devices = list(set(devices_found))
        filtered_devices = [device for device in unique_devices if len(device) > 3]
        
        if filtered_devices:
            self.logger.info(f"Extracted {len(filtered_devices)} devices from HTML fallback")
            yield {
                "category": "eSIM Compatible Devices (HTML Fallback)",
                "devices": filtered_devices,
                "source": "html_fallback",
                "total_devices": len(filtered_devices),
                "url": response.url
            }
        else:
            self.logger.warning("No devices found in HTML fallback parsing")
            yield {
                "status": "no_devices_found",
                "error": "No device data could be extracted",
                "url": response.url,
                "parsing_method": "html_fallback"
            }