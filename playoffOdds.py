#teamSchedule.py

from pybaseball import schedule_and_record as teamSched
from random import random as rand
from random import randint as ri
import pandas as pd
import csv
import math
import time

def main():
    year=2021
    teamFile="teams.csv"
    teamList=createTeamList(teamFile)
    futureGames=[]
    numSims=1000000
    gameBallast=50
    createSchedule(year,teamList,futureGames)
    runsPerGame=getRunsPerGame(teamList)
    runBallast=runsPerGame*gameBallast
    calcTeamPythags(teamList,gameBallast,runBallast)
    #1 = all current
    lastXGames=1
    runSimulations(teamList,futureGames,numSims,gameBallast,runBallast,lastXGames)
    print("Team            | Tal   AV     MX    MN    |Div    WC     | W-L      PO%")
    teamList=sortDivisionPlayoffStandings(teamList)
    for i in range(len(teamList)):
        if i%5==0 and i>0: print("-----")#"           D     W     AV      MX    MN    PO%")
        team=teamList[i]
        team.printSimSummary(numSims)

def createTeamList(filePath,confirm=False):
    teamList=[]
    with open(filePath,'r') as f:
        reader=csv.reader(f)
        for row in reader:
            newTeam=Team(row[0],row[1],row[2])
            teamList.append(newTeam)
            if confirm==True:
                print("%s added to team list." % newTeam.nickname)
    f.close()
    return teamList

def findTeam(abbr,teamList):
    return [x for x in teamList if x.abbr==abbr][0]

def createSchedule(year,teamList,futureGames):
    for team in teamList:
        team.getCurrentYearSchedule(year,teamList,futureGames)
        team.processPlayedGames()

def getRunsPerGame(teamList):
    runs=0
    games=0
    for team in teamList:
        games+=team.gp
        runs+=team.rf
    return runs/games

def calcTeamPythags(teamList,gameBallast,runBallast):
    for team in teamList:
        team.calcPythag(gameBallast,runBallast)

def runSimulations(teamList,futureGames,numSims,gameBallast,runBallast,lastXGames):
    printStandings=False
    for i in range(numSims):
        #print("Simulation %d" % (i+1))
        simOneSeason(teamList,futureGames,gameBallast,runBallast,printStandings)

def updateTeamPythag(teamList,gameBallast,runBallast):
    for team in teamList:
        team.calcPythag(gameBallast,runBallast)

def simOneSeason(teamList,futureGames,gameBallast=0,runBallast=0,printStandings=False):
    for team in teamList:
        team.resetSimStats()
    for game in futureGames:
        game.simGame()
    for team in teamList:
        team.setSimWinP()
    findDivisionWinners(teamList)
    findWildCards(teamList)
    for team in teamList:
        team.finishSim()
    if printStandings==True:
        printTeamStandings(teamList)

def printTeamStandings(teamList):
    print("AL Standings")
    alWest=Division(teamList[0:5])
    alWest.printStandings("AL West")
    alCentral=Division(teamList[5:10])
    alCentral.printStandings("AL Central")
    alEast=Division(teamList[10:15])
    alEast.printStandings("AL East")
    print("NL Standings")
    nlWest=Division(teamList[15:20])
    nlWest.printStandings("NL West")
    nlCentral=Division(teamList[20:25])
    nlCentral.printStandings("NL Central")
    nlEast=Division(teamList[25:30])
    nlEast.printStandings("NL East")

def findDivisionWinners(teamList):
    alWest=Division(teamList[0:5])
    alWest.determineWinner()
    alCentral=Division(teamList[5:10])
    alCentral.determineWinner()
    alEast=Division(teamList[10:15])
    alEast.determineWinner()
    nlWest=Division(teamList[15:20])
    nlWest.determineWinner()
    nlCentral=Division(teamList[20:25])
    nlCentral.determineWinner()
    nlEast=Division(teamList[25:30])
    nlEast.determineWinner()

def findWildCards(teamList):
    alWildCard=createWildCardList(teamList[0:15])
    alWildCard.determineWildCards()
    nlWildCard=createWildCardList(teamList[15:30])
    nlWildCard.determineWildCards()

def createWildCardList(teamList):
    return Division([x for x in teamList if x.divTitle != 1])

