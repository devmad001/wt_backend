"""

https://github.com/neo4j-partners/neo4j-generative-ai-google-cloud

SEC + resume demo

person_prompt_tpl="""From the Resume text for a job aspirant below, extract Entities strictly as instructed below
1. First, look for the Person Entity type in the text and extract the needed information defined below:
   `id` property of each entity must be alphanumeric and must be unique among the entities. You will be referring this property to define the relationship between entities. NEVER create new entity types that aren't mentioned below. Document must be summarized and stored inside Person entity under `description` property
    Entity Types:
    label:'Person',id:string,role:string,description:string //Person Node
2. Description property should be a crisp text summary and MUST NOT be more than 100 characters
3. If you cannot find any information on the entities & relationships above, it is okay to return empty value. DO NOT create fictious data
4. Do NOT create duplicate entities
5. Restrict yourself to extract only Person information. No Position, Company, Education or Skill information should be focussed.
6. NEVER Impute missing values
Example Output JSON:
{"entities": [{"label":"Person","id":"person1","role":"Prompt Developer","description":"Prompt Developer with more than 30 years of LLM experience"}]}

Question: Now, extract the Person for the text below -
$ctext

Answer:
"""

postion_prompt_tpl="""From the Resume text for a job aspirant below, extract Entities & relationships strictly as instructed below
1. First, look for Position & Company types in the text and extract information in comma-separated format. Position Entity denotes the Person's previous or current job. Company node is the Company where they held that position.
   `id` property of each entity must be alphanumeric and must be unique among the entities. You will be referring this property to define the relationship between entities. NEVER create new entity types that aren't mentioned below. You will have to generate as many entities as needed as per the types below:
    Entity Types:
    label:'Position',id:string,title:string,location:string,startDate:string,endDate:string,url:string //Position Node
    label:'Company',id:string,name:string //Company Node
2. Next generate each relationships as triples of head, relationship and tail. To refer the head and tail entity, use their respective `id` property. NEVER create new Relationship types that aren't mentioned below:
    Relationship definition:
    position|AT_COMPANY|company //Ensure this is a string in the generated output
3. If you cannot find any information on the entities & relationships above, it is okay to return empty value. DO NOT create fictious data
4. Do NOT create duplicate entities. 
5. No Education or Skill information should be extracted.
6. DO NOT MISS out any Position or Company related information
7. NEVER Impute missing values
 Example Output JSON:
{"entities": [{"label":"Position","id":"position1","title":"Software Engineer","location":"Singapore",startDate:"2021-01-01",endDate:"present"},{"label":"Position","id":"position2","title":"Senior Software Engineer","location":"Mars",startDate:"2020-01-01",endDate:"2020-12-31"},{label:"Company",id:"company1",name:"Neo4j Singapore Pte Ltd"},{"label":"Company","id":"company2","name":"Neo4j Mars Inc"}],"relationships": ["position1|AT_COMPANY|company1","position2|AT_COMPANY|company2"]}

Question: Now, extract entities & relationships as mentioned above for the text below -
$ctext

Answer:
"""

results
{'entities': [{'label': 'Person',
   'id': 'person1',
   'role': 'Developer',
   'description': 'Developer with 10 years of experience in IT industry'},
  {'label': 'Position',
   'id': 'position1',
   'title': 'Developer',
   'location': 'Batavia, OH',
   'startDate': '2016-06-01',
   'endDate': 'present'},
  {'label': 'Company', 'id': 'company1', 'name': 'TATA CONSULTANTCY SERVICE'},
  {'label': 'Skill', 'id': 'skill1', 'name': 'SQL', 'level': 'expert'},
  {'label': 'Skill', 'id': 'skill2', 'name': 'Java', 'level': 'expert'},
  {'label': 'Skill', 'id': 'skill3', 'name': 'Linux', 'level': 'expert'},
  {'label': 'Skill', 'id': 'skill4', 'name': 'Splunk', 'level': 'expert'},
  {'label': 'Skill', 'id': 'skill5', 'name': 'front end', 'level': 'expert'},
  {'label': 'Skill', 'id': 'skill6', 'name': 'Db2', 'level': 'expert'},
  {'label': 'Skill', 'id': 'skill7', 'name': 'HTML5', 'level': 'intermediate'},
  {'label': 'Skill', 'id': 'skill8', 'name': 'CSS3', 'level': 'intermediate'},
  {'label': 'Skill', 'id': 'skill9', 'name': 'XML', 'level': 'intermediate'},
  {'label': 'Skill', 'id': 'skill10', 'name': 'JSON', 'level': 'intermediate'},
  {'label': 'Skill',
   'id': 'skill11',
   'name': 'JavaScript',
   'level': 'intermediate'},

   run_query('CREATE CONSTRAINT unique_person_id IF NOT EXISTS FOR (n:Person) REQUIRE (n.id) IS UNIQUE')
run_query('CREATE CONSTRAINT unique_position_id IF NOT EXISTS FOR (n:Position) REQUIRE (n.id) IS UNIQUE')
run_query('CREATE CONSTRAINT unique_skill_id IF NOT EXISTS FOR (n:Skill) REQUIRE n.id IS UNIQUE')
run_query('CREATE CONSTRAINT unique_education_id IF NOT EXISTS FOR (n:Education) REQUIRE n.id IS UNIQUE')
run_query('CREATE CONSTRAINT unique_company_id IF NOT EXISTS FOR (n:Company) REQUIRE n.id IS UNIQUE')



SEC=====================

mgr_info_tpl = """From the text below, extract the following as json. Do not miss any of these information.
* The tags mentioned below may or may not namespaced. So extract accordingly. Eg: <ns1:tag> is equal to <tag>
* "name" - The name from the <name> tag under <filingManager> tag
* "street1" - The manager's street1 address from the <com:street1> tag under <address> tag
* "street2" - The manager's street2 address from the <com:street2> tag under <address> tag
* "city" - The manager's city address from the <com:city> tag under <address> tag
* "stateOrCounty" - The manager's stateOrCounty address from the <com:stateOrCountry> tag under <address> tag
* "zipCode" - The manager's zipCode from the <com:zipCode> tag under <address> tag
* "reportCalendarOrQuarter" - The reportCalendarOrQuarter from the <reportCalendarOrQuarter> tag under <address> tag
* Just return me the JSON enclosed by 3 backticks. No other text in the response

