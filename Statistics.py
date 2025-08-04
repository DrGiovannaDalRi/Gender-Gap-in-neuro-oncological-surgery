
##IMPORT NEEDED LIBRARIES
#Import the libraries that the program will need
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
#import numpy as np

##DEFINE NEEDED VARIABLES
#Define the # of minimum reports needed for the statistics to be considered valid
MINIMUMREPORTS = 10
#Define the # of maximum countries to be reported in the specific statistical plot
MAXIMUMCOUNTRIES = 10
#Define the # of maximum journals to be reported in the specific statistical plot
MAXIMUMJOURNALS = 10
# Define font properties to use throughout the plots
FONTFAMILY = 'Times New Roman'
FONTSIZE = 12
TITLEFONTSIZE = 14

##NAME THE USED FILES
#Files for all statistics
USEDFILE="FirstAuthor.xlsx"
FIRSTAUTHORSTATISTICS="FirstAuthorStatistics.txt"

#Files for countries statistics
TABLECOUNTRY="TableCountriesFirstAuthors.png"
BARPLOTCOUNTRY="BarPlotCountriesFirstAuthors.png"
TOTALREPORTSCOUNTRY="1.TotalReportsCountriesFirstAuthors.xlsx"
FEMALENUMBERREPORTSCOUNTRY="2.FemaleReportsCountriesFirstAuthors.xlsx"
FEMALEPERCENTREPORTSCOUNTRY="3.FemaleAndTotalReportsALLCountriesFirstAuthors.xlsx"
FEMALEPERCENTRANKINGCOUNTRY="4.FemalePercentageRankingCountriesFirstAuthors.xlsx"

#Files for journals statistics
TABLEJOURNAL="TableJournalsFirstAuthors.png"
TOTALREPORTSJOURNAL="1.TotalReportsJournalsFirstAuthors.xlsx"
FEMALENUMBERREPORTSJOURNAL="2.FemaleReportsJournalsFirstAuthors.xlsx"
FEMALEPERCENTREPORTSJOURNAL="3.FemaleAndTotalReportsALLJournalsFirstAuthors.xlsx"
FEMALEPERCENTRANKINGJOURNAL="4.FemalePercentageRankingJournalsFirstAuthors.xlsx"

#Files for years statistics
PLOTYEARCOUNT="TrendYearsCountFirstAuthors.png"
PLOTYEARPERCENTAGE="TrendYearsCountFirstAuthors.png"
PLOTYEARCOMBINED="TrendYearsCombinedFirstAuthors.png"
TOTALREPORTSYEAR="1.TotalReportsYearsFirstAuthors.xlsx"
FEMALENUMBERREPORTSYEAR="2.FemaleReportsYearsFirstAuthors.xlsx"
FEMALEPERCENTREPORTSYEAR="3.FemaleAndTotalReportsALLYearsFirstAuthors.xlsx"
FEMALEPERCENTRANKINGYEAR="4.FemalePercentageRankingYearsFirstAuthors.xlsx"

##CLEAN THE DATA
class DataCleaning():
	def __init__(self):
		# Define the dataframe in which the program will work
		self.dataframe = pd.read_excel(USEDFILE)

	def CallFunctions(self):
		#Call the function to cut the dataframe
		self.CutDataframe()
		#Call the function to count and cut the rows with the unknown gender
		dataframe, unknownGenderCount= self.CutUnknownGender()

		return dataframe, unknownGenderCount

	def CutDataframe(self):
		#Remove the columns that are not needed to the statistics
		#Aim: reduce memory footprint and computational time, since the dataframe is big
		wantedColumns = ['Female', 'Male', 'Nationality', 'Year', 'Journal']
		self.dataframe = self.dataframe[wantedColumns].copy()

	def CutUnknownGender(self):
		#Count the data rows for which the gender is unknown
		unknownGenderCount = self.dataframe[(self.dataframe['Male'] == 'X') & (self.dataframe['Female'] == 'X')].shape[0]

		#Remove the data rows for which the gender is unknown
		self.dataframe = self.dataframe[~((self.dataframe['Male'] == 'X') & (self.dataframe['Female'] == 'X'))]

		#Convert all the data in the Female column as an integer (number)
		self.dataframe['Female'] = pd.to_numeric(self.dataframe['Female']).astype(int)

		return self.dataframe, unknownGenderCount

