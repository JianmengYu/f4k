-- Imports

require 'image'
require 'nn'

-- Parameters

n_outputs = 10  -- 10 classes of fish

n_feats = 3
width = 100  -- 32
height = 100 -- 32
n_inputs = n_feats * width * height

-- MLP NN Stuff
n_hidden = n_inputs / 2

-- CNN Stuff
n_states = {64, 64, 128, 30976}
filt_size = 5
pool_size = 2
norm_kern = image.gaussian1D(7)

-- Build the model

if opt.reloadmodel then
	print('==> Reloading model ' .. opt.modelname)
	local f_name = paths.concat(opt.save, opt.modelname .. '.' .. 'model.net')
	model = torch.load(f_name)
elseif opt.model == 'mlp' then
	-- This is a simple 2 layer NN with tanh HUs
	model = nn.Sequential()
	model:add(nn.Reshape(n_inputs))
	model:add(nn.Linear(n_inputs, n_hidden))
	model:add(nn.Tanh())
	model:add(nn.Linear(n_hidden, n_outputs))
elseif opt.model == 'convnet' then
	if opt.type == 'cuda' then
		print('==> CUDA ConvNet')
		-- CONV + RELU + POOL
		model = nn.Sequential()
		
		-- 1: Filter bank -> Squashing -> L2 pooling -> Normalization
		model:add(nn.SpatialConvolutionMM(n_feats, n_states[1], filt_size, filt_size))
		model:add(nn.ReLU())
		model:add(nn.SpatialMaxPooling(pool_size, pool_size, pool_size, pool_size))
		
		-- 2: Filter bank -> Squashing -> L2 pooling -> Normalization
		model:add(nn.SpatialConvolutionMM(n_states[1], n_states[2], filt_size, filt_size))
		model:add(nn.ReLU())
		model:add(nn.SpatialMaxPooling(pool_size, pool_size, pool_size, pool_size))
		
		-- 3: 2-layer NN
--		model:add(nn.View(n_states[2] * filt_size * filt_size))
		model:add(nn.View(n_states[4]))
		model:add(nn.Dropout(0.5))
--		model:add(nn.Linear(n_states[2] * filt_size * filt_size, n_states[3]))
		model:add(nn.Linear(n_states[4], n_states[3]))
		model:add(nn.ReLU())
		model:add(nn.Linear(n_states[3], n_outputs))
	else
		print('==> Conventional ConvNet')
		model = nn.Sequential()
		
		-- 1: Filter bank -> Squashing -> L2 pooling -> Normalization
		model:add(nn.SpatialConvolutionMM(n_feats, n_states[1], filt_size, filt_size))
		model:add(nn.Tanh())
		model:add(nn.SpatialLPPooling(n_states[1], 2, pool_size, pool_size, pool_size, pool_size))
		model:add(nn.SpatialSubtractiveNormalization(n_states[1], normkernel))
		
		-- 2: Filter bank -> Squashing -> L2 pooling -> Normalization
		model:add(nn.SpatialConvolutionMM(n_states[1], n_states[2], filt_size, filt_size))
		model:add(nn.Tanh())
		model:add(nn.SpatialLPPooling(n_states[2], 2, pool_size, pool_size, pool_size, pool_size))
		model:add(nn.SpatialSubtractiveNormalization(n_states[2], normkernel))
		
		-- 3: 2-layer NN
		-- model:add(nn.Reshape(n_states[2] * filt_size * filt_size))
		-- model:add(nn.Linear(n_states[2] * filt_size * filt_size, n_states[3]))
		model:add(nn.Reshape(n_states[4]))
		model:add(nn.Linear(n_states[4], n_states[3]))
		
		model:add(nn.Tanh())
		model:add(nn.Linear(n_states[3], n_outputs))
	end
end
--

print('==> Model:')
print(model)
