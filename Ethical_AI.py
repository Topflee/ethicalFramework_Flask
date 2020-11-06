#Script responsible for training the AI agents 
#This file does not do any testing but simply trains and saves an agent
#Uses the tensorforce agents and the custom environment design in this repo

#Imported for command line arguments, not used in the current design
import argparse

parser = argparse.ArgumentParser()
#parser.add_argument("--theory", help="select an agent type [ppo, vpg, dqn]")
#args = parser.parse_args()

#These are imported if I need to run stuff on the server 
import os
import logging

#Tenforforce imputs
from tensorforce.agents import Agent
from tensorforce.environments import Environment
from tensorforce.execution import Runner
from tensorforce import Runner

#Custome file inputs
import cenv
from Ethical_Sim import Ethical_Sim


# Create an OpenAI-Gym environment
environment = Environment.create(
    environment='cenv.CustomEnvironment', max_episode_timesteps=100
)

# Create a PPO agent
agent = Agent.create(
    agent='ppo',
    environment=environment,
    # Automatically configured network
    network='auto',
    # PPO optimization parameters
    batch_size=20, update_frequency=5, learning_rate=3e-4, multi_step=10,
    subsampling_fraction=0.33,
    # Exploration
    exploration=0.1, variable_noise=0.0,
    # Default additional config values
    config=None,
    parallel_interactions=1,
)

# Initialize the runner
runner = Runner(agent=agent, environment=environment)

# Start the runner
runner.run(num_episodes=100000)
runner.close()

#save the agent in the working directory
agent.save(directory='.', format='numpy', append='episodes')

