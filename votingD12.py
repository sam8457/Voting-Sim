#!/usr/bin/env python3
import random, math, scipy.stats, numpy as np, matplotlib.pyplot as plt
from datetime import datetime

# TODO: add DONORMALS varriable
#       add ability to manually place cans
#       add caucusses 

# main parameters, affects performance most heavily
NUMVOTERS = 1000
NUMCANS = 5
TESTTIMES = 100

# If true, determines 2D distance between voter/can, else adds differences
DOSTRAIGHTLINE = True

# size of grid, changing usuall doesn't do anything
X = 10
Y = 10

# limits are the number of candidates that can be ranked
IRVLIMIT = 29
BORDALIMIT = 29

# distances are how far away votes/approvals/points will be given
CONSIDERDIST = 14
# multipliers to modify CONSIDERDIST for each voting style
PLURALITYMULT = 2
RANKMULT = 2 # affects both BORDA and IRV
APPROVALMULT = 1.3 # optimal tends to be 1.3 * X or Y
SCOREMULT = 2

# affects the standard normal distributioin
NUMPEAKS = 2 # zero means use completely random, will override NUMCANS if larger
STANDARDDEV = 20 # 3, 7, maybe higher
RANDOMREMAINING = True
MANUALPEAKS = [] # zero means peaks will be generated randomly, overrides NUMPEAKS
# Example: MANUALPEAKS = [(-5,-5), (0,0), (5,5)], MANUALPEAKS = []

PARAMLIST = [NUMVOTERS, NUMCANS, X, Y, DOSTRAIGHTLINE,
             IRVLIMIT, BORDALIMIT,
             CONSIDERDIST, RANKMULT, APPROVALMULT, SCOREMULT,
             NUMPEAKS, STANDARDDEV, RANDOMREMAINING, MANUALPEAKS]

# which part of the displays to include
DOEXAMPLE = False
DOTESTS = True
DOGRAPHING = True

# scatterplot customization
VOTERALPHA = 0.1

# plots voters and candidates on a scatterplot, distinguished by color
def showScatter(voters, cans, best, voterAlpha):

    plt.figure(figsize=(5,7))
    plt.subplot(2,1,1) # will place scatterplot at top
    
    plt.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    plt.title('Voter Distribution')

    # voters
    x = np.array([voter[0] for voter in voters]) # get x list with 'voter[] for voter in voters' loop, convert to numpy array
    y = np.array([voter[1] for voter in voters]) # get y list

    plt.scatter(x, y, c='grey', alpha=voterAlpha, s=50, label='Voters') # add points to graph
    plt.show(block=False) # draw graph, block=false --> dont pause rest of program after graphing

    # ideal candidate
    x = np.array(cans[best][0])
    y = np.array(cans[best][1])

    plt.scatter(x, y, c='#3300cc', s=200, label='Ideal Can')
    plt.show(block=False)

    plt.legend()

    # candidates
    x = np.array([can[0] for can in cans])
    y = np.array([can[1] for can in cans])

    colors = ['#ff3333','#ffcc66','#88c999','#6666ff','#9900ff']
    altColors = ['#F8CECC','#FFE6CC','#CCFFCC','#DAE8FC','#E1D5E7']
    altColorsOutline = ['#B85450','#D79B00','#009900','#6C8EBF','#9673A6']

    plt.scatter(x, y, c=altColors, edgecolors=altColorsOutline,
                s=100, label='Candidates')
    
    plt.show(block=False)

# plots each voting method on a bar graph
def showBars(stats, allSats):

    # candidates and colors are the same for all graphs
    x = np.array([1,2,3,4,5])
    
    colors = ['#ff3333','#ffcc66','#88c999','#6666ff','#9900ff']
    altColors = ['#F8CECC','#FFE6CC','#CCFFCC','#DAE8FC','#E1D5E7']
    altColorsOutline = ['#B85450','#D79B00','#009900','#6C8EBF','#9673A6']

    # convert voter satisfaction to positive
    allSatsAvg = sum(allSats)/len(allSats)
    voterSats = [(sat + (allSatsAvg*-2)) for sat in allSats] # adds the negative doubled average of sats to each sat

    # will be looping through these to make each graph
    titles = ['Plurality', 'Instant Runoff', 'Borda Count',
              'Approval', 'Score', 'Voter Satisfaction']
    statsPlusVS = stats
    statsPlusVS.append(voterSats)

    # each loop makes a graph for a specific voting method
    for t in range(len(titles)):

        # pick appropriate data, name, and location for the graph
        y = np.array(statsPlusVS[t]) # data
        plt.subplot(4, 3, t + 7) # location, 7 is the offset to get it to work right
        plt.title(titles[t]) # name

        # plot bars and color according to candidates
        barlist=plt.bar(x,y)
        for i in range(NUMCANS):
            barlist[i].set_color(altColors[i])
            barlist[i].set_edgecolor(altColorsOutline[i])

        # remove ticks and numbers on sides and bottom
        plt.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    
    plt.show(block=False)

