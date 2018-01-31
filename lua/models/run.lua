require 'image'
require 'cunn'
require 'paths'

torch.setdefaulttensortype('torch.FloatTensor')
dofile 'visualise.lua'

whichmodel = 'B_C'
model = torch.load('cuda/' .. whichmodel .. '_SGD.model.net')
fmodel = model:float()
which = 1  -- Also 1 & 4
layer = fmodel:get(which)

print(layer)

filters = showFilters(layer.weight, 64, 5)

output_dir = 'filters/' .. whichmodel .. '/' .. which

if not paths.dirp(output_dir) then
	paths.mkdir(output_dir)
end
	
for i = 1, #filters do
	image.save(output_dir .. '/' .. i .. '.png', filters[i])
end
