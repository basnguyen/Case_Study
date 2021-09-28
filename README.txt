List of Folders:
	ESG_Country_Score:
		- Contains World Bank Loader and mapping (Worldbank_CountryCode_to_ISO.csv) & ignore (Ignorelist_Worldbank.ini)
		- WBFields_Loader.csv Fields to Load
		- List_all_ESG_Indicators.xlsx : Current list of indicators in ESG model with their associated weigth in each pillar

	SQL_Database: 
		- ESG_Database.sqlite3 : Prod database, contains most-up-to-date data
		- ESG_Database_DEV.sqlite3 : Worldbank Loader first load in this database, data is checked and then pushed to prod
		- Folder Additional Sources : contains csv files from additional sources (TO DO: write generic loader to treat automaticaly fetch and load these files)

	Spread_Prediction:
		- Spread_Prediction_Prohpet.py : Train models with Prophet from Facebook
		- Spread_Prediction_SARIMA.py : Train models with SARIMA
			+ TO DO : Cross-validation 
		- TO DO : Spread_Prediction_LSTM.py : Train LSTM models
		+ TO DO : Split in training/test set and test performance of three models
	


