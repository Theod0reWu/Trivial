![trivial](https://github.com/user-attachments/assets/21cb97d8-d4b1-4934-a868-79da2b74b61a)
<hr>
<h3 align="center"> Made by Theodore Wu and Calvin Chu </h3>

Trivial empowers users to engage in continuous learning through an immersive trivia experience fueled by Google's AI. By seamlessly blending the vast knowledge of Wikipedia with real-time competitive gameplay, Trivial creates a dynamic environment where players can explore their interests, discover new passions, and challenge themselves intellectually. Whether playing solo or competing against friends, users are encouraged to expand their horizons and test their trivia prowess.  Leveraging the Gemini API, Trivial generates a vast supply of engaging and informative trivia content, from intriguing category titles to thought-provoking clues and accurate answers. Wikipedia serves as a rich foundation, providing context and depth to the generated questions, ensuring that players not only have fun but also learn something new with every game.
<h3 align="center"> Intriguing Category Titles! </h3>

![tutorial_board](https://github.com/user-attachments/assets/4e2bbb37-8cce-4c66-91a2-9e1ef495c99e)

<h3 align="center"> Exciting Trivia! </h3>

![tutorial_clue](https://github.com/user-attachments/assets/42ae3ff0-0950-4730-b033-b3220c191635)


## Backend
The backend for Trivial is a Python-based system built on the FastAPI framework, leveraging SocketIO for real-time communication, asyncio for asynchronous task management, and Firestore for flexible data storage. The FastAPI high-performance web framework handles RESTful API endpoints for various room-setup related operations, such as creating rooms and player sessions. SocketIO enables real-time bidirectional communication between the server and clients, ensuring seamless updates on game progress, timers, and player scores. 

To generate a Trivial board, a dedicated process is spawned for each room to efficiently manage Gemini API interactions. Upon successful generation, the board data is persisted to the Firestore database for subsequent retrieval as the game unfolds. To maintain game pace and urgency, the backend continuously creates timers to give players a limited amount of time to answer questions and buzz-in. Leveraging the asyncio library, these timers operate asynchronously, preventing blocking behavior and ensuring smooth gameplay. Timer start and end times are recorded in the Firestore database for pausing functionality. By judiciously utilizing asyncio.sleep, the system accommodates other critical asynchronous tasks within the game loop.

## Frontend

The frontend for Trivial, is made with Angular. Leveraging Angular's component-based architecture, the UI is structured into reusable components for efficient development and maintenance. The frontend establishes a WebSocket connection using SocketIO to facilitate real-time interactions with the backend, ensuring seamless updates to the game state, timers, and player scores. Angular's reactive programming capabilities, powered by RxJS, are utilized to manage asynchronous data streams and handle user interactions effectively.

## Tech stack
- Python 3.12 + [FastAPI](https://fastapi.tiangolo.com/) API development.
- [Firestore](https://firebase.google.com/docs/firestore) for storing user data, game data and room specific data. 
- [Wikipedia](https://pypi.org/project/wikipedia/) for fetching data from Wikipedia and adding context to clue generation to ensure factually correct clues.
- [Gemini](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini) via [VertexAI](https://cloud.google.com/vertex-ai) for generating categories, category titles, clues and answers.
- [Angular](https://angular.dev/) for frontend developement

## Project Architecture Overview
![architecture drawio](https://github.com/user-attachments/assets/7c7cc33a-8686-4a6c-a57f-b6cf4b849e1e)

## Game Generation

### Category Generation

Trivia categories are difficult to generate for a couple reasons. First, Gemini does not handle returning random answers very well. Secondly, it is hard to ensure the categories are not too specific but also not too general. To create categories for Trivial a novel method was used involving something we call a Category Tree. A Category is a tree data structure composed of nodes. Each node in the tree holds a trivia topics for example "math" or "literature". Each node can have any number of children, with the only stipulation being that each child node is considered a "subcategory" of the parent node. What constitutes a "subcategory" is not well defined, but this tree structure allows us to use the Gemini API to generate various categories. 

### Clue and Answer Generation

To increase the variety and variability of the trivia answers, Gemini is prompted to respond with more answers than needed to generate the board. Once this happens enough answers are randomly selected to fufill the requirements for the number of clues per category.

To enhance the accuracy of generated trivia, the backend incorporates the Retrieval-Augmented Generation (RAG) method. By leveraging factual data from Wikipedia as context, the system mitigates the risk of the model producing incorrect or misleading information. This approach significantly improves the overall quality and reliability of the generated trivia clues, ensuring that players are challenged with accurate and informative questions. 

## Server-Client Flow Chart
![server-client flow chart drawio (1)](https://github.com/user-attachments/assets/577e5153-53ba-4a45-aeb5-022539ec16b9)

## Project setup

### Backend
Nativate to the server directory
```
cd server
```
Install the python packages
```
pip install -r requirements.txt
```
Create [firestore credentials](https://firebase.google.com/docs/firestore/quickstart#python) and place the file in the server directory. <br>
Then set the environment variable FIREBASE_PATH to the name of the file with the credentials: <br>
In Windows:
```
set FIREBASE_PATH=<CREDENTIALS_FILE_NAME>.json
```
In Linux:
```
export FIREBASE_PATH=<credentials file name>.json
```
Create a [Gemini API Key](https://ai.google.dev/gemini-api/docs/quickstart?lang=python) and set the environment variable. <br>
In Windows:
```
set API_KEY=<YOUR_API_KEY>
```
In Linux:
```
export API_KEY=<YOUR_API_KEY>
```
(Optional): Choose the port by setting the ```PORT``` environment variable. <br>
Run the server directly or with uvicorn (hosts on port 8000 by default) <br>
```
python main.py
```
or 
```
uvicorn main:app --host <localhost> --port <YOUR_CHOSEN_PORT>
```
### Frontend
Install node.js and navigate to the client directory. <br>
```
cd client
```
To install dependencies run:
```
npm install
```
Host the server with:
```
ng serve
```
(Note: build the frontend in developement mode when running locally to avoid errors)
