import torch
from bindsnet.environment       import *
from bindsnet.encoding          import *
from bindsnet.pipeline.action   import *
from bindsnet.datasets          import MNIST
from bindsnet.network           import Network
from bindsnet.pipeline          import Pipeline
from bindsnet.learning          import m_stdp_et
from bindsnet.network.topology  import Connection
from bindsnet.network.nodes     import Input, LIFNodes
from bindsnet.models            import DiehlAndCook2015


class TestPipeline:
	
	def test_MNIST_pipeline(self):
		network = DiehlAndCook2015(n_inpt=784,
						           n_neurons=400,
						           exc=22.5,
						           inh=17.5,
						           dt=1.0,
						           norm=78.4)
		
		environment = DatasetEnvironment(dataset=MNIST(path='../../data/MNIST', download=True),
										 train=True,
										 intensity=0.25)
		
		p = Pipeline(network=network,
					 environment=environment,
					 encoding=poisson,
					 time=350)
		
		assert p.network == network
		assert p.env == environment
		assert p.encoding == poisson
		assert p.time == 350
		assert p.history_length is None
		
		def test_Gym_pipeline(self):
			# Build network.
			network = Network(dt=1.0)
			
			# Layers of neurons.
			inpt = Input(n=6552, traces=True)
			middle = LIFNodes(n=225, traces=True, thresh=-52.0 + torch.randn(225))
			out = LIFNodes(n=60, refrac=0, traces=True, thresh=-40.0)
			
			# Connections between layers.
			inpt_middle = Connection(source=inpt, target=middle, wmax=1e-2)
			middle_out = Connection(source=middle, target=out, wmax=0.5,
								    update_rule=m_stdp_et, nu=2e-2,
								    norm=0.15 * middle.n)
			
			# Add all layers and connections to the network.
			network.add_layer(inpt, name='X')
			network.add_layer(middle, name='Y')
			network.add_layer(out, name='Z')
			network.add_connection(inpt_middle, source='X', target='Y')
			network.add_connection(middle_out, source='Y', target='Z')
			
			# Load SpaceInvaders environment.
			environment = GymEnvironment('SpaceInvaders-v0')
			environment.reset()
			
			# Build pipeline from specified components.
			for history_length in [3, 4, 5, 6]:
				for delta in [2, 3, 4]:
					p = Pipeline(network, environment, encoding=bernoulli,
								 feedback=select_multinomial, output='Z',
								 time=1, history_length=2, delta=4)
					
					assert p.feedback == select_multinomial
					assert p.history_length == history_length
					assert p.delta == delta
					
			
			# Checking assertion errors
			for time in [0, -1]:
				try:
					p = Pipeline(network, environment, encoding=bernoulli,
								 feedback=select_multinomial, output='Z',
								 time=time, history_length=2, delta=4)
				except Exception as es:
					assert es == AssertionError
					
			for delta in [0, -1]:
				try:
					p = Pipeline(network, environment, encoding=bernoulli,
								 feedback=select_multinomial, output='Z',
								 time=time, history_length=2, delta=delta)
				except Exception as es:
					assert es == AssertionError
			
			for output in ['K']:
				try:
					p = Pipeline(network, environment, encoding=bernoulli,
								 feedback=select_multinomial, output=output,
								 time=time, history_length=2, delta=4)
				except Exception as es:
					assert es == AssertionError
	
			p = Pipeline(network, environment, encoding=bernoulli,
								 feedback=select_random, output='Z',
								 time=1, history_length=2, delta=4,
								 save_interval=50, render_interval=5)
	
			assert p.feedback == select_random
			assert p.encoding == bernoulli
			assert p.save_interval == 50
			assert p.render_interval == 5
			assert p.time == 1
	
	
	
	