##INTRODUCTION STATISTICS
class DataCount():
	def CallFunctions(self, dataframe):
		self.dataframe = dataframe
		self.totalReports = self.TotalReports()
		numberJournals= self.NumberJournals()
		numberCountries=self.NumberCountries()
		femaleReports, femaleReportsPercent= self.FemaleReports()

		return self.totalReports, numberJournals, numberCountries, femaleReports, femaleReportsPercent

	def TotalReports(self):
		#Obtain the total # of reports by obtaining the # of rows
		totalReports = self.dataframe.shape[0]

		return totalReports

	def NumberJournals(self):
		#Obtain the total # of journals by counting them
		totalJournals = self.dataframe['Journal'].nunique()

		return totalJournals

	def NumberCountries(self):
		#Obtain the total # of journals by counting them
		totalCountries = self.dataframe['Nationality'].nunique()

		return totalCountries

	# GET THE NUMBER and % OF REPORTS WITH FEMALE AUTHORS
	def FemaleReports(self):
		#Obtain the # of female authors by counting the rows with Female column equal to 1
		femaleReports = self.dataframe[self.dataframe['Female'] == 1].shape[0]
		#Obtain the % of female authors
		femaleReportsPercent = (femaleReports / self.totalReports) * 100
		return femaleReports, femaleReportsPercent

