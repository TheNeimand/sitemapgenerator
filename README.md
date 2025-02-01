# Sitemap Generator Tool

This tool allows you to scan a website and generate an SEO-friendly `sitemap.xml` file by extracting internal links. It provides a **modern user interface (Tkinter + ttkbootstrap)** for a user-friendly experience and includes **internet connection checking, cancelable operations, detailed logging, and file-saving options**.

## Features

- **SEO-Friendly Sitemap Generation:**  
  Crawls internal links from a specified website and outputs a `sitemap.xml` file.

- **Internet Connection Check:**  
  Verifies internet access before starting; if none is available, an error is displayed.

- **Real-Time Logs and Progress Indicators:**  
  Shows log messages and a progress bar to track the scanning process.

- **Cancelable Operations and Log Clearing:**  
  You can cancel the scan at any time and clear the log output.

- **Safe Locale Setting:**  
  The program applies a "monkey patch" at startup to avoid `locale` errors.

## Requirements

- **Python 3.6+** (Recommended: Python 3.10 or later)
- Required Python libraries:
  - [requests](https://pypi.org/project/requests/)
  - [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
  - [ttkbootstrap](https://pypi.org/project/ttkbootstrap/)

## Installation

1. **Install Python:**  
   Download and install Python from the [official website](https://www.python.org/downloads/).

2. **(Optional) Create a Virtual Environment:**
   python -m venv venv
   source venv/bin/activate   # Linux/MacOS
   venv\Scripts\activate      # Windows

3. **Install Required Libraries:**
   pip install requests beautifulsoup4 ttkbootstrap


4. **Download Project Files:**
   git clone https://github.com/your-username/modern-sitemap-generator.git
   cd modern-sitemap-generator


## Usage

1. **Run the Program:**
   python sitemap.py


2. **Interact with the GUI:**
   - **Website URL:** Enter the main URL of the website you want to scan.
   - **Max Pages:** Specify how many pages you want to scan at most.
   - **Generate Sitemap:** Click this button to start the scan.
   - **Cancel:** Stop the scan at any time.
   - **Clear Log:** Clear the log output.
   - **Save the Sitemap:** When the process finishes, a dialog will appear to let you choose where to save the generated `sitemap.xml`.
