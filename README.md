# Run Instructions
1. Navigate to the root directory of the project which contains the frontend/ and backend/ folders along with this README.
2. Set up a virtual environment in the backend directory
```shell
virtualenv --python=python3 backend
```
3. Activate the virtual environment with:\
```shell
source backend/bin/activate
```
4. Install the required packages from requirements.txt with: 
```shell
pip install -r backend/requirements.txt
```
5. Navigate to the frontend directory.
```shell
cd frontend
```
6. Install the npm packages in the frontend directory with:
```shell
npm install
```
7. Navigate to the root-directory of the project and run the startup script: 
```shell
cd ..
./run-local
```

# Future Directions
* Gather better data: Lots of assumptions were made about disorder probability that could be drastically improved  with data from the real-world about the probability of these disorders occurring.
* Testing for the backend: Ultimately I was crunched for time and did not have time to write unit tests for the backend.
* Testing for the frontend: I don't have experience with frontend testing frameworks, but acquiring that experience and testing the frontend would be a great addition.
* Breaking out frontend code into separate components: There are a few chunks of code that could be better organized by being placed into their own components.
* Design polish in frontend: Some things like adding logos, custom fonts, etc would improve the look of the project.

# Coding Project:

Your task is to build a mini symptom checker. The goal is to figure out which rare conditions a user has, given the symptoms they input. Your task is as follows:

1. Parse this XML file here (http://www.orphadata.org/data/xml/en_product4.xml) to find the relationship between diseases and symptoms.
2. Write a function which accepts a list of symptoms (HPO IDs) as input and returns an ordered list of the most relevant rare conditions. The method by which relevant conditions are selected is up to your discretion.
3. Set up a server using Python Django/FastAPI/Flask which can accept symptoms via a HTTP request and return relevant conditions.
    1. Python Django is preferred, but if you do not know Python or Django, you may use a language or framework of your choice.
4. Set up a React TS frontend which allows users to input symptoms, hits your API, and displays the conditions returned from the Python server. I will leave it up to you to decide how you want to display symptoms. If you are not comfortable with React you can use another JS or TS based framework or simple HTML.
5. Please upload all code to a GitHub repository with instructions on how it works and how to run it in the README. Finally, please make a list of edge cases that you might check for and future directions you would take the project. Send the link to your repo before 9pm ET the day before your debrief session.

# Criteria

Below are the things we will be looking for when evaluating your project. Do not worry about Bonus points unless you have extra time to work on them.

## What we are looking for:

1. Creativity and organization
2. Production-ready bug-free code:
    1. Please make sure you use known best practices to design and structure your code for the best readability, testability, and maintainability.
3. A functional UX:
    1. Ability to easily select symptoms
    2. Ability to view an ordered list of relevant conditions given the input symptoms
4. An algorithm which roughly selects and ranks appropriate conditions based on symptoms
5. A thoughtful list of edge cases and future directions

## Bonus points:

1. Unit testing of backend functions
2. Using database models to store/query symptoms and conditions
3. Easy development setup using something like Docker Compose
4. A beautifully designed UI
5. A symptom search tool for selecting symptoms
6. A UI with enriched info allowing users to learn more about the symptoms/conditions
7. Using Data Science or ML techniques to predict conditions from symptoms

## Extra bonus points:

1. Unit testing of frontend functions
2. Deployment on simple cloud provider like Heroku
