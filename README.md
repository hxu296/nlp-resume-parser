## Resume Parser Service

GPT-3 based resume parser as a REST API that transforms a [resume PDF like this](https://github.com/hxu296/resume-parser-service/blob/main/examples/SDE_May2023_HuanXu.pdf) to a [JSON like this](https://github.com/hxu296/resume-parser-service/blob/main/examples/resume.json).

Parsing a resume PDF takes around 15 seconds and costs about $0.01 for every 500 tokens using `text-davinci-002` engine (that's why there is no live demo website). Note that a typical request and response may use 1500 tokens ($0.03), 3000 tokens ($0.06) or more.

Please note that more accurate results may be achieved by fine-tuning GPT-3, but the out-of-the-box results from this repo are already very impressive.

### Quick Start
1. Install Python 3 and pip3. For macOS, see note below.
1. Install all dependencies of `pdftotext` ([see here](https://github.com/jalan/pdftotext)).
1. In a new terminal, update pip3 if needed: `python3 -m pip install --upgrade pip`
1. In another new terminal, clone the repository and move Terminal to the directory.
    * Please close the other terminals and continue in this terminal.
1. Check the versions: `python3 --version` and `pip3 --version`.
1. Run the `./build.sh` in the project root.
1. Get your [OpenAI API Key](https://openai.com/api/).
1. Create a file named `.env` and set your API key in it: `OPENAI_API_KEY=YOURKEY` or set the key in an environment variable: `export OPENAI_API_KEY=YOURKEY`.
1. Run `./run.sh` in the project root.

A Flask server will start listening to port 5001 of localhost. Feel free to [check it out with your browser](http://0.0.0.0:5001/).

#### Note for MacOS

You need to install either XCode or GCC tools ([see here](https://docs.python-guide.org/starting/install3/osx/#doing-it-right)).
* If you install XCode, make sure to run it to complete the setup.
* Then run `xcode-select --install` and complete command-line tools installation.
* Finally install [Homebrew](https://brew.sh/), and use `brew install python` to install Python 3.

### Supported Fields
- Basic Information
  - [x] first name
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
- Job Experience
  - [x] job title
  - [x] company
  - [x] location
  - [x] duration
  - [x] job content
- Project Experience
  - [x] project name
  - [x] project description
