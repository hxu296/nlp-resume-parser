### Resume Parser Service

GPT-3 based resume parser as a REST API that transforms a [resume pdf like this](https://github.com/hxu296/resume-parser-service/blob/main/examples/402_huanxu_sde.pdf) to a [json like this](https://github.com/hxu296/resume-parser-service/blob/main/examples/resume.json). Parsing a resume pdf costs around 15 seconds and $0.06 (explains why there is not a live demo website). ***Please note that there are more efficient ways to do this by tuning your GPT-3 prompt, and this repository only serves as an example of what GPT-3 is capable of.***

### Quick Start
Install dependencies, run the `bash build.sh` in the project root.   
To run the RESTFull service in 2 steps:
1. get your [OpenAI API Key](https://openai.com/api/)
2. set the environment variable OPENAI_API_KEY to your API key: `export OPENAI_API_KEY=YOURKEY`
3. run `bash run.sh` in the project root. By default, a Flask server will start listening to port 5000 of localhost. Feel free to check it out with your browser.

### Supported Fields
- Basic Information
  - [x] fist name
  - [x] last name
  - [x] full name
  - [x] email 
  - [x] U.S. phone number
  - [x] location
  - [x] portfolio website URL
  - [x] LinkedIn URL
  - [x] GitHub main page URL
- Education
  - [x] university
  - [x] education level
  - [x] graduation year
  - [x] graduation month
  - [x] majors
  - [x] GPA
- Experience
  - [x] job title
  - [x] company
  - [x] location
  - [x] duration
  - [x] job content
