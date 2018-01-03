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
scores = []
questionVal = 0

#Constants

TIME_LIMIT = 30

# Life cycle

@ask.launch
def launch():
	prompt = 'Welcome to Mathketball... If this is your first time playing, say how do I play? Then say start when you are ready to play!'
	reprompt = 'Say start when you are ready to play!'
	return question(prompt).reprompt(reprompt)

@ask.session_ended
def sessionEnd():
        print('sessionEnded')
        return '', 200

# Intents

@ask.intent('PlayIntent', convert={'Players': int})
def playGame(Players):
        print('Players=' + str(Players))
        if Players:
                setPlayers(Players)
                setScores([0]*Players)
                return startRound(1)
        else:
                return delegate('')
    
@ask.intent('QuestionIntent')
def getQuestion(Type):
        print(Type)
        currentTime = time.time()
        if currentTime - getStartTime() > TIME_LIMIT:
                print('Time is up!')
                currPlyr = getCurrentPlayer()
                if currPlyr == getPlayers():
                        return reportScores()
                return startRound(currPlyr + 1, timesUP=True)
        q = ''
        if Type == 'free throw':
                setQuestionVal(1)
                num1 = random.randint(1,10)
                num2 = random.randint(1,10)
                q = str(num1) + ' plus ' + str(num2)
                setCurrentAnswer(num1+num2)
        elif Type == '2 pointer':
                setQuestionVal(2)
                num1 = random.randint(1,10)
                num2 = random.randint(1,10)
                q = str(num1) + ' times ' + str(num2)
                setCurrentAnswer(num1*num2)
        elif Type == '3 pointer':
                setQuestionVal(3)
                num1 = random.randint(1,10)
                num2 = random.randint(1,10)
                num3 = random.randint(1,10)
                q = 'What\'s the average of {}, {}, and {}?'.format(num1, num2, num3)
                setCurrentAnswer((num1+num2+num3)/3.0)
        elif Type == 'buzzer beater':
                setQuestionVal(4)
                num1 = random.randint(50,100)
                num2 = random.randint(1,10)
                q = 'What is the remainder of {} divided by {}?'.format(num1, num2)
                setCurrentAnswer(num1%num2)

        return question(q).reprompt(q)

@ask.intent('AnswerIntent', convert={'Answer' : int})
def answer(Answer):
    if Answer == getCurrentAnswer():
            plyrScores = getScores()
            plyrScores[getCurrentPlayer()-1] += getQuestionVal()
            setScores(plyrScores)
            return question('Correct').reprompt('Correct')
    return question('Incorrect').reprompt('Incorrect')

@ask.intent('RulesIntent')
def giveRules():
    return question('Each player has {} seconds on the shot clock to answer as many questions as possible...Say free throw, 2 pointer, 3 pointer, or buzzer beater for a question. A free throw is 1 point, a 2 pointer is 2, a 3 pointer is 3, and a buzzer beater is worth 4. The more points it\'s worth, the harder the question! Good luck, and go Duke!'.format(TIME_LIMIT))

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

def setScores(val):
        global scores
        scores = val

def getScores():
        return scores

def setQuestionVal(val):
        global questionVal
        questionVal = val

def getQuestionVal():
        return questionVal

# Game logic
def startRound(playerNum, timesUp=False):
        setStartTime(time.time())
        setCurrentPlayer(playerNum)
        prompt = 'Ok player {} you have {} seconds on the shot clock...start!'.format(playerNum, TIME_LIMIT)
        if timesUp:
                prompt = 'Times up! ' + prompt
        return question(prompt)

def reportScores():
        scrs = getScores()
        winner = scrs.index(max(scrs)) + 1
        prompt = 'The scores are in! Player {} has won with a score of {}.'.format(winner, scrs[winner-1])
        if getPlayers() == 1:
                return quitGame(text=prompt)
        
        for i in range(len(scrs)):
                prompt += ' Player {} scored {},'.format(i+1, scrs[i])
        prompt += ' and Player {} scored {}.'.format(getPlayers(), scrs[-1])
        return quitGame(text=prompt)

def quitGame(text = ''):
	return statement(text + ' Thank you for playing...Come back soon!')

if __name__ == '__main__':
	app.run(debug=True)

