Formula dictionary:

ESG_SOV_SCORE_OVERALL_GDP_PPP_ADJUSTED : Overall adjusted ESG Score per GDP PPP
ESG_SOV_SCORE_OVERALL : Overall ESG Score
  ESG_SOV_SCORE_PILLAR_E : ESG Score for pillar E
  ESG_SOV_SCORE_PILLAR_S : ESG Score for pillar S
  ESG_SOV_SCORE_PILLAR_G : ESG Score for pillar G

ESG_SOV_COVERAGE : Returns the coverage of each country, also available for each pillar by adding _PILLAR_E for instance

Indicators are organied as follows:
  - TableName : raw data in folder Tables
Views :
    - TableName_LATEST : gets the most recent data for each country
    - TableName_RENORMALIZED or TableName_SCORE : gets a score between 0 and 100
