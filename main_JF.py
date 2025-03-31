import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import secrets
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import webbrowser
import logging

# Setup selenium
service = ChromeService("/Users/alexeysharunov/Desktop/JobFinder-Script/chromedriver")
driver = webdriver.Chrome(service=service)

# Setup logging to keep track of what happens in the program
logging.basicConfig(filename='job_finder.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Load Spacy model for named entity recognition
nlp = spacy.load('en_core_web_sm')

# Sleep for a random duration to mimic human interaction
def random_sleep(min_seconds, max_seconds):
    time.sleep(secrets.randbelow(int((max_seconds - min_seconds) * 1000)) / 1000 + min_seconds)

# Simulate random mouse actions to avoid detection
def random_mouse_action(driver, element):
    actions = ActionChains(driver)
    action = secrets.choice(["move", "click"])
    if action == "move":
        actions.move_to_element(element)
    elif action == "click":
        actions.click(element)
    actions.perform()

# Calculate similarity between user skills and job description
def calculate_similarity(user_skills, description):
    vectorizer = TfidfVectorizer()
    corpus = [user_skills, description]
    tfidf_matrix = vectorizer.fit_transform(corpus)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0] * 100

# Find user skills mentioned in the job description
def find_user_skills_in_description(user_skills, description):
    user_skills_lower = [skill.lower().strip() for skill in user_skills.split(",")]
    description_doc = nlp(description)
    found_skills = [skill for skill in user_skills_lower if skill in description_doc.text.lower()]
    return found_skills

# Main automation function to login and search for jobs
async def start_automation(login, password, parameters, start_page, end_page, user_skills):
    chrome_install = ChromeDriverManager().install()
    folder = os.path.dirname(chrome_install)
    chromedriver_path = os.path.join(folder, "chromedriver.exe")

    service = ChromeService(chromedriver_path)
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "normal"
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-infobars")

    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20, poll_frequency=0.5)

    job_titles = []
    job_links = []
    job_descriptions = []
    job_matching_percentage = []

    try:
        driver.get("https://hh.ru/")
        random_sleep(1, 3)

        # Perform login steps
        first_enter = wait.until(EC.element_to_be_clickable(("xpath", "//a[@class='supernova-button']")))
        first_enter.click()
        random_sleep(1, 3)

        google_button = wait.until(EC.element_to_be_clickable(("xpath", "//a[@title='Google']")))
        google_button.click()
        random_sleep(1, 3)

        google_login = wait.until(EC.element_to_be_clickable(("xpath", "//input[@type='email']")))
        google_login.send_keys(login)
        random_sleep(1, 2)

        next_google_button_1 = wait.until(EC.element_to_be_clickable(("xpath", "(//span[@jsname='V67aGc'])[2]")))
        next_google_button_1.click()
        random_sleep(1, 3)

        google_password = wait.until(EC.element_to_be_clickable(("xpath", "//input[@type='password']")))
        google_password.send_keys(password)
        random_sleep(1, 2)

        next_google_button_2 = wait.until(EC.element_to_be_clickable(("xpath", "(//span[@jsname='V67aGc'])[2]")))
        next_google_button_2.click()
        random_sleep(2, 4)

        search_parameters = wait.until(EC.element_to_be_clickable(("xpath", "//input[@id='a11y-search-input']")))
        search_parameters.send_keys(parameters)
        random_sleep(1, 3)

        search_after_parameters = wait.until(EC.element_to_be_clickable(("xpath", "//button[@type='submit']")))
        search_after_parameters.click()
        random_sleep(2, 4)

        for page in range(start_page, end_page + 1):
            logging.info(f"Parsing page {page}")
            driver.get(f"https://hh.ru/search/vacancy?page={page - 1}&text={parameters}")
            random_sleep(2, 5)
            titles, links, descriptions = await parsing_for_all_jobs(driver, user_skills)
            job_titles.extend(titles)
            job_links.extend(links)
            job_descriptions.extend(descriptions)
            for job, description in zip(titles, descriptions):
                found_skills = find_user_skills_in_description(user_skills, description)
                matching_percentage = calculate_similarity(user_skills, description) if found_skills else 0
                job_matching_percentage.append(matching_percentage)

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        driver.quit()
    
    return job_titles, job_links, job_descriptions, job_matching_percentage

