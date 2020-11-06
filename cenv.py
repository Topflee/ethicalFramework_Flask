#Custom environment file built of the tensorforce environments.
#Needed to automate training and agent creation. Super useful. 

#General library inputs
import os
import logging
import random

#Libraries for AI creation, mainly here for load order
import tensorflow as tf
from tensorforce.agents import Agent
from tensorforce.environments import Environment
from tensorforce.execution import Runner

#The loading the actual simulator system
from Ethical_Sim import Ethical_Sim

class CustomEnvironment(Environment):
    #General constructor, not used, use reset() instead for inputs
    def __init__(self):
        super().__init__() 
    
    #Input layer state of the AI system. Single array of size 24
    def states(self):
        return dict(type='float', shape=(25,))

    #Action outputs of network. Single value, option_0 < 0.5 < option_1
    def actions(self):
        #return {"choice": dict(type="float",num_values=1, min_value=0.0, max_value=1.0)}
        return dict(type="float", min_value=0.0, max_value=1.0)

    # Optional, should only be defined if environment has a natural maximum
    # episode length
    def max_episode_timesteps(self):
        return super().max_episode_timesteps()

    # Optional
    def close(self):
        super().close()

    #Reset used after a game is completed, can be later modified for manual reset.
    def reset(self):
        self.sim = Ethical_Sim(20)
        return self.sim.state()

    #Helper function just to make stuff shorter and clearner
    def getCurrentDilemma(self):
        return self.sim.dilemmasDone[-1]

    #Helper function to make stuff shorter and cleaner
    def getState(self):
        return self.sim.state()

    def getReward(self, theory, action):
        return self.sim.reward(theory, action)

    #Actual tasks done from from state creation to agent action. 
    def execute(self, actions):
        #Only here for future reference, don't need
        terminal = False 

        #choice selection
        if False: #make true to do over 0.5, good for absolute choices
            choice = int(actions > 0.5)
        else: #make False for pseudo random, good for adjusting confidence levels
            if actions > 0.5:
                choice = int(random.uniform(0,1) < actions)
            else:
                choice = int(random.uniform(0,1) < 1 - actions)

        #Make the actual decision, thus creating the new state of the game
        self.sim.makeNextDilemma(self.sim.dilemmasDone[-1]["id"], choice)

        #get the reward based on the action
        reward = self.sim.reward('virtue',choice)

        #return the new state, the terminal (always False), and the reward
        return self.sim.state(), terminal, reward