##COUNTRIES STATISTICS
class CountriesStatistics():
	def CallFunctions(self, dataframe):
		self.dataframe = dataframe
		#Get the data needed for the statistics regarding the countries
		self.GetData()
		#Get the 3 countries with highest % of female authors
		firstCountry, secondCountry, thirdCountry = self.HighestCountries()
		#Get the country with lowest % of female authors
		lastCountry= self.LowestCountry()
		#Generate the table with the % of female authors
		self.GenerateTable()
		#Generate the bar plot with the statistics
		self.GenerateBarChart()

		return firstCountry, secondCountry, thirdCountry, lastCountry

	def GetData(self):
		##Get the total # of authors per country
		self.totalReportsCountry = self.dataframe.groupby("Nationality").size().reset_index(name="TotalCount")

		#Save the dataframe as an excel file
		self.totalReportsCountry.to_excel(TOTALREPORTSCOUNTRY, index=False)

		##Get the number of female authors per country
		#Generate a new dataset with only the female authors
		femaleAuthorsDataset = self.dataframe[self.dataframe["Female"] == 1]
		#Get a list with the # of female authors per country
		self.femaleReportsCountry = femaleAuthorsDataset.groupby("Nationality").size().reset_index(name="FemaleCount")
		#Save the dataframe as an excel file
		self.femaleReportsCountry.to_excel(FEMALENUMBERREPORTSCOUNTRY, index=False)

		##Get the number of male authors per country
		#Generate a new dataset with only the male authors
		maleAuthorsDataset = self.dataframe[self.dataframe["Male"] == 1]
		#Get a list with the # of female authors per country
		self.maleReportsCountry = maleAuthorsDataset.groupby("Nationality").size().reset_index(name="MaleCount")

		##Get the % of female authors per country
		#Merge the total count and female count dataframes
		self.percentCountry = pd.merge(self.totalReportsCountry, self.femaleReportsCountry, on="Nationality", how="left")
		self.percentCountry["FemaleCount"] = self.percentCountry["FemaleCount"].fillna(0)
		# Save the dataframe as an excel file
		self.percentCountry = self.percentCountry.sort_values(by="FemaleCount", ascending=False)
		self.percentCountry.to_excel(FEMALEPERCENTREPORTSCOUNTRY, index=False)

		#Take into consideration only the countries with more than N reports
		self.percentCountry = self.percentCountry[self.percentCountry["TotalCount"] > MINIMUMREPORTS]

		#Calculate the % of female authors per country
		self.percentCountry["FemalePercentage"] = (self.percentCountry["FemaleCount"] / self.percentCountry["TotalCount"]) * 100

		#Sort the dataFrame by the % of female authors in descending order (rank of the countries)
		self.rankingCountry = self.percentCountry.sort_values(by="FemalePercentage", ascending=False)

		# Save the dataframe as an excel file
		self.rankingCountry.to_excel(FEMALEPERCENTRANKINGCOUNTRY, index=False)

		#Consider only the first N of countries
		self.MaximumDataframe = self.rankingCountry.head(MAXIMUMCOUNTRIES)
		print(self.rankingCountry)

		#Create a new dataframe identical to MaximumDataframe but with MaleCount
		self.MaximumDataframeWithMaleCount = pd.merge(self.MaximumDataframe, self.maleReportsCountry, on="Nationality", how="left")
		self.MaximumDataframeWithMaleCount["MaleCount"] = self.MaximumDataframeWithMaleCount["MaleCount"].fillna(0)
		self.MaximumDataframeWithMaleCount["MalePercentage"] = (self.MaximumDataframeWithMaleCount["MaleCount"] / self.MaximumDataframeWithMaleCount["TotalCount"]) * 100

	def HighestCountries(self):
		##Get the 3 countries with the highest % of female authors
		#Get the top 3 countries with the highest percentage of female authors
		topCountries = self.rankingCountry.head(3)

		firstCountry = topCountries.iloc[0]["Nationality"]
		secondCountry = topCountries.iloc[1]["Nationality"]
		thirdCountry = topCountries.iloc[2]["Nationality"]

		return firstCountry, secondCountry, thirdCountry

	def LowestCountry(self):
		#Get the journal with the lowest % of female authors
		lastCountry = self.rankingCountry.iloc[-1]["Nationality"]

		return lastCountry

	#PRODUCE TABLE WITH ALL DATA
	def GenerateTable(self):
		#Use self.MaximumDataframe as dataframe, because for the representations it is necessary to keep the # of countries low
		#Generate a new figure and axis
		fig, ax = plt.subplots(figsize=(10, 6))

		#Hide the axes
		ax.axis('off')
		ax.axis('tight')

		#Generate the table plot starting from the dataframe
		table = ax.table(cellText=self.MaximumDataframe.values, colLabels=self.MaximumDataframe.columns, cellLoc='center', loc='center')

		#Style the table
		table.auto_set_font_size(False)
		table.set_fontsize(10)
		table.scale(1.2, 1.2)

		#Save the plot as an image
		plt.savefig(TABLECOUNTRY, bbox_inches='tight')

	#PRODUCE BAR CHART WITH ALL DATA
	def GenerateBarChart(self):
		fig, ax1 =plt.subplots(figsize=(18, 12))

		# Set global font properties
		plt.rcParams['font.family'] = FONTFAMILY
		plt.rcParams['font.size'] = FONTSIZE

		# Ensure the column names match those in your dataframe
		if all(col in self.MaximumDataframeWithMaleCount.columns for col in ['Nationality', 'FemaleCount', 'MaleCount', 'FemalePercentage', 'MalePercentage']):

			percent_data = self.MaximumDataframeWithMaleCount.melt(id_vars=["Nationality"],
																   value_vars=["FemalePercentage", "MalePercentage"],
																   var_name="Gender",
																   value_name="Percentage")
			percent_data["Gender"] = percent_data["Gender"].apply(lambda x: "Women authors" if "Female" in x else "Men authors")

			# Create barplot for percentages
			sns.barplot(x="Nationality", y="Percentage", hue="Gender", data=percent_data,
						palette={"Women authors": "purple", "Men authors": "violet"}, alpha=0.6, ax=ax1)

			# Set the primary y-axis label explicitly after the bar plot
			ax1.set_ylabel('Percentage of women and men authors (%)', labelpad=20)  # Add padding

			# Create lineplot for counts
			ax2 = ax1.twinx()
			#indigo
			sns.lineplot(x="Nationality", y="FemaleCount", data=self.MaximumDataframeWithMaleCount, color='crimson',
						 marker='o', markeredgecolor='crimson', sort=False, label='Women authors', ax=ax2)
			#darkviolet
			#deeppink
			#orangered
			sns.lineplot(x="Nationality", y="MaleCount", data=self.MaximumDataframeWithMaleCount, color='darkorange',
						 marker='s', markeredgecolor='darkorange', sort=False, label='Men authors', ax=ax2)

			# Add titles and labels with padding and explicit font properties
			ax1.set_title('Percentage of women and men authors per country',
						  fontfamily=FONTFAMILY,
						  fontsize=TITLEFONTSIZE,
						  pad=20)

			ax1.set_xlabel('Country',
						   fontfamily=FONTFAMILY,
						   fontsize=FONTSIZE,
						   labelpad=15)

			ax1.set_ylabel('Percentage of women and men authors (%)',
						   fontfamily=FONTFAMILY,
						   fontsize=FONTSIZE,
						   labelpad=20)

			ax2.set_ylabel('Number of women and men authors',
						   fontfamily=FONTFAMILY,
						   fontsize=FONTSIZE,
						   labelpad=20)

			# Apply font to tick labels
			for label in ax1.get_xticklabels() + ax1.get_yticklabels():
				label.set_fontfamily(FONTFAMILY)
				label.set_fontsize(FONTSIZE)

			for label in ax2.get_yticklabels():
				label.set_fontfamily(FONTFAMILY)
				label.set_fontsize(FONTSIZE)

			# Get current y-axis limits
			y1_min, y1_max = ax1.get_ylim()
			y2_min, y2_max = ax2.get_ylim()

			# Extend the y-axis limits to make room for legends at the top
			# Increase the upper limit by 20% to create space
			ax1.set_ylim(y1_min, y1_max * 1.2)
			ax2.set_ylim(y2_min, y2_max * 1.2)

			# Move the legends completely outside the plot area
			# For the percentage legend (bar chart)
			legend1 = ax1.legend(title="Percentage", loc='upper left',
								 frameon=True, fontsize=FONTSIZE)
			legend1.get_title().set_fontsize(FONTSIZE)

			# For the count legend (line chart) - place it below the first legend
			legend2 = ax2.legend(title="Number",loc='upper right',
								 frameon=True, fontsize=FONTSIZE)

			# Make the legend box transparent
			legend1.get_frame().set_alpha(0.8)
			legend2.get_frame().set_alpha(0.8)

			# Apply font to legend text
			for text in legend1.get_texts() + legend2.get_texts():
				text.set_fontfamily(FONTFAMILY)
				text.set_fontsize(FONTSIZE)

			# Add a grid for better readability
			ax1.grid(axis='y', linestyle='--', alpha=0.7)

			# Adjust layout to prevent plot covering labels
			# Using less extreme values since legends are now inside
			fig.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.15)

			# Show the plot
			#plt.tight_layout()  # Adjust layout automatically
			plt.show()

			#Save the plot as an image
			plt.savefig(BARPLOTCOUNTRY, bbox_inches='tight')

