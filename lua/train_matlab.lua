--[[
	This Neural Net was built using a number of resources, specifically the excellent
	videos from Oxford's CS department:
	
	* https://www.youtube.com/watch?v=-YRB0eFxeQA
	* https://www.youtube.com/watch?v=NUKp0c4xb8w
	* https://www.youtube.com/watch?v=bEUX_56Lojc
	
	And also example projects in Torch:
	
	* https://github.com/hpenedones/luacnn/
	
	And literature:
	
	* http://neuralnetworksanddeeplearning.com/chap3.html
--]]

-- Imports

local paths = require 'paths'

-- Functions

function create_network()

end

function train_network(X, Y)

	for i=1,max_iterations do
	
	end

end

function validation_score()

end

function main()
	local mat_file = 'cnn_pca_28'
	local X_trn, Y_trn = load_training(mat_file)
	local network = create_network(#classes)
	
	
	local X_val, Y_val = load_validation(mat_file)
	local v_score = validation_score(network, X_val, Y_val)
	local X_tst, Y_tst = load_test(mat_file)
end

function main_production()
	dofile('matlab.lua')

	if #arg == 0 then
		print('Unable to train a network without an identifier argument.')
	elseif not is_valid_mat_path(arg[1]) then
		print(string.format("Can't find the export folder %s", arg[1]))
	else
		local mat_file = arg[1]
		local X_trn, Y_trn = load_training(mat_file)
		local X_val, Y_val = load_validation(mat_file)
		local X_tst, Y_tst = load_test(mat_file)
		
		local network = create_network(#classes)
		train_network(network, X_trn, Y_trn)
		local v_score = validation_score(network, X_val, Y_val)
		local t_score = test_network(network, X_tst, Y_tst)
	end
end

main()