Text:
$ctext
"""

filing_info_tpl = """The text below contains a list of investments. Each instance of <infoTable> tag represents a unique investment. 
For each investment, please extract the below variables into json then combine into a list enclosed by 3 back ticks. Please use the quated names below while doing this
* "cusip" - The cusip from the <cusip> tag under <infoTable> tag
* "companyName" - The name under the <nameOfIssuer> tag.
* "value" - The value from the <value> tag under <infoTable> tag. Return as a number. 
* "shares" - The sshPrnamt from the <sshPrnamt> tag under <infoTable> tag. Return as a number. 
* "sshPrnamtType" - The sshPrnamtType from the <sshPrnamtType> tag under <infoTable> tag
* "investmentDiscretion" - The investmentDiscretion from the <investmentDiscretion> tag under <infoTable> tag
* "votingSole" - The votingSole from the <votingSole> tag under <infoTable> tag
* "votingShared" - The votingShared from the <votingShared> tag under <infoTable> tag
* "votingNone" - The votingNone from the <votingNone> tag under <infoTable> tag

Text:
$ctext
"""

  
https://github.com/neo4j-partners/neo4j-generative-ai-google-cloud/blob/main/assetmanager/notebook.ipynb

  From the text below, extract the following as json. Do not miss any of these information.
* The tags mentioned below may or may not namespaced. So extract accordingly. Eg: <ns1:tag> is equal to <tag>
* "name" - The name from the <name> tag under <filingManager> tag
* "street1" - The manager's street1 address from the <com:street1> tag under <address> tag
* "street2" - The manager's street2 address from the <com:street2> tag under <address> tag
* "city" - The manager's city address from the <com:city> tag under <address> tag
* "stateOrCounty" - The manager's stateOrCounty address from the <com:stateOrCountry> tag under <address> tag
* "zipCode" - The manager's zipCode from the <com:zipCode> tag under <address> tag
* "reportCalendarOrQuarter" - The reportCalendarOrQuarter from the <reportCalendarOrQuarter> tag under <address> tag
* Just return me the JSON enclosed by 3 backticks. No other text in the response

Text:
<?xml version="1.0" encoding="UTF-8"?>
<edgarSubmission xsi:schemaLocation="http://www.sec.gov/edgar/thirteenffiler eis_13F_Filer.xsd" xmlns="http://www.sec.gov/edgar/thirteenffiler" xmlns:ns1="http://www.sec.gov/edgar/common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <schemaVersion>X0202</schemaVersion>
  <headerData>
    <submissionType>13F-HR</submissionType>
    <filerInfo>
      <liveTestFlag>LIVE</liveTestFlag>
      <flags>
        <confirmingCopyFlag>false</confirmingCopyFlag>
        <returnCopyFlag>false</returnCopyFlag>




LANGCHAIN


_DEFAULT_ENTITY_EXTRACTION_TEMPLATE = """Extract all entities from the following text. As a guideline, a proper noun is generally capitalized. You should definitely extract all names and places.

Return the output as a single comma-separated list, or NONE if there is nothing of note to return.

EXAMPLE
i'm trying to improve Langchain's interfaces, the UX, its integrations with various products the user might want ... a lot of stuff.
Output: Langchain
END OF EXAMPLE

EXAMPLE
i'm trying to improve Langchain's interfaces, the UX, its integrations with various products the user might want ... a lot of stuff. I'm working with Sam.
Output: Langchain, Sam
END OF EXAMPLE

Begin!

{input}
Output:"""
ENTITY_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["input"], template=_DEFAULT_ENTITY_EXTRACTION_TEMPLATE
)
