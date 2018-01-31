-- Imports

require 'image'
require 'nn'
require 'torch'
require 'xlua'

-- 

local PATH_DIR_DATA = paths.concat(opt.rootdir, 'data')
local thetas = torch.range(45, 315, 45)

-- From training data

if opt.modelname == 'N_SGD' then
	mean = {0.39652687546177, 0.45261265063944, 0.42062426025794}
	std = {0.28132888018719, 0.30690810636064, 0.30367700787976}
elseif opt.modelname == 'W_C_SGD' then
	mean = {0.9249023692381, 0.92963844758093, 0.92607431571841}
	std = {0.21736589663274, 0.20606532102447, 0.21408039791867}
elseif opt.modelname == 'B_C_SGD' then
	mean = {0.048790299759605, 0.052937559625764, 0.049839084833519}
	std = {0.15689543246897, 0.16453823057925, 0.15784736844257}
else
	mean = {0.5, 0.5, 0.5}
	std = {0.25, 0.25, 0.25}
end
--

function load_csv(filepath)
	-- Torch really sucks at loading data, csvigo doesn't work either
	-- Adapted from http://blog.aicry.com/torch7-reading-csv-into-tensor/
	local csvfile = io.open(filepath, 'r')
	local i = 0
	local files = {}
	local Y = {}
	
	for line in csvfile:lines() do
		i = i + 1
		local l = line:split(',')
		files[i] = l[1]
		Y[i] = tonumber(l[2])
	end
	
	csvfile:close()
	
	return files, Y
end

function load_data(filepath, expand)
	-- Loads the image files, returns the list of them and the Y labels
	local files, Y = load_csv(filepath)
	local frame_dir = opt.framedir
	local N = #files
	
	if opt.flip and expand then
		print('==> Flipping images')
		N = N * 2
	end
	
	if opt.rotate and expand then
		print('==> Rotating images')
		N = N + (N * 4)  -- Only use 4 of the thetas... kills the servers otherwise
	end
	
	local images = torch.FloatTensor(N, 3, 100, 100)
	local j = 1
	local Yp = {}
	
	print('==> Loading files for ' .. filepath .. ' to make ' .. N .. ' inputs')
	
	for i=1,#files do
		xlua.progress(j, N)
		local img = image.loadJPG(string.format('%s/%s', frame_dir, files[i])):float()
		images[{j,{},{},{}}] = img
		Yp[j] = Y[i]
		j = j + 1
		
		if opt.flip then
			local flipped = image.hflip(img):float()
			images[{j,{},{},{}}] = flipped
			Yp[j] = Y[i]
			j = j + 1
		
			if opt.rotate then
			
				for t=1,4 do
					local theta = thetas[t]
					local r = math.rad(theta)
					
					-- Do these need to be resized?
					local rotated_orig = image.rotate(img, r)
					local rotated_flip = image.rotate(flipped, r)
					
					image.scale(rotated_orig, '100x100')
					image.scale(rotated_flip, '100x100')

					images[{j,{},{},{}}] = rotated_orig
					Yp[j] = Y[i]
					j = j + 1
					
					images[{j,{},{},{}}] = rotated_flip
					Yp[j] = Y[i]
					j = j + 1
				end
			end
		
		elseif opt.rotate then
			local theta = thetas[t]
			local r = math.rad(theta)
			
			-- Do these need to be resized?
			local rotated_orig = img.rotate(r)

			images[{j,{},{},{}}] = image.scale(rotated_orig, '100x100')
			Yp[j] = Y[i]
			j = j + 1
		end
	end
	
	print('==> Finished loading images')
	
	return images, Yp, N	
end

-- Methods to lazy-load the data as required, instead of eating all RAM

function get_partition_data(which)
	local f_name = paths.concat(PATH_DIR_DATA, opt.dataname .. '.' .. which)
	local expand = false
	
	if paths.filep(f_name) and not opt.recompute then
		print('==> Loading ' .. which .. ' from ' .. f_name)
		data = torch.load(f_name)
	else
		print('==> Creating partition for ' .. which )
		if which == 'training' then
			csvfile = opt.trainingcsv
			expand = true
		elseif which == 'validation' then
			csvfile = opt.validationcsv
		else
			csvfile = opt.testcsv
		end
	
		d, l, s = load_data(csvfile, expand)
		dist = torch.Tensor(s, 10) -- Distribution of values
		dist:fill(-1)
		
		for i=1,s do
			dist[{i, l[i]}] = 1
		end
		
--		if opt.type == 'cuda' then
--			d = d:cuda()
--		end
	
		data = {
			data = d,
			Y = l,
			size = tonumber(s),
			dist = dist,
			type = which
		}
		
		if opt.preprocess then
			preprocess_data_yuv_normalize(data)
		end
		
		if not opt.skipsavedata then
			print('==> Saving ' .. which .. ' to ' .. f_name)
			torch.save(f_name, data)
		end
	end
	
	return data
end

function get_training_data()
	return get_partition_data('training')
end

function get_validation_data()
	return get_partition_data('validation')
end

function get_test_data()
	return get_partition_data('test')
end

function get_classify_data()
	local d = {}
	local data
	local frame_dir = opt.framedir
	local N = #paths.dir(frame_dir) - 2
	local images = torch.FloatTensor(N, 3, 100, 100)
	local i = 1
	
	print('==> Working with ' .. frame_dir)

	for f in paths.files(frame_dir) do
		if f:len() > 2 then
			local local_path = string.format('%s/%s', frame_dir, f)
--			print('==> Trying to load ' .. local_path)
			local img = image.loadJPG(local_path):float()
			images[{i,{},{},{}}] = img
			i = i + 1
		end
	end
		
	data = {
		data = images,
		size = N,
	}
	
	if opt.preprocess then
		preprocess_data_yuv_normalize(data)
	end
	
	return data
end

-- Preprocessing

function preprocess_data_yuv_normalize(partition)
	print(string.format('==> Preprocessing data, %i frames', partition.size))
	partition.data:float()  -- Make sure it's a float representation
	print('==> Converting RGB frames to YUV')
	
	for i=1,partition.size do
		xlua.progress(i, partition.size)
		partition[i] = image.rgb2yuv(partition.data[i])
	end
	
	print('==> Normalizing YUV channels')
	
--	mean = {}
--	std = {}
	
	for i=1,3 do
--		mean[i] = partition.data[{{},i,{},{}}]:mean()
--		std[i] = partition.data[{{},i,{},{}}]:std()
		partition.data[{{},i,{},{}}]:add(-mean[i])
		partition.data[{{},i,{},{}}]:div(std[i])
	end
	
	print(mean)
	print(std)
	
	neighbourhood = image.gaussian1D(13)
	normalization = nn.SpatialContrastiveNormalization(1, neighbourhood, 1):float()
	
	for c=1,3 do
		for i=1,partition.size do
			xlua.progress(i, partition.size)
			partition.data[{i,{c},{},{}}] = normalization:forward(partition.data[{i,{c},{},{}}])
		end
	end
	
end