##JOURNALS STATISTICS
class JournalsStatistics():
	def CallFunctions(self, dataframe):
		self.dataframe = dataframe
		#Get the data needed for the statistics regarding the countries
		self.GetData()
		#Get the 3 countries with highest % of female authors
		firstJournal, secondJournal, thirdJournal = self.HighestJournals()
		#Get the country with lowest % of female authors
		lastJournal= self.LowestJournal()
		#Generate the table with the % of female authors
		self.GenerateTable()

		return firstJournal, secondJournal, thirdJournal, lastJournal

	def GetData(self):
		##Get the total # of authors per journal
		self.totalReportsJournal = self.dataframe.groupby("Journal").size().reset_index(name="TotalCount")

		#Save the dataframe as an excel file
		self.totalReportsJournal.to_excel(TOTALREPORTSJOURNAL, index=False)

		##Get the number of female authors per journal
		#Generate a new dataset with only the female authors
		femaleAuthorsDataset = self.dataframe[self.dataframe["Female"] == 1]
		#Get a list with the # of female authors per journal
		self.femaleReportsJournal = femaleAuthorsDataset.groupby("Journal").size().reset_index(name="FemaleCount")
		#Save the dataframe as an excel file
		self.femaleReportsJournal.to_excel(FEMALENUMBERREPORTSJOURNAL, index=False)

		##Get the number of male authors per journal
		#Generate a new dataset with only the male authors
		maleAuthorsDataset = self.dataframe[self.dataframe["Male"] == 1]
		#Get a list with the # of female authors per journal
		self.maleReportsJournal = maleAuthorsDataset.groupby("Journal").size().reset_index(name="MaleCount")

		##Get the % of female authors per journal
		#Merge the total count and female count dataframes
		self.percentJournal = pd.merge(self.totalReportsJournal, self.femaleReportsJournal, on="Journal", how="left")
		self.percentJournal["FemaleCount"] = self.percentJournal["FemaleCount"].fillna(0)
		# Save the dataframe as an excel file
		self.percentJournal = self.percentJournal.sort_values(by="FemaleCount", ascending=False)
		self.percentJournal.to_excel(FEMALEPERCENTREPORTSJOURNAL, index=False)

		#Take into consideration only the journals with more than N reports
		self.percentJournal = self.percentJournal[self.percentJournal["TotalCount"] > MINIMUMREPORTS]

		#Calculate the % of female authors per journal
		self.percentJournal["FemalePercentage"] = (self.percentJournal["FemaleCount"] / self.percentJournal["TotalCount"]) * 100

		#Sort the dataFrame by the % of female authors in descending order (rank of the journals)
		self.rankingJournal = self.percentJournal.sort_values(by="FemalePercentage", ascending=False)

		#Save the dataframe as an excel file
		self.rankingJournal.to_excel(FEMALEPERCENTRANKINGJOURNAL, index=False)

		#Consider only the first N of journals
		self.MaximumDataframe = self.rankingJournal.head(MAXIMUMJOURNALS)

		print(self.rankingJournal)

	def HighestJournals(self):
		##Get the 3 journals with the highest % of female authors
		#Get the top 3 journals with the highest percentage of female authors
		topJournals = self.rankingJournal.head(3)

		firstJournal = topJournals.iloc[0]["Journal"]
		secondJournal = topJournals.iloc[1]["Journal"]
		thirdJournal = topJournals.iloc[2]["Journal"]

		return firstJournal, secondJournal, thirdJournal

	def LowestJournal(self):
		#Get the journal with the lowest % of female authors
		lastJournal = self.rankingJournal.iloc[-1]["Journal"]

		return lastJournal

	#PRODUCE TABLE WITH ALL DATA
	def GenerateTable(self):
		#Use self.MaximumDataframe as dataframe, because for the representations it is necessary to keep the # of journals low
		#Generate a new figure and axis
		fig, ax = plt.subplots(figsize=(10, 6))

		#Hide the axes
		ax.axis('off')
		ax.axis('tight')

		#Generate the table plot starting from the dataframe
		table = ax.table(cellText=self.MaximumDataframe.values, colLabels=self.MaximumDataframe.columns, cellLoc='center', loc='center')

		#Style the table
		table.auto_set_font_size(False)
		table.set_fontsize(10)
		table.scale(1.2, 1.2)

		#Save the plot as an image
		plt.savefig(TABLEJOURNAL, bbox_inches='tight')

