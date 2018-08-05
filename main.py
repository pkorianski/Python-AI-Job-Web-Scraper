"""
Created by:   Patrick Korianski
Last Updated: 8/05/2018

This program is used to scrape a variety of job websites and find the most popular
skills needed to apply to the following positions:

1) Python Developer
2) Machine Learning Engineer
3) Software Engineer
4) Deep Learning Engineer
5) Python Engineer

"""

import urllib.request, urllib.parse, urllib.error
import bs4
from bs4 import BeautifulSoup
import requests
import re
import os
import pandas as pd
import time

##################
# INITIALIZATION #
##################
output_jobs = {}
global jobOut
global companyOut
global locationOut
global dateOut
global visual


##################
#    METHODS     #
##################

# Create a csv file of all job opportunities
def createCSV():
    fileName = input("Enter file name (w/o extension): ")
    csvFile = open(fileName+".csv", "w+")
    header = "JOB NAME,COMPANY NAME,LOCATION,DAYS POSTED,LINK\n"
    csvFile.write(header)
    for k,v in output_jobs.items():
        line = "\"" + k[0] + "\"" + "," + "\"" + k[1] + "\"" + "," + "\"" + k[2] + "\"" + "," + "\"" + v[0] + "\"" + "," + "\"" + v[1] + "\"" + "\n"
        csvFile.write(line)
    csvFile.close()

# Determines if a variable is empty or filled
def is_empty(a):
    if a:
        return False
    else:
        return True

# Scraps the webpage to find the job title. The job title should be the first one it finds
def find_jobTitle(s):
    d = ""
    for div in s.find_all(name="div",attrs={"data-tn-component":"jobHeader"}):
        jTitle = div.find(name="b", attrs={"class":"jobtitle"})
        d = jTitle.text.strip()
    return d

# Scraps the webpage to find job title. It will iterate until it is found
def get_jobTitle(w):
    global jobOut
    page = requests.get(w)
    soup = BeautifulSoup(page.text, "html.parser")
    jobTitle = find_jobTitle(soup)
    if is_empty(jobTitle) == True:
        get_jobTitle(w)
    else:
        if visual.lower() == 'y' or visual.lower() == 'yes':
            print("     " + "JOB TITLE--> " +jobTitle)
        jobOut = jobTitle

# Scraps the webpage to find the company name. The company name should be the first one it finds
def find_company(s):
    d = ""
    for div in s.find_all(name="div", attrs={"data-tn-component":"jobHeader"}):
        company = div.find(name="span", attrs={"class":"company"})
        if company != None:
            d = company.text.strip()
            break
    return d

# Scraps the webpage to find company name. It will iterate until it is found
def get_company(w):
    global companyOut
    page = requests.get(w)
    soup = BeautifulSoup(page.text, "html.parser")
    company = find_company(soup)
    if len(company) == 0:
        get_company(w)
    else:
        if visual.lower() == 'y' or visual.lower() == 'yes':
            print("     " + "COMPANY--> " +company)
        companyOut = company

# Scraps the webpage to find the company location. The company should be the first one it finds
def find_location(s):
    d = ""
    for div in s.find_all(name="div", attrs={"data-tn-component":"jobHeader"}):
        location = div.find(name="span", attrs={"class":"location"})
        if location != None:
            d = location.text.strip()
            break
    return d

# Scraps the webpage to find company location. It will iterate until it is found
def get_location(w):
    global locationOut
    page = requests.get(w)
    soup = BeautifulSoup(page.text, "html.parser")
    location = find_location(soup)
    if len(location) == 0:
        get_location(w)
    else:
        if visual.lower() == 'y' or visual.lower() == 'yes':
            print("     " + "LOCATION--> " +location)
        locationOut = location

# Scraps the webpage to find posting times. The date should be the first one it finds
def find_jobDate(s):
    d = ""
    for div in s.find_all(name="span", attrs={"class":"date"}):
        if is_empty(div) == False:
            #print(div.text.strip())
            d = div.text.strip()
            break
    return d

# Scraps the webpage to find posting times. It will iterate until it is found
def get_jobDate(w):
    global dateOut
    page = requests.get(w)
    soup = BeautifulSoup(page.text, "html.parser")
    jDate = find_jobDate(soup)
    if len(jDate) == 0:
        get_jobDate(w)
    else:
        if visual.lower() == 'y' or visual.lower() == 'yes':
            print("     " + "DATE--> " +jDate)
        dateOut = jDate

