#IMPORT LIBRARIES
import openpyxl
from Bio import Entrez
import gender_guesser.detector as gender
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

#SETTING UP

# Set up the Entrez API keys and email address
Entrez.email = "luca.mascaro00@gmail.com"
Entrez.api_key = "85a0c7eeaa15bb56735b36487500a96b3208"

# Set up the gender detector (from Gender-guesser)
gd = gender.Detector()

#Set up the time date for the PubMed research
start_date = "2017/09/01"
end_date = "2022/08/31"

#GATHER DATA

#Set up the journal list (including the journals that we want to consider for the analysis) taking data from a list of wanted journals
journalNames = pd.read_excel('UfficialJournalNames.xlsx')
journalList = journalNames['Journal'].tolist()

#Define the search query at the basis of the PubMed research
search_query = ('("Nervous System Neoplasms [MeSH Terms]" OR “Neoplasms, Nerve Tissue [MeSH Terms]”) AND “Neurosurgery”')

#VARIABLES
nameExcel = "PubMedResults.xlsx"
nameExcelStatistics = "StatisticsAnalysis.xlsx"
language = "English"

#INITIALIZATION

#Initialize count variables
countOmittedForJournals=0
countOmittedForDoi=0
countTotalResults=0

#Initialize lists
doiConsidered=[]

#Initialize the Excel files to generate
#Excel file1: containing all the data about articles from PubMed
wb = openpyxl.Workbook()
ws = wb.active
ws.append(["DOI", "First Author Name", "First Author Female", "First Author Male", "Last Author Name", "Last Author Female", "Last Author Male", "Year", "First Author Nationality","Last Author Nationality", "Journal"])

#Excel file2: containing some variables on the statistics about the current analysis
wbStatistics = openpyxl.Workbook()
wsStatistics = wbStatistics.active
wsStatistics.append(["Variable", "Value"])

#Initialization of the time dates
#Convert the time dates in the required format
start_date = datetime.strptime(start_date, "%Y/%m/%d").strftime("%Y/%m/%d")
end_date = datetime.strptime(end_date, "%Y/%m/%d").strftime("%Y/%m/%d")

#Set up of the date for the following while loop
start_date_temp = start_date
end_date_temp = (datetime.strptime(start_date_temp, '%Y/%m/%d') + relativedelta(days=1)).strftime('%Y/%m/%d')

#MAIN CODE