##YEARS STATISTICS
class YearsStatistics():
    def CallFunctions(self, dataframe):
        self.dataframe = dataframe
        self.GetData()
        self.PlotYears()  # Plots absolute counts
        self.PlotYearsPercentage()  # Plots female percentage only

    # GET THE DATA
    def GetData(self):
        ## Get the total # of authors per year
        self.totalReportsYear = self.dataframe.groupby("Year").size().reset_index(name="TotalCount")

        # Filter out years 2017, 2022, and 2023
        self.totalReportsYear = self.totalReportsYear[~self.totalReportsYear['Year'].isin([2017, 2022, 2023])]

        ## Get the number of female authors per year
        femaleAuthorsDataset = self.dataframe[self.dataframe["Female"] == 1]
        self.femaleReportsYear = femaleAuthorsDataset.groupby("Year").size().reset_index(name="FemaleCount")
        self.femaleReportsYear = self.femaleReportsYear[~self.femaleReportsYear['Year'].isin([2017, 2022, 2023])]

        ## Get the number of male authors per year
        maleAuthorsDataset = self.dataframe[self.dataframe["Female"] == 0]  # Assuming 0 represents male
        self.maleReportsYear = maleAuthorsDataset.groupby("Year").size().reset_index(name="MaleCount")
        self.maleReportsYear = self.maleReportsYear[~self.maleReportsYear['Year'].isin([2017, 2022, 2023])]

        ## Merge all dataframes
        self.mergedData = pd.merge(self.totalReportsYear, self.femaleReportsYear, on="Year", how="left")
        self.mergedData = pd.merge(self.mergedData, self.maleReportsYear, on="Year", how="left")

        # Fill NaN values with 0 (for years with no female/male authors)
        self.mergedData["FemaleCount"] = self.mergedData["FemaleCount"].fillna(0)
        self.mergedData["MaleCount"] = self.mergedData["MaleCount"].fillna(0)

        # Calculate percentages
        self.mergedData["FemalePercentage"] = (self.mergedData["FemaleCount"] / self.mergedData["TotalCount"]) * 100
        self.mergedData["MalePercentage"] = (self.mergedData["MaleCount"] / self.mergedData["TotalCount"]) * 100

        # Create sorted versions for output
        self.mergedData = self.mergedData.sort_values("Year")  # For plotting
        self.rankingYear = self.mergedData.sort_values(by="FemalePercentage", ascending=False)  # For ranking

        # Save all dataframes
        self.totalReportsYear.to_excel(TOTALREPORTSYEAR, index=False)
        self.femaleReportsYear.to_excel(FEMALENUMBERREPORTSYEAR, index=False)
        self.mergedData.to_excel(FEMALEPERCENTREPORTSYEAR, index=False)
        self.rankingYear.to_excel(FEMALEPERCENTRANKINGYEAR, index=False)

        print(self.rankingYear)

    # PLOT ABSOLUTE COUNTS OF FEMALE AND MALE AUTHORS
    def PlotYears(self):
        fig, ax = plt.subplots(figsize=(18, 12))

        # Set global font properties
        plt.rcParams['font.family'] = FONTFAMILY
        plt.rcParams['font.size'] = FONTSIZE

        # Prepare data (ensure Year is categorical and sorted)
        self.mergedData["Year"] = pd.Categorical(
            self.mergedData["Year"],
            ordered=True,
            categories=sorted(self.mergedData["Year"].unique())
        )
        self.mergedData = self.mergedData.sort_values("Year")

        # Create line plots for both genders (using counts)
        sns.lineplot(
            x="Year",
            y="FemaleCount",
            data=self.mergedData,
            color='purple',
            marker='o',
            markeredgecolor='purple',
            linewidth=2.5,
            label='Women authors',
            ax=ax
        )

        sns.lineplot(
            x="Year",
            y="MaleCount",
            data=self.mergedData,
            color='violet',
            marker='s',
            markeredgecolor='violet',
            linewidth=2.5,
            label='Men authors',
            ax=ax
        )

        # Title and labels
        ax.set_title(
            'Yearly trend of women and men authors',
            fontfamily=FONTFAMILY,
            fontsize=TITLEFONTSIZE,
            pad=20
        )
        ax.set_xlabel('Year', fontfamily=FONTFAMILY, fontsize=FONTSIZE, labelpad=15)
        ax.set_ylabel('Number of authors', fontfamily=FONTFAMILY, fontsize=FONTSIZE, labelpad=20)

        # Customize ticks
        ax.set_xticks(self.mergedData['Year'])
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontfamily(FONTFAMILY)
            label.set_fontsize(FONTSIZE)
        plt.xticks(rotation=45)

        # Grid and legend
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        legend = ax.legend(
            loc='upper left',
            frameon=True,
            fontsize=FONTSIZE
        )
        legend.get_title().set_fontsize(FONTSIZE)
        legend.get_frame().set_alpha(0.8)
        for text in legend.get_texts():
            text.set_fontfamily(FONTFAMILY)

        # Adjust layout and save
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
        plt.savefig(PLOTYEARCOUNT, bbox_inches='tight')
        plt.show()

    # PLOT PERCENTAGE OF FEMALE AUTHORS ONLY
    def PlotYearsPercentage(self):
        fig, ax = plt.subplots(figsize=(18, 12))

        # Set global font properties
        plt.rcParams['font.family'] = FONTFAMILY
        plt.rcParams['font.size'] = FONTSIZE

        # Prepare data (ensure Year is categorical and sorted)
        self.mergedData["Year"] = pd.Categorical(
            self.mergedData["Year"],
            ordered=True,
            categories=sorted(self.mergedData["Year"].unique())
        )
        self.mergedData = self.mergedData.sort_values("Year")

        # Create line plot for female percentage only
        sns.lineplot(
            x="Year",
            y="FemalePercentage",
            data=self.mergedData,
            color='indigo',
            marker='o',
            markeredgecolor='black',
            linewidth=2.5,
            label='Women authors',  # Modified label
            ax=ax
        )

        # Title and labels
        ax.set_title(
            'Yearly trend of women authors',
            fontfamily=FONTFAMILY,
            fontsize=TITLEFONTSIZE,
            pad=20
        )
        ax.set_xlabel('Year', fontfamily=FONTFAMILY, fontsize=FONTSIZE, labelpad=15)
        ax.set_ylabel('Percentage of women authors (%)', fontfamily=FONTFAMILY, fontsize=FONTSIZE, labelpad=20)

        # Customize ticks
        ax.set_xticks(self.mergedData['Year'])
		#ax.set_ylim(26,29)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontfamily(FONTFAMILY)
            label.set_fontsize(FONTSIZE)
        plt.xticks(rotation=45)

        # Grid and legend with "Gender" title
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        legend = ax.legend(
            frameon=True,
            fontsize=FONTSIZE,
            loc='upper right'
        )
        legend.get_title().set_fontsize(FONTSIZE)  # Set title font size
        legend.get_frame().set_alpha(0.8)
        for text in legend.get_texts():
            text.set_fontfamily(FONTFAMILY)

        # Adjust layout and save
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
        plt.savefig(PLOTYEARPERCENTAGE, bbox_inches='tight')
        plt.show()
