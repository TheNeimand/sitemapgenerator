
import locale


_original_setlocale = locale.setlocale
def safe_setlocale(category, loc=None):
    try:
        return _original_setlocale(category, loc)
    except locale.Error:
        return _original_setlocale(category, 'C')
locale.setlocale = safe_setlocale

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import queue
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from datetime import datetime

def check_internet_connection():

    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except Exception:
        return False

def remove_fragment(url):

    return url.split("#")[0]

def get_all_links(url, max_pages=500, log_callback=None, stop_event=None):

    visited = set()
    to_visit = [remove_fragment(url)]
    links = []

    while to_visit and len(links) < max_pages:
        if stop_event and stop_event.is_set():
            break

        current_url = remove_fragment(to_visit.pop(0))
        if current_url in visited:
            continue

        try:
            response = requests.get(current_url, timeout=10)
            if response.status_code != 200:
                if log_callback:
                    log_callback(f"link ERROR: {current_url} - Status Code: {response.status_code}")
                continue


            last_modified = response.headers.get('Last-Modified')
            if last_modified:
                try:
                    lastmod = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d')
                except Exception:
                    lastmod = datetime.now().strftime('%Y-%m-%d')
            else:
                lastmod = datetime.now().strftime('%Y-%m-%d')

            soup = BeautifulSoup(response.text, 'html.parser')
            visited.add(current_url)


            if current_url == remove_fragment(url):
                priority = "1.0"
                changefreq = "daily"
            else:
                priority = "0.8"
                changefreq = "weekly"


            images = []
            for img in soup.find_all('img'):
                if 'src' in img.attrs:
                    img_url = urljoin(current_url, img['src'])
                    img_url = remove_fragment(img_url)
                    if img_url not in images:
                        images.append(img_url)

            links.append({
                "loc": current_url,
                "lastmod": lastmod,
                "priority": priority,
                "changefreq": changefreq,
                "images": images
            })

            if log_callback:
                log_callback(f"link OK: {current_url}")


            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)
                full_url = remove_fragment(full_url)
                parsed = urlparse(full_url)
                if (parsed.netloc == urlparse(url).netloc and
                    full_url not in visited and
                    full_url not in to_visit):
                    to_visit.append(full_url)
        except Exception as e:
            if log_callback:
                log_callback(f"link ERROR: {current_url} - {str(e)}")

    return links

def create_sitemap(links, filename):

    root = ET.Element("urlset", 
                      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9", 
                      **{"xmlns:image": "http://www.google.com/schemas/sitemap-image/1.1"})
    
    for entry in links:
        url_element = ET.SubElement(root, "url")
        ET.SubElement(url_element, "loc").text = entry["loc"]
        ET.SubElement(url_element, "lastmod").text = entry["lastmod"]
        ET.SubElement(url_element, "priority").text = entry["priority"]
        ET.SubElement(url_element, "changefreq").text = entry["changefreq"]

        if "images" in entry and entry["images"]:
            for img in entry["images"]:
                image_elem = ET.SubElement(url_element, "image:image")
                ET.SubElement(image_elem, "image:loc").text = img

    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)

class SitemapGeneratorApp(ttk.Window):
    def __init__(self):

        super().__init__(themename="flatly")
        self.title("Modern Sitemap Generator Tool")
        self.geometry("900x650")
        self.resizable(False, False)

        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()

        self.create_widgets()

    def create_widgets(self):

        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="x")


        url_label = ttk.Label(frame, text="Website URL:")
        url_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = ttk.Entry(frame, width=60)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)
        self.url_entry.insert(0, "https://www.redaysoft.com")


        max_label = ttk.Label(frame, text="Max Pages:")
        max_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.max_entry = ttk.Entry(frame, width=10)
        self.max_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.max_entry.insert(0, "500")


        self.generate_button = ttk.Button(frame, text="Generate Sitemap", command=self.start_generation, bootstyle=PRIMARY)
        self.generate_button.grid(row=2, column=0, padx=5, pady=10)

        self.cancel_button = ttk.Button(frame, text="Cancel", command=self.cancel_generation, state=DISABLED, bootstyle=DANGER)
        self.cancel_button.grid(row=2, column=1, padx=5, pady=10, sticky="w")

        self.clear_button = ttk.Button(frame, text="Clear Log", command=self.clear_log, bootstyle=INFO)
        self.clear_button.grid(row=2, column=1, padx=5, pady=10, sticky="e")


        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)


        log_label = ttk.Label(self, text="Log:")
        log_label.pack(anchor="w", padx=10)
        self.log_text = scrolledtext.ScrolledText(self, width=105, height=30, state="disabled", font=("Courier", 10))
        self.log_text.pack(padx=10, pady=5)


        self.status_label = ttk.Label(self, text="Ready", bootstyle="secondary")
        self.status_label.pack(anchor="w", padx=10, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_generation(self):

        if not check_internet_connection():
            messagebox.showerror("Internet Connection Error", "No internet connection detected. Please check your connection and try again.")
            return

        url = self.url_entry.get().strip()
        try:
            max_pages = int(self.max_entry.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Max Pages must be an integer.")
            return

        if not url:
            messagebox.showerror("Input Error", "Please enter a website URL.")
            return


        filename = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml")],
            title="Save Sitemap"
        )
        if not filename:
            return

        self.clear_log()
        self.status_label.config(text="Running...")
        self.stop_event.clear()
        self.progress.start()
        self.generate_button.config(state="disabled")
        self.cancel_button.config(state="normal")


        threading.Thread(target=self.run_generation, args=(url, max_pages, filename), daemon=True).start()
        self.after(100, self.process_log_queue)

    def run_generation(self, url, max_pages, filename):
        def log_callback(message):
            self.log_queue.put(message)

        links = get_all_links(url, max_pages, log_callback, self.stop_event)
        if not self.stop_event.is_set():
            try:
                create_sitemap(links, filename)
                self.log_queue.put(f"Sitemap created successfully: {filename}")
            except Exception as e:
                self.log_queue.put(f"Error saving sitemap: {str(e)}")
        else:
            self.log_queue.put("Process cancelled by user.")
        self.log_queue.put("PROCESS_COMPLETE")

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                if message == "PROCESS_COMPLETE":
                    self.progress.stop()
                    self.generate_button.config(state="normal")
                    self.cancel_button.config(state="disabled")
                    self.status_label.config(text="Ready")
                    return
                self.append_log(message)
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue)

    def append_log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def cancel_generation(self):
        self.stop_event.set()
        self.status_label.config(text="Cancelling...")
        self.cancel_button.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def on_close(self):
        self.stop_event.set()
        self.destroy()

if __name__ == "__main__":
    app = SitemapGeneratorApp()
    app.mainloop()