#Start the cycle for the acquisition of the data, occurring every month
while end_date_temp <= end_date:

    # Use Entrez to search for the relevant publications
    fetch_handle = Entrez.esearch(db="pubmed", term=search_query, mindate=start_date_temp, maxdate=end_date_temp,lang=language)
    fetch_results = Entrez.read(fetch_handle)
    fetch_handle.close()

    # Use Entrez to retrieve the full records for the relevant publications
    id_list = fetch_results["IdList"]

    if id_list:
        fetch_handle = Entrez.efetch(db="pubmed", id=id_list, rettype="xml", retmode="text", retmax=100000)
        fetch_results = Entrez.read(fetch_handle, validate=False)
        fetch_handle.close()

        Entrez.parse(fetch_results, validate=False)

        #Define a For cycle for the writing in the Excel file of the single publications (with first/last authors, their gender, ...)
        for article in fetch_results["PubmedArticle"]:
            try:
                # Get the doi of the article considered
                doi_list = article["PubmedData"]["ArticleIdList"] if "ArticleIdList" in article["PubmedData"] else []
                doi = next((i for i in doi_list if i.attributes.get("IdType") == "doi"), article["MedlineCitation"]["PMID"])

                if not doiConsidered or doi not in doiConsidered:
                    doiConsidered.append(doi)

                    # Get the journal first (to check if it belongs to the list of wanted journals, otherwise it is omitted from the research)
                    journal = article["MedlineCitation"]["Article"]["Journal"]["Title"] if "Title" in article["MedlineCitation"]["Article"]["Journal"] else ""

                    if journal in journalList:
                        # Get the first and last author's name and nationality
                        author_list = article["MedlineCitation"]["Article"]["AuthorList"]

                        if isinstance(author_list, list):
                            author = author_list[0]
                            lastAuthor = author_list[-1]
                        else:
                            author = author_list
                            lastAuthor = author_list

                        # Obtain the name and nationality of the first author
                        first_name = author.get("ForeName", "")
                        last_name = author.get("LastName", "")

                        # Get nationality from author's affiliations
                        nationality = ""
                        affiliations = author.get("AffiliationInfo", [])
                        for affiliation in affiliations:
                            # Extract affiliation string
                            affiliation_string = affiliation.get("Affiliation", "").strip()
                            # Remove "Electronic address:" if present
                            if "Electronic address:" in affiliation_string:
                                affiliation_string = affiliation_string.replace("Electronic address:", "")
                            # Extract country from affiliation string and remove any trailing semicolon and period
                            country = affiliation_string.split(",")[-1].strip().split(" ")[0].rstrip(";").rstrip(".")
                            # Check if the country name exists in the affiliation string
                            if country:
                                nationality = country
                                break  # Break once we find the first non-empty country

                        # Obtain the name and surname of the last author
                        first_name_last = lastAuthor.get("ForeName", "")
                        last_name_last = lastAuthor.get("LastName", "")

                        # Get nationality of the last author from author's affiliations
                        last_author_nationality = ""
                        last_author_affiliations = lastAuthor.get("AffiliationInfo", [])
                        for affiliation in last_author_affiliations:
                            # Extract affiliation string
                            affiliation_string = affiliation.get("Affiliation", "").strip()
                            # Remove "Electronic address:" if present
                            if "Electronic address:" in affiliation_string:
                                affiliation_string = affiliation_string.replace("Electronic address:", "")
                            # Extract country from affiliation string and remove any trailing semicolon and period
                            country = affiliation_string.split(",")[-1].strip().split(" ")[0].rstrip(";").rstrip(".")
                            # Check if the country name exists in the affiliation string
                            if country:
                                last_author_nationality = country
                                break  # Break once we find the first non-empty country

                        # Year of publication on PubMed
                        year = article["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"]["Year"] if "Year" in article["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"] else ""

                        # Guess the gender of the first author
                        gender_guess_first = gd.get_gender(first_name)
                        if gender_guess_first == "male":
                            male_first = "1"
                            female_first = "0"
                        elif gender_guess_first == "female":
                            male_first = "0"
                            female_first = "1"
                        else:
                            male_first = "X"
                            female_first = "X"

                        # Guess the gender of the last author
                        gender_guess_last = gd.get_gender(first_name_last)
                        if gender_guess_last == "male":
                            male_last = "1"
                            female_last = "0"
                        elif gender_guess_last == "female":
                            male_last = "0"
                            female_last = "1"
                        else:
                            male_last = "X"
                            female_last = "X"

                        # Add the results to the Excel file
                        ws.append([doi, f"{first_name} {last_name}", female_first, male_first, f"{first_name_last} {last_name_last}", female_last, male_last, year, nationality, last_author_nationality, journal])
                        # Save the Excel file (the name of the Excel file will be in an input-format in the future)
                        wb.save(nameExcel)
                        #Obtain the total count of results
                        countTotalResults=countTotalResults+1

                    else:
                        # Obtain the total count of omitted articles for not considered journals
                        countOmittedForJournals=countOmittedForJournals+1

                else:
                    # Obtain the total count of duplicates
                    countOmittedForDoi=countOmittedForDoi+1

            except KeyError:
                continue

    else:
        # Handle the case when the ID list is empty
        print("No publications found for the given day.")

    # Update the start and end dates (for the while cycle), adding one month
    start_date_temp = (datetime.strptime(start_date_temp, '%Y/%m/%d') + relativedelta(days=1)).strftime('%Y/%m/%d')
    end_date_temp = (datetime.strptime(end_date_temp, '%Y/%m/%d') + relativedelta(days=1)).strftime('%Y/%m/%d')

    print(start_date_temp)

#RETURN STATISTICS ON THE ANALYSIS

# Add data to Excel file
data = [
   ("Omitted data for journal", countOmittedForJournals),
   ("Omitted data for doi", countOmittedForDoi),
   ("Total number of results", countTotalResults)]

# Write data to Excel rows
for row in data:
    wsStatistics.append(row)

# Save the Excel file
wbStatistics.save(nameExcelStatistics)