"""
	def GenerateBarChart(self):
		fig, ax1 = plt.subplots(figsize=(18, 12))

		# Set global font properties
		plt.rcParams['font.family'] = FONTFAMILY
		plt.rcParams['font.size'] = FONTSIZE

		# Ensure the column names match those in your dataframe
		if all(col in self.MaximumDataframeWithMaleCount.columns for col in
			   ['Nationality', 'FemaleCount', 'MaleCount', 'FemalePercentage', 'MalePercentage']):

			percent_data = self.MaximumDataframeWithMaleCount.melt(id_vars=["Nationality"],
																   value_vars=["FemalePercentage", "MalePercentage"],
																   var_name="Gender",
																   value_name="Percentage")
			percent_data["Gender"] = percent_data["Gender"].apply(lambda x: "Women" if "Female" in x else "Men")

			# Create barplot for percentages
			sns.barplot(x="Nationality", y="Percentage", hue="Gender", data=percent_data,
						palette={"Women": "purple", "Men": "violet"}, alpha=0.6, ax=ax1)

			# Set the primary y-axis label explicitly after the bar plot
			ax1.set_ylabel('Percentage of women and men authors (%)', labelpad=20)  # Add padding

			# Create lineplot for counts
			ax2 = ax1.twinx()
			# indigo
			sns.lineplot(x="Nationality", y="FemaleCount", data=self.MaximumDataframeWithMaleCount, color='crimson',
						 marker='o', markeredgecolor='crimson', sort=False, label='Count of women authors', ax=ax2)
			# darkviolet
			# deeppink
			# orangered
			sns.lineplot(x="Nationality", y="MaleCount", data=self.MaximumDataframeWithMaleCount, color='darkorange',
						 marker='s', markeredgecolor='darkorange', sort=False, label='Count of men authors', ax=ax2)

			# Add titles and labels with padding and explicit font properties
			ax1.set_title('Percentage of women and men authors per country',
						  fontfamily=FONTFAMILY,
						  fontsize=TITLEFONTSIZE,
						  pad=20)

			ax1.set_xlabel('Country',
						   fontfamily=FONTFAMILY,
						   fontsize=FONTSIZE,
						   labelpad=15)

			ax1.set_ylabel('Percentage of women and men authors (%)',
						   fontfamily=FONTFAMILY,
						   fontsize=FONTSIZE,
						   labelpad=20)

			ax2.set_ylabel('Number of women and men authors',
						   fontfamily=FONTFAMILY,
						   fontsize=FONTSIZE,
						   labelpad=20)

			# Apply font to tick labels
			for label in ax1.get_xticklabels() + ax1.get_yticklabels():
				label.set_fontfamily(FONTFAMILY)
				label.set_fontsize(FONTSIZE)

			for label in ax2.get_yticklabels():
				label.set_fontfamily(FONTFAMILY)
				label.set_fontsize(FONTSIZE)

			# Get current y-axis limits
			y1_min, y1_max = ax1.get_ylim()
			y2_min, y2_max = ax2.get_ylim()

			# Extend the y-axis limits to make room for legends at the top
			# Increase the upper limit by 20% to create space
			ax1.set_ylim(y1_min, y1_max * 1.2)
			ax2.set_ylim(y2_min, y2_max * 1.2)

			# Move the legends completely outside the plot area
			# For the percentage legend (bar chart)
			legend1 = ax1.legend(title="Gender", loc='upper left',
								 frameon=True, fontsize=FONTSIZE)
			legend1.get_title().set_fontsize(FONTSIZE)

			# For the count legend (line chart) - place it below the first legend
			legend2 = ax2.legend(loc='upper right',
								 frameon=True, fontsize=FONTSIZE)

			# Make the legend box transparent
			legend1.get_frame().set_alpha(0.8)
			legend2.get_frame().set_alpha(0.8)

			# Apply font to legend text
			for text in legend1.get_texts() + legend2.get_texts():
				text.set_fontfamily(FONTFAMILY)
				text.set_fontsize(FONTSIZE)

			# Add a grid for better readability
			ax1.grid(axis='y', linestyle='--', alpha=0.7)

			# Adjust layout to prevent plot covering labels
			# Using less extreme values since legends are now inside
			fig.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.15)

			# Show the plot
			# plt.tight_layout()  # Adjust layout automatically
			plt.show()

			# Save the plot as an image
			plt.savefig(BARPLOTCOUNTRY, bbox_inches='tight')
"""
#COMPUTE THE P-VALUE
class ComputePValue():
	def Computation(self, femaleReportsPercent):
		#Define the % of male
		maleReportsPercent = 100 - femaleReportsPercent

		#Observed and expected counts
		observedPercents = [femaleReportsPercent, maleReportsPercent]
		expectedPercents = [50, 50]

		#Calculate the chi-squared test statistic and p-value
		chi2Statistic, pValue = stats.chisquare(f_obs=observedPercents, f_exp=expectedPercents)

		return pValue