# randomly generate people with no clustering
def makePeopleRandom(x, y, numpeople):
    
    people = []
    for i in range(numpeople):
        people.append(
            [random.randint(-x*100, x*100) /100,
             random.randint(-y*100, y*100) /100]) # gives two decimals
        
    return people

# randomly generate people with clustering
def makePeopleNormal(x, y, numpeople, numPeaks, standardDev):

    # generate locations of clusters randomly
    peakLocations = []
    if len(MANUALPEAKS) == 0:
        for p in range(numPeaks):
            peakLocations.append((random.randint(-x*100, x*100) /100,
                                 random.randint(-y*100, y*100) /100))
    else:
        peakLocations = MANUALPEAKS

    # generate voters
    voters = []
    for p in range(numpeople):

        # select which peak to use at random
        peakIndex = random.randint(0, len(peakLocations)-1) # one less to avoid index error
        peak = peakLocations[peakIndex]

        # use bell curve to generate person's location
        voters.append([round(np.random.normal(peak[0], standardDev),2), # x
                       round(np.random.normal(peak[1], standardDev),2)]) # y

    # generate candidates
    cans = []
    for c in range(numPeaks):

        # one candidate per peak
        peak = peakLocations[c]
        cans.append([round(np.random.normal(peak[0], standardDev),2),
                     round(np.random.normal(peak[1], standardDev),2)])

    # randomly generate remaining candidates beyond peaks
    remainCans = (NUMCANS - len(cans))
    if remainCans > 0:
        for i in range(remainCans):

            # make candidates outside peaks
            if RANDOMREMAINING == True:
                cans.append([random.randint(-x*100, x*100) /100,
                             random.randint(-y*100, y*100) /100])

            # make candidates from peaks
            else:
                peak = peakLocations[random.randint(0, len(peakLocations)-1)] # pick a random peak
                cans.append([np.random.normal(peak[0], standardDev),
                             np.random.normal(peak[1], standardDev)])

    return voters, cans

# Calculates the 2D distance between points where points are sent as lists of two values. Used basically everywhere.    
def distanceList(A, B):
    
    X1 = A[0]
    X2 = B[0]
    Y1 = A[1]
    Y2 = B[1]
    
    if DOSTRAIGHTLINE == True:
        dist = math.sqrt( (X1 - X2)**2 + (Y1 - Y2)**2)
    else:
        dist = abs((X1 - X2) + (Y1 - Y2))
        
    return dist

# Determines how satisfied each voter is with a particular candidate, and averages them together to get total voter satisfaction. Greater distance means less satisfaction. Used in Score.
def voterSat(can, voters):
    distTotal = 0
    for v in voters:
        dist = distanceList(v, can)
        distTotal += (- dist)
    distAvg = distTotal / len(voters)
    return round(distAvg, 2)

# Ranks candidates based on distance, furthest is lowest ranked. Used in IRV and Borda Count.   
def rankCans(voters, cans):

    # list of lists, each sublist is a single voters' ranks
    rankings = [[] * (len(cans))] * len(voters)
    distances = {}

    # loop through all voters
    for v in range(len(voters)):
        # loop through all candidates
        for c in range(len(cans)):

            # add distance to that candidate for that voter
            distances[c] = distanceList(voters[v], cans[c])

        # rank each voter's set of candidates by distance    
        rankings[v] = (sorted(distances.items(), key=lambda item: item[1]))

        # removes rankings if they're outside CONSIDERDIST * RANKMULT
        rankings[v] = [c for c in rankings[v] if c[1] <= round(CONSIDERDIST * RANKMULT)]
        # the first "c" in the [] is the item that will be added if the condition is true
        # "for c in rankings[v]" is a for loop, as long as rankings[v]
        # "if c[1] >= round(CONSIDERDIST * RANKMULT)" is the condition that has to be true for c to be added

    # rankings is a list of lists of tuples. Each sublist represents
    # a single voter's opinions on all the candidates, whith each tuple
    # containing the name of the candidate and the distance from the voter,
    # in that order.
    return rankings

