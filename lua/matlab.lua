-- Imports

dofile('util.lua')

-- Local functions

local function load_mat_file(mat_file)
	if VERBOSE then
		print(string.format("Loading the MAT file - %s", mat_file))
	end
	
	if is_mac then
		if VERBOSE then
			print("Running on OSX with matio")
		end
		
		local matio = require 'matio'
		return matio.load(mat_file)
	else
		if VERBOSE then
			print("Running on Linux with mattorch")
		end
		
		local mattorch = require 'mattorch'
		return mattorch.load(mat_file)
	end
end

local function get_mat_directory(mat_file)
	return string.format("%s%s", PATH_MAT, mat_file)
end

local function get_mat_split_path(mat_file, partition)
	return string.format("%s/%s.mat", get_mat_directory(mat_file), partition)
end

-- The above is the higher-level OS abstraction, expose
-- these methods for specific partitions relating to mat_file

function load_training(mat_file)
	local local_file = get_mat_split_path(mat_file, "training")
	local loaded = load_mat_file(local_file)
	
	return loaded.Xtrn, loaded.Ytrn
end

function load_validation(mat_file)
	local local_file = get_mat_split_path(mat_file, "validation")
	local loaded = load_mat_file(local_file)
	
	return loaded.Xval, loaded.Yval
end

function load_testing(mat_file)
	local local_file = get_mat_split_path(mat_file, "testing")
	local loaded = load_mat_file(local_file)
	
	return loaded.Xtst, loaded.Ytst
end

function save_Y(mat_file, Y)
	if is_linux then
		local mattorch = require 'mattorch'
		mattorch.save(mat_file, Y)
	end
end