###MAIN FUNCTION
def main():
	#Generate the instance for the DataCleaning (and run the __init__ part)
	DataCleaningInstance = DataCleaning()
	#Call the class to clean the dataframe and obtain the # of authors with unknown gender
	dataframe, unknownGenderCount = DataCleaningInstance.CallFunctions()

	# Generate the instance for the DataCount
	DataCountInstance = DataCount()
	#Call the class to perform initial statistics and obtain the # of authors, # of journals, # of female authors and % of female authors
	totalReports, numberJournals, numberCountries, femaleReports, femaleReportsPercent = DataCountInstance.CallFunctions(dataframe)

	# Generate the instance for the CountriesStatistics
	CountriesStatisticsInstance = CountriesStatistics()
	#Call the class to perform the statistics based on the countries and obtain the countries with highest % of female authors and the country with the lowest % of female authors
	firstCountry, secondCountry, thirdCountry, lastCountry = CountriesStatisticsInstance.CallFunctions(dataframe)

	#Generate the instance for the JournalsStatistics
	JournalsStatisticsInstance = JournalsStatistics()
	#Call the class to perform the statistics based on the journals and obtain the journals with highest % of female authors and the journal with the lowest % of female authors
	firstJournal, secondJournal, thirdJournal, lastJournal = JournalsStatisticsInstance.CallFunctions(dataframe)

	#Generate the instance for the YearsStatistics
	YearsStatisticsInstance = YearsStatistics()
	#Call the class to perform the statistics based on the years of publication
	YearsStatisticsInstance.CallFunctions(dataframe)

	#Generate the instance for the ComputePValue
	ComputePValueInstance = ComputePValue()
	#Call the class to compute the P-value
	pValue = ComputePValueInstance.Computation(femaleReportsPercent)

	#Generate a txt file with all the statistics
	saveStatisticsTxt(unknownGenderCount, totalReports, numberJournals, numberCountries, femaleReports, femaleReportsPercent, firstCountry, secondCountry, thirdCountry, lastCountry, firstJournal, secondJournal, thirdJournal, lastJournal, pValue)

