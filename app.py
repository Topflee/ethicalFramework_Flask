from flask import Flask, request, make_response, jsonify, session
import json, csv, random
from flask_cors import CORS
from Ethical_Sim import Ethical_Sim
app = Flask(__name__)
CORS(app)

pidSimDict = {}
pidTheoryDict = {}
pidFlagDict = {}
theories = ["deontology", "consequentialism", "virtue ethics"]
NUMQUESTIONS = 10 


# The site needs to send the pid
# Intializes sim for the particular user
@app.route('/get_dilemma', methods=['GET'])
def getData():
    if request.method == 'GET':
        pid             = request.args.get('pid')

        if not pid:
            responseObject = {
                    'status': 'fail',
                    'message': 'No pid sent.'
                }
            return make_response(jsonify(responseObject)), 401
        
        pidSimDict[pid] = Ethical_Sim(NUMQUESTIONS)
        random.seed()
        pidTheoryDict[pid] = theories[random.randint(0, 2)]
        pidFlagDict[pid] = False
    return make_response(jsonify(pidSimDict[pid].dilemmasDone[-1])), 200

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
            print(pidSimDict[pid].dilemmasDone)
            entry.append(pidSimDict[pid].dilemmasDone[-1]["target_0"][0])
            entry.append(pidSimDict[pid].dilemmasDone[-1]["target_0"][1])
            entry.append(pidSimDict[pid].dilemmasDone[-1]["target_1"][0])
            entry.append(pidSimDict[pid].dilemmasDone[-1]["target_1"][1])
        except:
            responseObject = {
                    'status': 'fail',
                    'message': 'Malformed parameters.'
                }
            return make_response(jsonify(responseObject)), 401
        if pidFlagDict[pid]:
            choice = 0 if int(request.args.get('aggregateSliderPos')) <= 0 else 1
            print("\n", choice, "\n")
            pidSimDict[pid].makeNextDilemma(pidSimDict[pid].dilemmasDone[-1]["id"], choice)
            responseObject = {
                        'status': 'success',
                        'data': pidSimDict[pid].dilemmasDone[-1]
                    }
        else:
            responseObject = {
                        'status': 'success',
                        'data': 'Data recorded'
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