# Makes new voters and candidates, returns them and the best candidate. 
def newSet():

    # if randomly generated people
    if NUMPEAKS == 0:
        cans = makePeopleRandom(X, Y, NUMCANS)
        voters = makePeopleRandom(X, Y, NUMVOTERS)

    # if clustered people
    else:
        voters, cans = makePeopleNormal(X, Y, NUMVOTERS, NUMPEAKS, STANDARDDEV)

    # find best candidate
    allSats = []
    for i in range(len(cans)):
        allSats.append(voterSat(cans[i], voters))
    best = allSats.index(max(allSats))
    
    return voters, cans, best, allSats

# prints all program parameters that can be tweaked for easy reference
def printParams():
    """ Parameters:
            [NUMVOTERS, NUMCANS, X, Y,
             IRVLIMIT, BORDALIMIT,
             CONSIDERDIST, RANKMULT, APPROVALMULT, SCOREMULT,
             NUMPEAKS, STANDARDDEV, RANDOMREMAINING, MANUALPICS]
    """
    paramNames = ['#V','#C','X','Y', 'STR8',
                  'IR-L','BO-L',
                  'CON-D','R-MUL','A-MUL','S-MUL',
                  '#PKs','SD','RR','MP']
    for p in range(len(PARAMLIST)):
        print(paramNames[p] + ':', end='')
        print(str(PARAMLIST[p]) + ', ', end='')
    print('')

# Calculates the straightline distance on a 2D plane between a voter and all candidates,
# then adds a vote to the nearest candidate.     
def doPlurality(voters, cans):

    # list to store votes for each candidate
    votes = [0] * len(cans)

    # loop through the voters
    for v in voters:

        # give vote to candidate that is the closest
        dists = [0] * len(cans)
        for c in range(len(cans)):
            dists[c] = distanceList(v, cans[c])
        voteTo = dists.index(min(dists))

        # only give votes to candidates that are close enough
        if min(dists) <= round(CONSIDERDIST * PLURALITYMULT):
            votes[voteTo] += 1
            
    winner = votes.index(max(votes))
    return(winner, votes)

# Calculates distances to candidates, orders them in terms of closest to farthest.
# Voting takes place in multiple rounds, where everyone's first choice is used on the
# first round. The lowest scoring candidate is eliminated. During the next round, the
# everyone who had their first choice eliminated has their vote transferred to the
# second round. This goes on until only one candidate remains, who is the winner.
def doIRV(voters, cans):

    # get candidate ranks for all voters    
    rankings = rankCans(voters, cans)

    lossOrder = [] # will keep track of overall ranks
    
    # a dict with all remaining candidates
    remainCans = {}
    for c in range(len(cans)):
        remainCans[c] = 0 # candidate names are just numbers
        
    # loop for each round of voting
    for r in range(len(cans)): # do as many rounds as there are candidates

        if r < IRVLIMIT: # only use opinions less than IRVLIMIT, functionally identical to only ranking IRVLIMIT candidates
            
            remainCans = remainCans.fromkeys(remainCans, 0) # zero out votes

            #count votes for this round
            for voterOpinions in rankings:
                for candidate in voterOpinions:
                    if candidate[0] in remainCans: # [0] is the candidate's name
                        remainCans[candidate[0]] += 1
                        break

        # drop loser for this round
        roundLoser = min(remainCans,key=remainCans.get)
        del remainCans[roundLoser]
            
        lossOrder.append(roundLoser)

    winner = roundLoser # last round loser is the winner

    #overallRanks = [x for x in lossOrder[::-1]] # reverse lossOrder for overallRanks

    # overallRanks has rounds as indexes and candidate numbers as elements,
    # this block of code reverses that: the candidate numbers become the
    # indexes of roundEliminated and the elements are the round
    roundEliminated = [0] * len(cans)
    for r in range(len(roundEliminated)):
        roundEliminated[lossOrder[r]] = r + 1 # +1 to make human readable
    
    return winner, roundEliminated


# Ranks candidates in order of favorite to least. Gives maximum points to favorite,
# maximum - 1 to second favorite, etc. until 1 after which no points are given.
def doBorda(voters, cans):

    rankings = rankCans(voters, cans) # get candidate ranks for all voters
    
    points = [0] * len(cans) # contains point totals

    # add points according to how close voters are
    for voter in range(len(rankings)):
        for rank in range(len(rankings[voter])):
            choice = rankings[voter][rank][0]
            if rank < BORDALIMIT:
                points[choice] += (BORDALIMIT - rank) # each rank gets 1 fewer points than the last
                
    winner = points.index(max(points))
    return(winner, points)