##SAVE A TXT FILE WITH ALL STATISTICS
def saveStatisticsTxt(unknownGenderCount, totalReports, numberJournals, numberCountries, femaleReports, femaleReportsPercent, firstCountry, secondCountry, thirdCountry, lastCountry,firstJournal, secondJournal, thirdJournal, lastJournal, pValue):
	with open(FIRSTAUTHORSTATISTICS, 'w') as file:
		file.write(f'Unknown Gender Count: {unknownGenderCount}\n')
		file.write(f'Total Reports: {totalReports}\n')
		file.write(f'Number of Journals: {numberJournals}\n')
		file.write(f'Number of Countries: {numberCountries}\n')
		file.write(f'Number of Female Reports: {femaleReports}\n')
		file.write(f'Percentage of Female Reports: {femaleReportsPercent:.2f}%\n')
		file.write(f'The 1st country with highest % of female reports: {firstCountry}\n')
		file.write(f'The 2st country with highest % of female reports: {secondCountry}\n')
		file.write(f'The 3st country with highest % of female reports: {thirdCountry}\n')
		file.write(f'The country with lowest % of female reports: {lastCountry}\n')
		file.write(f'The 1st journal with highest % of female reports: {firstJournal}\n')
		file.write(f'The 2st journal with highest % of female reports: {secondJournal}\n')
		file.write(f'The 3st journal with highest % of female reports: {thirdJournal}\n')
		file.write(f'The journal with lowest % of female reports: {lastJournal}\n')
		file.write(f'The P-value for % of female first authors: {pValue:.20f}\n')

if __name__ == '__main__':
	main()


