from flask import Flask, request, make_response, jsonify, session
import json, csv, random
from flask_cors import CORS
from Ethical_Sim import Ethical_Sim
from tensorforce.agents import Agent
from tensorforce.environments import Environment
import cenv

app = Flask(__name__)
CORS(app)

pidSimDict = {}
pidTheoryDict = {}
pidFlagDict = {}
NUMQUESTIONS = 10 

environment = Environment.create(
    environment='cenv.CustomEnvironment', max_episode_timesteps=100
)

util_agent = Agent.load(directory='./util_agent', format='numpy', environment=environment)

deon_agent = Agent.load(directory='./deon_agent', format='numpy', environment=environment)

virtue_agent = Agent.load(directory='./virtue_agent', format='numpy', environment=environment)

agents = [util_agent, deon_agent, virtue_agent]

#############################33
## Agent Actions          #####
## User_sim = specific user's codnition from dictionary
## User_agent = agents[user_condition - 1]
## actions = User_agent.act(states=User_sim.state(), independent=True, deterministic=True)
##############################

# The site needs to send the pid
# Intializes sim for the particular user
@app.route('/get_dilemma', methods=['GET'])
def getData():
    if request.method == 'GET':
        pid             = request.args.get('pid')
        condition       = request.args.get('condition')

        if not pid:
            responseObject = {
                    'status': 'fail',
                    'message': 'No pid sent.'
                }
            return make_response(jsonify(responseObject)), 401
        
        pidSimDict[pid] = Ethical_Sim(NUMQUESTIONS)
        pidTheoryDict[pid] = int(condition)
        pidFlagDict[pid] = False
        responseObject = {
            'status': 'success',
            'data': pidSimDict[pid].dilemmasDone[-1],
            'ruleset': pidSimDict[pid].get_rules(),
        }
    return make_response(responseObject), 200

@app.route('/post_response', methods=['POST'])
def postResponse():
    if request.method == 'POST':
        entry = []
        try:
            pid = request.args.get('pid')
            #participant id
            entry.append(pid)
            #AI moral theory
            entry.append(pidTheoryDict[pid])
            #question number
            entry.append(request.args.get('qNum'))
            #question id
            entry.append(request.args.get('qid'))
            #slider values
            entry.append(request.args.get('humanSliderPos'))
            entry.append(request.args.get('aggregateSliderPos'))
            entry.append(request.args.get('aiSliderPos'))
            #target values (0 left, 0 right, 1 left, 1 right)
            entry.append(pidSimDict[pid].dilemmasDone[-1]["target_0"])
            entry.append(pidSimDict[pid].dilemmasDone[-1]["target_1"])
        except:
            responseObject = {
                    'status': 'fail',
                    'message': 'Malformed parameters.'
                }
            return make_response(jsonify(responseObject)), 401

        if pidFlagDict[pid]:
            choice = 0 if int(request.args.get('aggregateSliderPos')) <= 0 else 1
            pidSimDict[pid].makeNextDilemma(pidSimDict[pid].dilemmasDone[-1]["id"], choice)
            teammateResponse =  agents[pidTheoryDict[pid] - 1].act(states=pidSimDict[pid].state(), independent=True, deterministic=True)
            responseObject = {
                        'status': 'success',
                        'data': pidSimDict[pid].dilemmasDone[-1]
                    }
        else:
            responseObject = {
                        'status': 'success',
                        'data': 'Data recorded',
                        'ai': teammateResponse

                    }
        pidFlagDict[pid] = not pidFlagDict[pid]
        with open('responses.csv', 'a', newline='\n') as i:
            writer = csv.writer(i)
            writer.writerow(entry)

    
    return make_response(jsonify(responseObject)), 200

@app.route('/')
def hello_world():
	return 'Hello, World!'

if __name__ == "__main__":
    app.run()
