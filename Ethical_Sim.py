#Simulation file for actual task running and loading.
#Currently used for AI training but can easily be used for the user system. 

#General inputs, don't need anything special
import random
import json
import sys
import numpy as np
import copy

class Ethical_Sim:
    #Gifts and the "values" associated with those gifts, mostly concerned with orderly.
    gifts = ["A Hat", "A Board Game", "A Sweater", "A Bike", "A Computer"]
    gift_values = [0.2, 0.4, 0.6, 0.8, 1]

    #General count of dilemmas, probably should move
    DILEMMA_COUNT = 7

    #I edit this, but I don't think it's ever used 
    QUESTION_COUNT = None #Number of questions we want to ask

    #Modifiers for different possible values
    modifierTypes = ("P_Number", "T_Number", "H_Percent", "M_Percent", "L_Percent", "Result", "Gift")
    
    #relationship types, values are more concerned with order rather than true value
    relations = ("Family Member(s)", "Friend(s)", "Stranger(s)")
    relation_values = [1,0.5,0]

    #General results of complication to imply severity values
    results = ["Dead", "In Pain"]
    results_values = [1,0.5]

    def __init__(self, questionCount):
        #Get teh dilemma stuff from the json file
        json_array = json.load(open("Dilemna.json"))
        self.QUESTION_COUNT = questionCount
        #Load list of dilemmas into memory
        self.dilemmas = []
        self.dilemmasDone = []
        self.flipIndex = []
        for item in json_array:
            self.flipIndex.append(random.randint(0,1))
            #Multi-Target Size 38
            #item['target_0'] = [random.randint(0,self.DILEMMA_COUNT-1),random.randint(0,self.DILEMMA_COUNT-1)]
            #item['target_1'] = [random.randint(0,self.DILEMMA_COUNT-1),random.randint(0,self.DILEMMA_COUNT-1)]
            possible_targets = [0,1,2,3,4,5,6]
            possible_targets.remove(int(item['id']))
            #Single Targets, Size 24
            item['target_0'] = [random.choice(possible_targets)]
            item['target_1'] = [random.choice(possible_targets)]
            if self.flipIndex[-1]:
                swap = item['Option_1']
                item['Option_1'] = item['Option_0']
                item['Option_0'] = swap
                
                swap = item['util_values_1'].copy()
                item['util_values_1'] = item['util_values_0'].copy()                
                item['util_values_0'] = swap.copy()

                swap = item['deon_values_1'].copy()
                item['deon_values_1'] = item['deon_values_0'].copy()
                item['deon_values_0'] = swap.copy()

                swap = item['deon_mods_1'].copy()
                item['deon_mods_1'] = item['deon_mods_0'].copy()
                item['deon_mods_0'] = swap.copy()

                swap = item['virtue_values_1'].copy()
                item['virtue_values_1'] = item['virtue_values_0'].copy()
                item['virtue_values_0'] = swap.copy()
    
                swap = item['virtue_mods_1'].copy()
                item['virtue_mods_1'] = item['virtue_mods_0'].copy()
                item['virtue_mods_0'] = swap.copy()

            self.dilemmas.append(item)

        #Generate initial node randomly
        self.makeNextDilemma(random.randint(0,len(self.dilemmas)-1), random.randint(0,1))
        

    #Make a decision on the current dilemma and pick the next one, this needs 
    #to be separate form the sending of a dilemma due to the first node being 
    #randomly generated
    def makeNextDilemma(self, currentDilemma, decision):
        nextDilemma = random.choice(self.dilemmas[currentDilemma]["target_"+str(decision)])
        node = copy.deepcopy(self.dilemmas[nextDilemma])
        
        for ind, mod in enumerate(node["Modifier_Types"]):
            if mod == self.modifierTypes[0]: #People
                node["Modifiers"].append(random.randint(0, 10))
            elif mod == self.modifierTypes[1]: #Time (Days)
                node["Modifiers"].append(random.randint(1, 10))
            elif mod == self.modifierTypes[2]: #High Percent
                node["Modifiers"].append(random.randint(66,101)/100.0)
            elif mod == self.modifierTypes[3]: #Medium Percent
                node["Modifiers"].append(random.randint(33,66)/100.0)
            elif mod == self.modifierTypes[4]: #Low Percent
                node["Modifiers"].append(random.randint(0,33)/100.0)
            elif mod == self.modifierTypes[5]: #results
                node["Modifiers"].append(random.choice(self.results))
            elif mod == self.modifierTypes[6]: #Gift
                node["Modifiers"].append(random.choice(self.gifts))
            if mod == self.modifierTypes[2] or mod == self.modifierTypes[3] or mod == self.modifierTypes[4]:
                sub = int(node["Modifiers"][-1] + 100)
            else:
                sub = str(node["Modifiers"][-1])
            node["Description"] = node["Description"].replace("[M"+str(ind)+"]", str(node["Modifiers"][-1]))
        
        #Generate the relationships in values 
        for relation in range(0, node["Relation_Count"]):
            node["Relationships"].append(random.choice(self.relations))
            node["Description"] = node["Description"].replace("[relation_"+str(relation)+"]", node["Relationships"][-1])

        self.dilemmasDone.append(node)
        

    #return the current dilemma the player is doing, which should be the last one
    def getCurrentDilemma(self):
        return self.dilemmasDone[-1]

    #Utilitarian reward, based on creating the most good, this is going to 
    #look at helping the most people.  Life or death is valued at a 1, pain is 
    #valued at a 0.5, the reward is calculated for how much good is made vs. 
    #how much total good is available
    def utilitarianReward(self, dilemma, decision):
        numer_1 = 0
        numer_2 = 0
        base = []
        mul = []
        #Calculated the numerical values for decision 0
        for value in dilemma['util_values_0']:
            #General Modifier
            if value[0] == "M":
                temp = int(value[1:])
                temp_type = dilemma['Modifier_Types'][temp]
                
                #Sub in gift value
                if temp_type == "Gift":
                    gift = dilemma['Modifiers'][temp]
                    gift = self.gifts.index(gift)
                    base.append(self.gift_values[gift])

                #Sub in Result values, (dead or in pain)
                elif temp_type == "Result":
                    res = dilemma['Modifiers'][temp]
                    res = self.results.index(res)
                    base.append(self.results_values[res])

                #These are generally the people, count, or percent values
                else:
                    base.append(dilemma['Modifiers'][int(value[1:])])
                mul.append(1)

            #Scaler Modifier
            elif value[0] == "X":
                if len(value[1:]) > 0:
                    mul[-1] = float(value[1:])
                else:
                    mul[-1] = dilemma['Modifiers'][int(value[1:])]
            #Raw input values, not variable
            else:
                base.append(float(value))
                mul.append(1)
        
        #Calculate the actual numerator including the scaler values used.
        for i in range(len(base)):  
            numer_1 += base[i] * mul[i]
        base = []
        mul = []

        #Same comments as above, but for decision 1
        for value in dilemma['util_values_1']:
            if value[0] == "M":
                temp = int(value[1:])
                temp_type = dilemma['Modifier_Types'][temp]
                if temp_type == "Gift":
                    gift = dilemma['Modifiers'][temp]
                    gift = self.gifts.index(gift)
                    base.append(self.gift_values[gift])
                elif temp_type == "Result":
                    res = dilemma['Modifiers'][temp]
                    res = self.results.index(res)
                    base.append(self.results_values[res])
                else:
                    base.append(dilemma['Modifiers'][int(value[1:])])
                mul.append(1)
            elif value[0] == "X":
                if len(value[1:]) > 1:
                    mul[-1] = float(value[1:])
                else: 
                    mul[-1] = dilemma['Modifiers'][int(value[1:])]
            else:
                base.append(float(value))
                mul.append(1)
        for i in range(len(base)):
            numer_2 += base[i] * mul[i]

        #In the rare case you get two zeros, give it a 0
        if numer_1 == 0 and numer_2 == 0:
            return 0

        #Calculate the actual reward, we do division for scaling, may want to change this.
        if not decision: #decision 0
            return numer_1 / (numer_1 + numer_2)
        #    if numer_1 >= numer_2:
        #        return numer_1 / (numer_1 + numer_2)
        #    else:
        #        return numer_1 / (numer_1 + numer_2) 
        #    return int(numer_1 > numer_2) 
        else: #decision 1
            return numer_2 / (numer_1 + numer_2)
        #    if numer_2 >= numer_1:
        #        return numer_1 / (numer_1 + numer_2)
        #    else:
        #        return numer_2 / (numer_1 + numer_2) 
        #    return int(numer_2 > numer_1)

    #The deontology reward is based on a strict act based deontology where 
    #hard rules are set and not broken. These are scored with 0 for break
    #and 1 for keep, these rules are:
    #Do not Deliberately Kill
    #Do not Deliberately Harm Others
    #Do not Deliberately Harm Yourself
    #Do not Steal
    #Do not Lie 
    #Act the way that is the maxum you can will as a universal 
    def deontologyReward(self, dilemma, decision):
        numer_1 = 0
        numer_2 = 0
        num_1_count = 0
        num_2_count = 0

        #Subbing in deon pass or fails for decision 0
        for value in dilemma['deon_values_0']:
            if value != -1:
                numer_1 += float(value)
                num_1_count += 1

        #Subbing in deon pass or fails for decision 1
        for value in dilemma['deon_values_1']:
            if value != -1:
                numer_2 += float(value)
                num_2_count += 1

        #Calculate, may want to scale over binary decision
        if not decision:
            return numer_1 / num_1_count
        #    return int(numer_1 > numer_2)
        else:
            return numer_2 / num_2_count
        #    return int(numer_2 > numer_1)


    #Virtues ethics are based on common virtues that are seen in humans.  While 
    #this study does not focus on every virtue, this is designed to act as a 
    #representative base for what virtue ethics would look like.  Relavent Virtues 
    #scored with 0 for ignore or 1 for prioritize include:
    #Liberality - The virtue of charity
    #Friendliness - Be friendly to other
    #Loyalty - emphasise family and friends 
    #Courage - Aware of danger, but act
    #Truthfulness - virtue of honesty
    def virtueEthicsReward(self, dilemma, decision):
        numer_1 = 0
        numer_2 = 0
        count = 0
        num_1_count = 0
        num_2_count = 0

        #Sub in the variable values for virtues, mainly relationships
        for value in dilemma['virtue_values_0']:
            if value == -1:
                continue
            if value == 2:
                relation = dilemma['virtue_mods_0'][count]
                relation = int(relation[-1])
                relation = dilemma['Relationships'][relation]
                relation = self.relations.index(relation)
                relation = self.relation_values[relation]
                numer_1 += relation
                num_1_count += 1
                count += 1
            else:
                numer_1 += float(value)
                num_1_count += 1
        count = 0
        for value in dilemma['virtue_values_1']:
            if value == -1:
                continue
            if value == 2:
                relation = dilemma['virtue_mods_1'][count]
                relation = int(relation[-1])
                relation = dilemma['Relationships'][relation]
                relation = self.relations.index(relation)
                relation = self.relation_values[relation]
                numer_2 += relation
                num_2_count += 1
                count += 1
            else:
                numer_2 += float(value)
                num_2_count += 1
        if not decision:
            return numer_1 / num_1_count
        #    return int(numer_1 > numer_2)
        else:
            return numer_2 / num_1_count
        #    return int(numer_2 > numer_1)

    #General reward choice function, here to make other code cleaner
    def reward(self, theory, choice):
        if theory == "util":
            return self.utilitarianReward(self.dilemmasDone[-1], choice)
        elif theory == "deon":
            return self.deontologyReward(self.dilemmasDone[-1], choice)
        else:
            return self.virtueEthicsReward(self.dilemmasDone[-1], choice)

    #return the rules array for the input layer
    def get_rules(self):
        ret = []
        for dilemma in self.dilemmas:
            ret.append([dilemma['target_0'][0],dilemma['target_1'][0]])
            #ret.append(dilemma['target_1'])
        return ret
    
    #return the state for the input layer of the AI
    def state(self):
        ret = []
        ret.append(self.dilemmasDone[-1]["id"]) # add ID,1
        ret.append(self.flipIndex[int(self.dilemmasDone[-1]["id"])])
        #drop in modifiers
        modifiers = [-1] * 6 # blank, read in next modifiers,6
        for ind,modifier in enumerate(self.dilemmasDone[-1]["Modifiers"]):
            if modifier in self.gifts:
                value = self.gifts.index(modifier)
                value = self.gift_values[value]
                modifiers[ind] = value
            elif modifier in self.results:
                value = self.results.index(modifier)
                value = self.results_values[value]
                modifiers[ind] = value
            else:
                value = float(modifier)
                modifiers[ind] = value
        ret.append(modifiers)    

        #drop in relationships values
        relationships = [-1] * 3 #blank, read in relation values,3 
        for ind, rel in enumerate(self.dilemmasDone[-1]["Relationships"]):
            value = self.relations.index(rel)
            value = self.relation_values[value]
            relationships[ind] = value
        ret.append(relationships)
        ret.append([item for sublist in self.get_rules() for item in sublist]) # add ruleset, 24
        ret_flat = []

        #compress to a flat array for input
        for row in ret:
            if isinstance(row, list):
                for item in row:
                    ret_flat.append(float(item))
            else:
                ret_flat.append(float(row))
        return ret_flat
    
