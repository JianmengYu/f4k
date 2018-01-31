-- Need to load / unserialize the saved NN


-- Now need to query it with the data passed through


-- Return the predictions

function classify()
	model:evaluate()
	partition = get_classify_data()
	Yhat = torch.Tensor(partition.size, 10):zero()
	
	for t=1,partition.size do
		xlua.progress(t, partition.size)
		local input = partition.data[t]
		
		if opt.type == 'double' then
			input = input:double()
		elseif opt.type == 'cuda' then
			input = input:cuda()
		end
		
		Yhat[{{t},{}}] = model:forward(input)
	end
	
	return Yhat
end
