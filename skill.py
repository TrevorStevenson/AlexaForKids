from flask import Flask
from flask_ask import Ask, statement, question, delegate, audio
import random
import time

app = Flask(__name__)
ask = Ask(app, '/')

# Global vars

numPlayers = 0
currentAnswer = ''
startTime = 0
currentPlayer = 1

# Life cycle

@ask.launch
def launch():
	prompt = 'Welcome to Mathketball... Say start when you are ready to play!'
	reprompt = 'Say start when you are ready to play!'
	return question(prompt).reprompt(reprompt)

@ask.session_ended
def sessionEnd():
	return '', 200

# Intents

@ask.intent('PlayIntent', convert={'Players': int, 'Difficulty': str})
def playGame(Players, Difficulty):
        print('Players=' + str(Players))
        print('Difficulty=' + str(Difficulty))
        if Players and Difficulty:
                setPlayers(Players)
                return startRound(1)
        else:
                return delegate('')
    
@ask.intent('QuestionIntent')
def getQuestion(Type):
        currentTime = time.time()
        if currentTime - getStartTime() > 30:
                
        q = ''
        if Type == 'free throw':
                num1 = random.randint(1,10)
                num2 = random.randint(1,10)
                q = str(num1) + ' times ' + str(num2)
        elif Type == '2 pointer':
                q = '3 time 10 divided by 5'
        elif Type == '3 pointer':
                q = 'What\'s the average of 4, 3, and 7?'
        elif Type == 'buzzer beater':
                q = '12 times 11'

        return question(q)

@ask.intent('AnswerIntent')
def answer(Answer):
    print(Answer)

@ask.intent('RulesIntent')
def giveRules():
    return statement('There are 4 quarters in every game. Each player has 30 seconds on the shot clock to answer as many questions as possible...Say free throw, 2 pointer, 3 pointer, or buzzer beater for a question. A free throw is 1 point, a 2 pointer is 2, a 3 pointer is 3, and a buzzer beater is worth 4. The more points it\'s worth, the harder the question! Good luck, and go Duke!')

@ask.intent('QuitIntent')
def quitIntent():
	return quitGame()

# Properties

def setPlayers(val):
	global numPlayers
	numPlayers = val

def getPlayers():
	return numPlayers

def setCurrentAnswer(val):
        global currentAnswer
        currentAnswer = val

def getCurrentAnswer():
        return currentAnswer

def setStartTime(val):
        global startTime
        startTime = val

def getStartTime():
        return startTime

def setCurrentPlayer(val):
        global currentPlayer
        currentPlayer = val

def getCurrentPlayer():
        return currentPlayer

# Game logic
def startRound(playerNum):
        setStartTime(time.time())
        prompt = 'Ok player ' + str(playerNum) + 'you have 30 seconds on the shot clock...start!'
        return question(prompt)

def quitGame(text = ''):
	return statement(text + 'Thank you for playing...Come back soon!')

if __name__ == '__main__':
	app.run(debug=True)

