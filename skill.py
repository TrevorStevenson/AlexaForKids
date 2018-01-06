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
threePtScore = 0
gameMode = 0
shotsRemaining = 10
gameActive = False

#Constants

TIME_LIMIT = 30

# Life cycle

@ask.launch
def launch():
        prompt = 'Welcome to Mathketball...What would you like to play?'
        reprompt = 'Say, start a game with 2 players, when you are ready to play!'
        return question(prompt).reprompt(reprompt)

@ask.session_ended
def sessionEnd():
        return '{}', 200

# Intents

@ask.intent('PlayIntent', convert={'Players': int})
def playGame(Players):
        if not Players:
                Players = 1
        setPlayers(Players)
        setScores([0]*Players)
        setGameMode(0)
        setGameActive(True)
        return startRound(1)
    
@ask.intent('QuestionIntent')
def getQuestion(Type):
        if not getGameActive():
                return question('')
        
        currentTime = time.time()
        if currentTime - getStartTime() > TIME_LIMIT:
                currPlyr = getCurrentPlayer()
                if currPlyr == getPlayers():
                        return reportScores()
                return startRound(currPlyr + 1, timesUp=True)
        q = ''
        if Type == '2 pointer':
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
        else:
                setQuestionVal(1)
                num1 = random.randint(1,10)
                num2 = random.randint(1,10)
                q = str(num1) + ' plus ' + str(num2)
                setCurrentAnswer(num1+num2)

        return question(q).reprompt(q)

@ask.intent('AnswerIntent', convert={'Answer' : int})
def answer(Answer):
        if not getGameActive():
                return question('')
        
        if Answer == getCurrentAnswer():
                if getGameMode() == 0:
                        plyrScores = getScores()
                        plyrScores[getCurrentPlayer()-1] += getQuestionVal()
                        setScores(plyrScores)
                        return question('')
                elif getGameMode() == 1:
                        plyrScore = getThreePtScore()
                        plyrScore += getQuestionVal()
                        setThreePtScore(plyrScore)
                        return giveMultQuestion()

        if getGameMode() == 1:
                return giveMultQuestion()
        
        return question('').reprompt('')

@ask.intent('RulesIntent')
def giveRules():
    return question('Mathketball has 2 game modes: game and three point contest. To start a game, say, start a game with 3 players. Each player has {} seconds on the shot clock to answer as many questions as possible...Say free throw, 2 pointer, 3 pointer, or buzzer beater for a question. A free throw is 1 point, a 2 pointer is 2, a 3 pointer is 3, and a buzzer beater is worth 4. The more points it\'s worth, the harder the question! Say, free throw, and wait for the question. Then give the answer! The three point contest is single player, and focuses on multiplication. Start the contest by saying, start a three point contest. You will have 10 total questions to get a high score. The fifth and tenth shots are money balls, worth 2 points! Good luck!'.format(TIME_LIMIT))

@ask.intent('ThreePointContest')
def play3PointContest():
        setGameMode(1)
        setGameActive(True)
        return giveMultQuestion()

@ask.intent('TopFivePlays')
def topTenPlays():
        facts = []
        with open('facts.txt', 'r') as f:
                for line in f.readlines():
                        facts.append(line.strip())

        topTen = random.sample(facts, 5)
        prompt = '<speak><prosody rate="slow">This is Top Five Plays.'
        for i in range(5,0,-1):
                prompt += ' Number {}. {}..'.format(i, topTen[i-1])
        prompt += '</prosody></speak>'
        return statement(prompt)

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

def setThreePtScore(val):
        global threePtScore
        threePtScore = val

def getThreePtScore():
        return threePtScore

def setGameMode(val):
        global gameMode
        gameMode = val

def getGameMode():
        return gameMode

def setShotsRemaining(val):
        global shotsRemaining
        shotsRemaining = val

def getShotsRemaining():
        return shotsRemaining

def setGameActive(val):
        global gameActive
        gameActive = val

def getGameActive():
        return gameActive

# Game logic
def startRound(playerNum, timesUp=False):
        setStartTime(time.time())
        setCurrentPlayer(playerNum)
        prompt = 'Ok player {} you have {} seconds on the shot clock...start!'.format(playerNum, TIME_LIMIT)
        if timesUp:
                prompt = 'Times up! ' + prompt
        return question(prompt)

def reportScores():
        setGameActive(False)
        scrs = getScores()
        winner = scrs.index(max(scrs)) + 1
        prompt = 'The scores are in! Player {} has won with a score of {}.'.format(winner, scrs[winner-1])
        if getPlayers() == 1:
                return quitGame(text=prompt)
        
        for i in range(len(scrs)):
                prompt += ' Player {} scored {},'.format(i+1, scrs[i])
        prompt += ' and Player {} scored {}.'.format(getPlayers(), scrs[-1])
        return quitGame(text=prompt)

def giveMultQuestion():
        shotNum = getShotsRemaining()
        if shotNum == 0:
                prompt = 'Game over! You scored {} points.'.format(getThreePtScore())
                return quitGame(prompt)
        if shotNum % 5 == 1:
                setQuestionVal(2)
                num1 = random.randint(11,16)
                num2 = random.randint(1,10)
        else:
                setQuestionVal(1)
                num1 = random.randint(1,10)
                num2 = random.randint(1,10)

        setCurrentAnswer(num1*num2)
        setShotsRemaining(shotNum - 1)
        prompt = '{} times {}'.format(num1, num2)
        return question(prompt).reprompt(prompt)

def quitGame(text = ''):
        setGameActive(False)
        return statement(text + ' Thank you for playing...Come back soon!')

if __name__ == '__main__':
	app.run(debug=True)

