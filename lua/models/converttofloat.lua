require 'paths'
require 'cunn'

local P_CUDA = 'cuda/'
local P_FLOAT = 'float/'

models = {'B_C', 'N', 'W_C'}

for m=1,#models do
	from = P_CUDA .. models[m] .. '_SGD.model.net'
	to = P_FLOAT .. models[m] .. '_SGD.model.net'
	
	print(string.format("==> Converting from %s to %s", from, to))
	model = torch.load(from)
	model = model:float()
	torch.save(to, model)
end