# Voters vote for multiple candidates. They approve of a candidate if they're CONSIDERDIST
# or less away. Candidate with most approvals wins.
def doApproval(voters, cans):
    votes = [0] * len(cans)
    for v in voters:
        for c in range(len(cans)):
            dist = distanceList(v, cans[c])
            if dist <= round(CONSIDERDIST * APPROVALMULT):
                votes[c] += 1
    winner = votes.index(max(votes))
    return(winner, votes)

# Voters score each candidate from 0 to 10 based on distance. Scores are
# added to each candidate's total, and the winner is whoever has most points.    
def doScore(voters, cans):
    scores = [0] * len(cans)
    for v in voters:
        for c in range(len(cans)):
            dist = distanceList(v, cans[c])
            score = (round(CONSIDERDIST * SCOREMULT) - math.floor(dist))
            if score > 0:
                scores[c] += score
    winner = scores.index(max(scores))
    return(winner, scores)
    
# Run one of each, show outcomes.
def runExample():

    # get a new set of voters
    voters, cans, best, allSats = newSet()

    # header
    print('Example Info:')
    print('Candidate Positions:', end=''), print(cans)
    print("Voter Satisfaction:", end='')
    for i in range(len(cans)):
        print(voterSat(cans[i], voters), end='')
        print(', ', end='')
    print('')
    print('')

    # items to loop through
    names = ['Plurality', 'Instant Runoff', 'Borda Count',
             'Approval', 'Score']
    functionList = [doPlurality, doIRV, doBorda, doApproval, doScore]
    statsNames = ['Vote Totals', 'Round Eliminated', 'Point Totals',
                  'Vote Totals', 'Point Totals']

    stats = [] # needed for bar charts
    
    # loop through each voting funciton and print their stats
    for f in range(len(functionList)):
        print(names[f] + ' Results:')
        winner, stat = functionList[f](voters, cans)
        print("Winner is candidate " + str(winner + 1))
        print(statsNames[f]+':', end=''), print(stat)
        print('')
        
        stats.append(stat) # needed for bar charts

    # formatting
    print('_' * 45)

    if DOGRAPHING == True:
        showScatter(voters, cans, best, VOTERALPHA)
        showBars(stats, allSats)
        plt.show(block=False)

# Run multiple of each, show how many times it gets the best choice.
def testAll(times):

    # keep track of how long it takes
    start = datetime.now()
    
    print("Test Parameters:")
    printParams()
    print('')
    
    print('Out of ' + str(times) + ' tests...')

    # lists that will be used in the loop
    names = ['Plurality', 'IRV', 'Borda', 'Approval', 'Score']
    functionList = [doPlurality, doIRV, doBorda, doApproval, doScore]
    correct = [0] * len(names)
    ties = [0] * len(names)

    # do each function multiple times
    for t in range(times):

        # make a new set of voters and candidates
        voters, cans, best, allSats = newSet()

        # loop through each voting funciton
        for f in range(len(functionList)):
            winner, stats = functionList[f](voters, cans) # each function from functionList
            if winner == best:
                correct[f] += 1 # add correct instances
            if len(stats) != len(set(stats)):
                ties[f] += 1

    # print to screen
    for i in range(len(names)):
        print(names[i]+' got '+str(correct[i])+
        ' right with '+str(ties[i])+' ties.')

    print("Competed in "+str(datetime.now() - start))

    # graph their performance
    if DOGRAPHING == True:

        plt.title('Voting System Performance')
        names = ["PLU","IRV","BOR","APP","SCO"]
        x = np.array(names)
        colors = ['#ff3333','#ffcc66','#88c999','#6666ff','#9900ff']
        altColors = ['#F8CECC','#FFE6CC','#CCFFCC','#DAE8FC','#E1D5E7']
        altColorsOutline = ['#B85450','#D79B00','#009900','#6C8EBF','#9673A6']

        y = np.array(correct) # data

        plt.ylim(0, TESTTIMES)
        
        # plot bars and color according to voting methods
        barlist=plt.bar(x,y)
        for i in range(len(names)):
            barlist[i].set_color(altColors[i])
            barlist[i].set_edgecolor(altColorsOutline[i])
    
        plt.show(block=False)
    
if __name__ == "__main__":
    if DOEXAMPLE == True:
        runExample()
        
    print('')

    if DOTESTS == True:
        testAll(TESTTIMES)