def sortDivisionPlayoffStandings(teamList):
    alWest=teamList[0:5]
    alWest.sort(key=lambda x:x.wp,reverse=True)
    alWest.sort(key=lambda x:x.totalSimWins,reverse=True)   #ALWest
    alCentral=teamList[5:10]
    alCentral.sort(key=lambda x:x.wp,reverse=True)
    alCentral.sort(key=lambda x:x.totalSimWins,reverse=True)
    alEast=teamList[10:15]
    alEast.sort(key=lambda x:x.wp,reverse=True)
    alEast.sort(key=lambda x:x.totalSimWins,reverse=True)
    nlWest=teamList[15:20]
    nlWest.sort(key=lambda x:x.wp,reverse=True)
    nlWest.sort(key=lambda x:x.totalSimWins,reverse=True)
    nlCentral=teamList[20:25]
    nlCentral.sort(key=lambda x:x.wp,reverse=True)
    nlCentral.sort(key=lambda x:x.totalSimWins,reverse=True)
    nlEast=teamList[25:30]
    nlEast.sort(key=lambda x:x.wp,reverse=True)
    nlEast.sort(key=lambda x:x.totalSimWins,reverse=True)
    return alWest+alCentral+alEast+nlWest+nlCentral+nlEast

def pythagExp(games,runs):
    #pythagenport
    #runsPerGame=runs/games
    #return 1.5*math.log10(2*runsPerGame)+.45
    #pythagenpat
    return (runs/games)**.287

def log5(A,B):
    num=A-A*B
    denom=A+B-2*A*B
    return num/denom

def parseHomeAway(pandaRow,teamList):
    homeAway=pandaRow[2]
    homeAbbr=pandaRow[1] if homeAway=="Home" else pandaRow[3]
    awayAbbr=pandaRow[3] if homeAway=="Home" else pandaRow[1]
    homeTeam=findTeam(homeAbbr,teamList)
    awayTeam=findTeam(awayAbbr,teamList)
    return awayTeam,homeTeam

class Division:
    def __init__(self,teamList):
        self.teams=teamList

    def determineWinner(self):
        self.teams.sort(key=lambda x:x.simWinP, reverse=True)
        winner=self.teams[0]
        winner.divTitle=1

    def determineWildCards(self):
        self.teams.sort(key=lambda x:x.simWinP, reverse=True)
        wildCards=self.teams[0:2]
        for team in wildCards:
            team.wildCard=1

    def printStandings(self,title=" "):
        if title != " ":
            print(title)
        self.teams.sort(key=lambda x:x.simWinP,reverse=True)
        self.teams.sort(key=lambda x:x.wildCard,reverse=True)
        self.teams.sort(key=lambda x:x.divTitle,reverse=True)
        for team in self.teams:
            if team.divTitle*team.wildCard==0: preamble="  "
            if team.divTitle==1: preamble="* "
            if team.wildCard==1: preamble="^ "
            print("%s%s%s-%s" % (preamble,team.nickname.ljust(16),team.simWins,team.simLosses))

    def sortDivision(self):
        self.teams.sort(key=lambda x:x.simDivTitles,reverse=True)


