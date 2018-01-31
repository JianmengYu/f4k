-- Imports

require 'torch'
require 'xlua'
require 'optim'

--

function test(partition, logger)
	local time = sys.clock()
	Yhat = torch.Tensor(partition.size, 10):zero()
	
	if average then
		cached_params = parameters:clone()
		parameters:copy(average)
	end
	
	model:evaluate() -- Set components to evaluation / testing mode
	
	for t=1,partition.size do
		xlua.progress(t, partition.size)
		
		local input = partition.data[t]
		local target = partition.Y[t]
		
		if opt.type == 'double' then
			input = input:double()
		elseif opt.type == 'cuda' then
			input = input:cuda()
		end
		
		local pred = model:forward(input)
		Yhat[{{t},{}}] = pred
		confusion:add(pred, target)
	end
	
	time = sys.clock() - time
	time = time / partition.size
  	print("\n==> Time to learn 1 sample = " .. (time * 1000) .. 'ms')
    print(confusion)
	
	logger:add{['% mean class accuracy (test set)'] = confusion.totalValid * 100}
	
	if average then -- Restore the parameters
		parameters:copy(cached_params)
	end
	
	confusion:zero()
	
	return Yhat
end
