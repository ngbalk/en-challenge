import csv, dateparser, re

class DataCleaner():
	"""Parses entity information from CSV, sanitizes, and writes to CSV"""

	statesDict = {}
	fieldNames = []

	def __init__(self, statesFileName='state_abbreviations.csv'):
		self.__loadStatesFile(statesFileName)

	def __loadStatesFile(self, fileName):
		with open(fileName) as f:
		    reader = csv.reader(f)
		    for row in reader:
				self.statesDict[row[0]] = row[1]


	def readCsvAndWriteSolutionCsv(self, inputFileName, outputFileName):
		data = self.__readCsv(inputFileName)
		self.__writeCsv(data)


	def __readCsv(self, fileName):
		data = []
		with open(fileName) as f:
			reader = csv.DictReader(f)

			# save fieldnames in original order for writing new csv later
			self.fieldNames = reader.fieldnames
			self.fieldNames.append("start_date_description")
			
			for row in reader:
				data.append(self.__sanitizeEntity(row))
		return data

	# data should be in format of list of dicts (i.e. [{},{}])
	def __writeCsv(self, data):
		with open('solution.csv', 'wb') as output_file:
		    dict_writer = csv.DictWriter(output_file, self.fieldNames)
		    dict_writer.writeheader()
		    dict_writer.writerows(data)


	def __sanitizeEntity(self, entity):

		# clean bio string
		dirtyBio = entity['bio']
		entity['bio'] = self.__cleanBio(dirtyBio)

		# replace state abrev. with full state name
		stateAbr = entity['state']
		entity['state'] = self.__convertToFullStateName(stateAbr)

		# normalize date format to YYYY-MM-DD
		dateString = entity['start_date']
		normalizedDate = self.__normalizeDateFormats(dateString)

		# if invalid date format, add extra field to entity with 'start_date_description'
		if(not normalizedDate):
			entity['start_date_description'] = entity['start_date']
		else:
			entity['start_date_description'] = None
		entity['start_date'] = normalizedDate

		return entity


	def __cleanBio(self, bioString):
		# removes extra spaces and newline characters
		return " ".join(bioString.split())


	def __convertToFullStateName(self, stateAbr):
		return self.statesDict[stateAbr]


	def __normalizeDateFormats(self, dateString):

		# attempt to filter obvious non-dates (and improve performance marginally)
		if not re.search(r'\d', dateString):
			return None

		# parse with strict parsing to ensure Y,M,D all provided
		dt = dateparser.parse(dateString,settings={"STRICT_PARSING":True})

		# check to see if succesfully parsed
		if not dt:
			return None

		# return in format YYYY-MM-DD
		return dt.strftime('%Y-%m-%d')


dataCleaner = DataCleaner()
dataCleaner.readCsvAndWriteSolutionCsv('test.csv','solution.csv')
