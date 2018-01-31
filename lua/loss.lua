-- Imports

require 'nn'

--

n_outputs = 10

if opt.loss == 'margin' then
	criterion = nn.MultiMarginCriterion()
elseif opt.loss == 'nll' then
	model:add(nn.LogSoftMax())
	criterion = nn.ClassNLLCriterion()
elseif opt.loss == 'mse' then
	model:add(nn.Tanh())
	criterion = nn.MSECriterion()
	criterion.sizeAverage = false
end
	
--
print('==> Loss function:')
print(criterion)
