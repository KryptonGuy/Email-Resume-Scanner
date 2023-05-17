# Cloud-Based Resume Scanner

This project is a cloud-based solution that uses Python and Spacy to scan resumes, extract candidate information, and keywords from email inboxes, streamlining the recruitment process.

## Table of Contents

- [Cloud-Based Resume Scanner](#cloud-based-resume-scanner)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Project Description](#project-description)
  - [Technologies Used](#technologies-used)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributing](#contributing)

## Introduction

The recruitment process can be a time-consuming task that requires a lot of resources and effort. With this cloud-based solution, we aim to streamline the recruitment process by providing an efficient way to scan resumes and extract candidate information and keywords from email inboxes.

## Project Description

This project uses Python and Spacy to extract candidate information and keywords from resumes that are emailed to a designated inbox. The program then stores the extracted data in a database for easy retrieval and analysis.

The program also has the capability to generate reports and insights on candidate information, such as the most common skills, education, and work experience. This feature can be useful for identifying trends and patterns in candidate resumes, which can assist recruiters in making informed hiring decisions.

## Technologies Used

This project was built using the following technologies:

- Python
- Spacy
- Flask
- SQLite
- AWS (Amazon Web Services)

## Installation

To run this project locally, follow these steps:

1. Clone the repository using the command `git clone https://github.com/KryptonGuy/Email-Resume-Scanner.git`
2. Navigate to the project directory using the command `cd Email-Resume-Scanner`
3. Install the required dependencies using the command `pip install -r requirements.txt`
4. Set up your AWS credentials to enable email retrieval. 
5. Run the application using the command `python src/main.py`

## Usage

To use this application, follow these steps:

1. Set up a designated inbox for receiving resumes.
2. Start the application using the command `python main.py`
3. The application will automatically start scanning the designated inbox for new resumes and extract the necessary data.
4. Use the generated reports and insights to analyze candidate information and make informed hiring decisions.

## Contributing

We welcome contributions from the community. If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Push your changes to your fork.
5. Submit a pull request.