# Function to parse job details from the search results
async def parsing_for_all_jobs(driver, user_skills):
    all_jobs_title = ("xpath", "//h2[@class='bloko-header-section-2']")
    titles_elements = driver.find_elements(*all_jobs_title)
    job_titles = []
    job_links = []
    job_descriptions = []

    for title_element in titles_elements:
        try:
            job_link_element = title_element.find_element(By.XPATH, ".//a[@class='bloko-link']")
            job_titles.append(title_element.text)
            job_links.append(job_link_element.get_attribute('href'))
            job_link = job_link_element.get_attribute('href')
            driver.execute_script("window.open(arguments[0]);", job_link)
            driver.switch_to.window(driver.window_handles[1])
            random_sleep(2, 4)

            try:
                description_element = driver.find_element(By.XPATH, "//div[@class='vacancy-description']")
                job_descriptions.append(description_element.text)
                random_sleep(1, 2)
                random_mouse_action(driver, description_element)
            except Exception as desc_e:
                logging.error(f"Error occurred while fetching job description: {desc_e}")
                job_descriptions.append("Description not available")
            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            logging.error(f"Error occurred while parsing job: {e}")
            if driver.window_handles:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            continue

    return job_titles, job_links, job_descriptions

# Create a database to store job information
def create_database():
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        link TEXT,
                        description TEXT,
                        matching_percentage REAL
                    )''')
    conn.commit()
    conn.close()

# Save job information to the database
def save_to_database(job_titles, job_links, job_descriptions, job_matching_percentage):
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    for job, link, description, matching_percentage in zip(job_titles, job_links, job_descriptions, job_matching_percentage):
        cursor.execute('''INSERT INTO jobs (title, link, description, matching_percentage) VALUES (?, ?, ?, ?)''', (job, link, description, matching_percentage))
    conn.commit()
    conn.close()

# Initialize the Tkinter GUI
def tkinter_part():
    global root, login_entry, password_entry, parameters_entry, start_page_entry, end_page_entry, skills_entry

    root = tk.Tk()
    root.title("JobFinder")
    root.geometry("800x600")

    style = ttk.Style()
    style.configure('TLabel', font=('Helvetica', 12))
    style.configure('TButton', font=('Helvetica', 12))
    style.configure('TEntry', font=('Helvetica', 12))

    form_frame = ttk.Frame(root, padding=20)
    form_frame.pack(fill=tk.BOTH, expand=True)

    # Create and place entry fields with placeholders
    ttk.Label(form_frame, text="Google Login:", font=("Helvetica", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
    login_entry = ttk.Entry(form_frame, width=40)
    login_entry.grid(row=0, column=1, padx=10, pady=5)
    login_entry.insert(0, "Enter your Gmail")
    login_entry.bind("<FocusIn>", lambda event: on_focus_in(event, "Enter your Gmail"))

    ttk.Label(form_frame, text="Google Password:", font=("Helvetica", 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
    password_entry = ttk.Entry(form_frame, width=40, show='*')
    password_entry.grid(row=1, column=1, padx=10, pady=5)
    password_entry.insert(0, "Enter your password")
    password_entry.bind("<FocusIn>", lambda event: on_focus_in(event, "Enter your password"))

    ttk.Label(form_frame, text="Search Parameters:", font=("Helvetica", 12)).grid(row=2, column=0, sticky=tk.W, pady=5)
    parameters_entry = ttk.Entry(form_frame, width=40)
    parameters_entry.grid(row=2, column=1, padx=10, pady=5)
    parameters_entry.insert(0, "Enter job search parameters")
    parameters_entry.bind("<FocusIn>", lambda event: on_focus_in(event, "Enter job search parameters"))

    ttk.Label(form_frame, text="Start Page:", font=("Helvetica", 12)).grid(row=3, column=0, sticky=tk.W, pady=5)
    start_page_entry = ttk.Entry(form_frame, width=10)
    start_page_entry.grid(row=3, column=1, padx=10, pady=5)
    start_page_entry.insert(0, "1")
    start_page_entry.bind("<FocusIn>", lambda event: on_focus_in(event, "1"))

    ttk.Label(form_frame, text="End Page:", font=("Helvetica", 12)).grid(row=4, column=0, sticky=tk.W, pady=5)
    end_page_entry = ttk.Entry(form_frame, width=10)
    end_page_entry.grid(row=4, column=1, padx=10, pady=5)
    end_page_entry.insert(0, "1")
    end_page_entry.bind("<FocusIn>", lambda event: on_focus_in(event, "1"))

    ttk.Label(form_frame, text="User Skills:", font=("Helvetica", 12)).grid(row=5, column=0, sticky=tk.W, pady=5)
    skills_entry = ttk.Entry(form_frame, width=40)
    skills_entry.grid(row=5, column=1, padx=10, pady=5)
    skills_entry.insert(0, "Enter skills, separated by commas")
    skills_entry.bind("<FocusIn>", lambda event: on_focus_in(event, "Enter skills, separated by commas"))

    submit_button = ttk.Button(form_frame, text="Start Parsing", command=on_submit)
    submit_button.grid(row=6, column=1, padx=10, pady=20, sticky=tk.E)

    # Add tooltips to entry fields
    create_tooltip(login_entry, "Enter the email you use to log in to Google.")
    create_tooltip(password_entry, "Enter the password for your Google account.")
    create_tooltip(parameters_entry, "Enter the job search parameters.")
    create_tooltip(start_page_entry, "Specify the page number to start from.")
    create_tooltip(end_page_entry, "Specify the page number to end on.")
    create_tooltip(skills_entry, "Your skills, separated by commas.")

    root.mainloop()

# Remove placeholder text on focus
def on_focus_in(event, placeholder):
    if event.widget.get() == placeholder:
        event.widget.delete(0, "end")
        if event.widget == password_entry:
            event.widget.config(show="*")

# Create tooltips for the entry fields
def create_tooltip(widget, text):
    tooltip = tk.Toplevel(root)
    tooltip.wm_overrideredirect(True)
    tooltip.withdraw()
    label = tk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1, padx=5, pady=5)
    label.pack()
    def enter(event):
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + 30
        tooltip.geometry(f"+{x}+{y}")
        tooltip.deiconify()
    def leave(event):
        tooltip.withdraw()
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

# Wrapper function to start the automation process
async def start_automation_wrapper(login, password, parameters, start_page, end_page, user_skills):
    try:
        job_titles, job_links, job_descriptions, job_matching_percentage = await start_automation(login, password, parameters, start_page, end_page, user_skills)
        save_to_database(job_titles, job_links, job_descriptions, job_matching_percentage)

        results_window = tk.Toplevel(root)
        results_window.title("Job Search Results")
        results_window.geometry("1200x800")

        frame = ttk.Frame(results_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create a treeview for displaying results
        tree = ttk.Treeview(frame, columns=("Title", "Matching", "Link", "Description"), show='headings')
        tree.heading("Title", text="Title")
        tree.heading("Matching", text="Matching %")
        tree.heading("Link", text="Link")
        tree.heading("Description", text="Description")
        tree.column("Title", anchor=tk.W, width=200)
        tree.column("Matching", anchor=tk.CENTER, width=100)
        tree.column("Link", anchor=tk.W, width=200)
        tree.column("Description", anchor=tk.CENTER, width=150)
        tree.pack(fill=tk.BOTH, expand=True)

        for title, link, matching, description in zip(job_titles, job_links, job_matching_percentage, job_descriptions):
            tree.insert("", "end", values=(title, f"{matching:.2f}", "Open Link", "View Description"))

        # Bind link opening
        tree.bind("<ButtonRelease-1>", lambda event: handle_tree_click(tree, event, job_links, job_descriptions))

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

# Handle treeview clicks
def handle_tree_click(tree, event, job_links, job_descriptions):
    item = tree.identify('item', event.x, event.y)
    column = tree.identify('column', event.x, event.y)
    if column == '#3':  # Link column
        index = tree.index(item)
        link = job_links[index]
        webbrowser.open(link)
    elif column == '#4':  # Description column
        index = tree.index(item)
        description = job_descriptions[index]

        description_window = tk.Toplevel(root)
        description_window.title("Job Description")
        description_window.geometry("800x600")

        text_area = scrolledtext.ScrolledText(description_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, description)
        text_area.configure(state='disabled')

# Handle form submission and start the job search
def on_submit():
    login = login_entry.get()
    password = password_entry.get()
    parameters = parameters_entry.get()
    start_page = int(start_page_entry.get())
    end_page = int(end_page_entry.get())
    user_skills = skills_entry.get()

    asyncio.run(start_automation_wrapper(login, password, parameters, start_page, end_page, user_skills))

if __name__ == "__main__":
    create_database()
    tkinter_part()