# This method gathers the job-by-job requirements and adds them to the output_jobs dictionary to reduce duplicates
def view_jobreq(w):
    # Get Job Title
    get_jobTitle(w)
    # Get Company Name
    get_company(w)
    # Get Location
    get_location(w)
    # Days Posting has been on indeed
    get_jobDate(w)
    # Adding records to dictionary to avoid duplicates & prep for CSV
    if (jobOut,companyOut, locationOut) not in output_jobs.keys():
        output_jobs[(jobOut,companyOut, locationOut)] = [dateOut, w]

# Scraps the initial webpage and finds links to all of the job postings available
def find_jobs(w):
    links = []
    page = requests.get(w)
    soup = BeautifulSoup(page.text, "html.parser")
    for script in soup.find_all(name="script"):
        temp = re.findall("jobKeysWithInfo\['(.*?)'] =",script.text.strip())
        if(len(temp) != 0):
            links = temp
            break
    print("\n============================")
    print(str(len(links)) + " job postings were found =")

    # No job posting were found. Ask user to retry search parameters
    if len(links) == 0:
        uiBack = input("Would you like to retry your job search? (Y/N): ")
        if uiBack.lower() == 'y' or uiBack.lower() == 'yes':
            main_menu()
        else:
            exit()
    else:
        if visual.lower() == 'n' or visual.lower() == 'no':
            print("=============================================================")
            print("Finding job data... Please wait")
        for link in links:
            if visual.lower() == 'y' or visual.lower() == 'yes':
                print("=============================================================")
                print("https://www.indeed.com/viewjob?jk=" + link)
            jobPost = "https://www.indeed.com/viewjob?jk=" + link
            view_jobreq(jobPost)

def main_job_search():
    # Global variable
    global visual

    # User input for job search
    print("---------------------")
    keyword = input("Enter a job title, keywords, or company: ")
    loc = input("Enter your desired city/town: ")
    state = input("Enter your desired state(IE NH): ")

    # Creation of Indeed webpage
    # Forming the keyword string to input into page link
    keySplit = keyword.split()
    keyString = ""
    i = 0
    while(i < len(keySplit)):
        if (i == len(keySplit) - 1):
            keyString = keyString + str(keySplit[i])
        else:
            keyString = keyString + str(keySplit[i]) + "+"
        i = i+1

    #Forming the city/two nstring to input int page link
    locSplit = loc.split()
    locString = ""
    i = 0
    while(i < len(locSplit)):
        if (i == len(locSplit) - 1):
            locString = locString + str(locSplit[i])
        else:
            locString = locString + str(locSplit[i]) + "+"
        i = i+1

    # Constructing the website link
    website = "https://www.indeed.com/jobs?q=" + keyString + "&l=" + locString + "%2C+" + state
    w1 = website

    # This selection is determine if the user wants the job output display in terminal
    visual = input("Would you like to see jobs info in terminal? (Y/N): ")

    # Finding job requirements ordering the users iput
    find_jobs(w1)

    # This allows the user to find more opportunites/Go to the next page
    moreJobs = input("Would you like to find more jobs? (Y/N): ")
    if moreJobs.lower() == 'y' or moreJobs.lower() == 'yes':
        for i in range(10,60,10):
            w2 = w1 + "&start=" + str(i)
            find_jobs(w2)

    # Prompts the user if they want the job data saved to a CSV File.
    # This will save to the directory the python program is in
    outputToCSV = input("Create CSV file? (Y/N): ")
    if outputToCSV.lower() == 'y' or outputToCSV.lower() == 'yes':
        createCSV()
    else:
        print("No CSV created.")

# The main startup screen that pops up for the application
def main_menu():
    while(True):
        os.system("clear")
        print("\nJOB SCRAPER PORTAL")
        print("---------------------")
        print("1 : Find job requirements")
        print("2 : Review job requirements")
        print("3 : Exit")
        ui = input("Number: ")
        if int(ui) == 1:
            # Starts job search
            main_job_search()
            # Brings the user back to the main menu
            input("Press 'enter' to continue: ")
        elif int(ui) == 2:
            # View the job requirements in Pandas (Need to be in Jupyter Notebook)
            print("---------------------")
            uiPandas = input("Are you running this program in Jupyter Notebook? (Y/N): ")
            if uiPandas.lower() == 'y' or uiPandas.lower() == 'yes':
                print("---------------------")
                print("Development Coming soon..")
                input("Press 'enter' to continue: ")
            else:
                print("---------------------")
                print("For best visual results, it is recommended to use Jupyter Notebook!")
                input("Press 'enter' to continue: ")
        elif int(ui) == 3:
            # Quit the program
            exit()
        else:
            print("The data entered was not valid. Try again")
            main_menu()

##################
# READ TXT FILE #
##################
# NOT available yet..

##################
#  RUN PROGRAM   #
##################
main_menu()