class Team:
    def __init__(self,abbr,name,nickname):
        self.abbr=abbr
        self.name=name
        self.nickname=nickname
        self.wins=0
        self.losses=0
        self.rf=0
        self.ra=0
        self.seasonGames=[]
        self.last100Games=[]
        self.lastSeasonGames=[]
        self.futureGames=[]
        self.maxWins=0
        self.maxLosses=0
        self.simDivTitles=0
        self.simWildCard=0
        self.totalSimWins=0
        self.totalSimLosses=0
        self.tieBreaker=rand()/10**6

    def getCurrentYearSchedule(self,year,teamList,leagueFutureGames):
        schedule=teamSched(year,self.abbr)
        pandaList=schedule.values.tolist()
        for i in range(len(pandaList)):
            gameID=i+1
            pandaRow=pandaList[i]
            gameDate=pandaRow[0].split(", ")[1]
            if self.gameDateOk(gameDate)==False:
                continue
            awayTeam,homeTeam=parseHomeAway(pandaRow,teamList)
            gameID=gameDate+awayTeam.abbr+homeTeam.abbr
            opp=pandaRow[3]
            if pandaRow[4] is None:
                futureGame=Game(gameID,awayTeam,homeTeam)
                self.futureGames.append(futureGame)
                if homeTeam==self:
                    leagueFutureGames.append(futureGame)
            else:
                wl=pandaRow[4][0]
                r=int(pandaRow[5])
                ra=int(pandaRow[6])
                self.seasonGames.append((gameID,opp,wl,r,ra))

    #error in brewers page, hacking
    def gameDateOk(self,gameDate):
        gameMonth=gameDate[0:3]
        gameDay=gameDate[4:]
        if gameMonth=='Oct':
            gameDay=int(gameDay)
        if gameMonth=='Oct' and gameDay>3:
            return False
        return True


    def getLastYearsSchedule(self,year):
        schedule=teamSched(year-1,self.abbr)
        pandaList=schedule.values.tolist()
        for i in range(len(pandaList)):
            pandaRow=pandaList[i]
            gameID=i+1
            opp=pandaRow[3]
            if pandaRow[4] is not None:
                wl=pandaRow[4][0]
                r=int(pandaRow[5])
                ra=int(pandaRow[6])
                self.lastSeasonGames.append((gameID,opp,wl,r,ra))

    def printSchedule(self,attr,title):
        print(title)
        theList=getattr(self,attr)
        for game in theList:
            print(game)

    def processPlayedGames(self):
        self.wins=len([x for x in self.seasonGames if x[2]=="W"])
        self.losses=len([x for x in self.seasonGames if x[2]=="L"])
        self.rf=sum([x[3] for x in self.seasonGames])
        self.ra=sum([x[4] for x in self.seasonGames])
        self.gp=self.wins+self.losses
        self.wp=round(self.wins/self.gp,3)


    def printWinLoss(self):
        print(self.name+" "+self.nickname)
        print("%s-%s; %s" % (self.wins,self.losses,self.wp))
        print("RF: %s; RA: %s, Pythag = %s" % (self.rf,self.ra,round(self.pythag,3)))
        eWin=int(round(self.pythag*(self.gp),0))
        eLoss=self.gp-eWin
        print("Expected W-L: %s-%s" % (eWin,eLoss))

    def calcPythag(self,gameBallast,runBallast):
        games=self.gp+gameBallast
        adjRF=self.rf+runBallast/2
        adjRA=self.ra+runBallast/2
        runs=adjRF+adjRA
        exp=pythagExp(games,runs)
        self.pythag=adjRF**exp/(adjRF**exp+adjRA**exp)

    def resetSimStats(self):
        self.simWins=self.wins
        self.simLosses=self.losses
        self.divTitle=0
        self.wildCard=0

    def addSimWin(self,opp):
        self.simWins+=1
        opp.simLosses+=1

    def setSimWinP(self):
        self.simWinP=self.simWins/(self.simWins+self.simLosses)+self.tieBreaker

    def finishSim(self):
        self.maxWins=max(self.maxWins,self.simWins)
        self.maxLosses=max(self.maxLosses,self.simLosses)
        self.simDivTitles+=self.divTitle
        self.simWildCard+=self.wildCard
        self.simPlayoffs=self.simDivTitles+self.simWildCard
        self.totalSimWins+=self.simWins
        self.totalSimLosses+=self.simLosses

    def printSimSummary(self,numSeasons):
        name=self.nickname.ljust(16)
        talent="%.3f" % self.pythag
        talent=str(talent).lstrip("0").ljust(6)
        divTitles=str(round(100*self.simDivTitles/numSeasons,1)).ljust(7)#str(self.simDivTitles).ljust(6)
        wildCards=str(round(100*self.simWildCard/numSeasons,1)).ljust(7)
        avgWins=str(round(self.totalSimWins/numSeasons,1)).ljust(8)
        maxWins=str(self.maxWins).ljust(6)
        minWins=str(162-self.maxLosses).ljust(6)
        playoffTrips=self.simPlayoffs
        wins=str(self.wins).rjust(3)
        losses=str(self.losses).ljust(6)
        wl=wins+"-"+losses
        poPerc=100*playoffTrips/numSeasons
        print("%s|%s%s%s%s|%s%s|%s%.1f" % (name,talent,avgWins,maxWins,minWins,divTitles,wildCards,wl,poPerc))

class Game:
    def __init__(self,gameID,away,home):
        self.gameID=gameID
        self.away=away
        self.home=home

    def simGame(self):
        teamString=("ID: %s\tAway: %s\tHome: %s" % (self.gameID.ljust(12),self.away.abbr,self.home.abbr))
        winProb=log5(self.away.pythag,self.home.pythag)
        num=rand()
        if num<winProb:
            self.away.addSimWin(self.home)
            #print("%s\t%.3f  %.3f  %s" % (teamString,num,winProb,self.away.abbr))
        else:
            self.home.addSimWin(self.away)
            #print("%s\t%.3f  %.3f  %s" % (teamString,num,winProb,self.home.abbr))

def testMain():
    year=2021
    confirm=False
    teamFile="teams.csv"
    teamList=createTeamList(teamFile,confirm)
    #let's do stuff
    team=findTeam("SEA",teamList)
    team.getCurrentYearSchedule(year)
    team.processPlayedGames()
    team.printWinLoss()

if __name__=="__main__":
    start=time.time()
    main()
    seconds=int(time.time()-start)
    print("Program took %d:%d to run" % (seconds//60,seconds%60))

