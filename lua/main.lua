--[[
	Build a CNN on the normalised images in the F4K RDS
	
	Created using the torch tutorials:
	https://github.com/torch/tutorials/
	
	Specifically: https://github.com/torch/tutorials/tree/master/2_supervised
   
   Natural dataset
   th main.lua -modelname N_SGD -dataname N -loss nll -type cuda -optimization SGD -weightDecay 0 -momentum 0 -run
   
   White-out dataset
   th main.lua -modelname W_SGD -dataname W -loss nll -type cuda -optimization SGD -weightDecay 0 -momentum 0 -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/whitened_frames/ -run

   Black-out dataset
   th main.lua -modelname B_SGD -dataname B -loss nll -type cuda -optimization SGD -weightDecay 0 -momentum 0 -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/blackened_frames/ -run

   White-out centred dataset
   th main.lua -modelname W_C_SGD -dataname W_C -loss nll -type cuda -optimization SGD -weightDecay 0 -momentum 0 -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/whitened_frames_centered/ -run

   Black-out centred dataset
   th main.lua -modelname B_C_SGD -dataname B_C -loss nll -type cuda -optimization SGD -weightDecay 0 -momentum 0 -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/blackened_frames_centered/ -run

   White-out centred, flipped and rotated - FI removed
   th main.lua -modelname W_C_F_R_YUV_SGD -dataname W_C_F_R_YUV -loss nll -type double -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/whitened_frames_centered/ -flip -rotate -justbuild
   
   th main.lua -modelname W_C_F_R_YUV_SGD -dataname W_C_F_R_YUV -loss nll -type cuda -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/whitened_frames_centered/ -flip -rotate -run

   Black-out centred, flipped and rotated - FI removed
   th main.lua -modelname B_C_F_R_YUV_SGD -dataname B_C_F_R_YUV -loss nll -type double -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/blackened_frames_centered/ -flip -rotate -justbuild
   
   th main.lua -modelname B_C_F_R_YUV_SGD -dataname B_C_F_R_YUV -loss nll -type cuda -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/blackened_frames_centered/ -flip -rotate -run
   
   CLASSIFYING NEW DATA
   th main.lua -classify -type float -modelname <model> -reloadmodel -save models/float -framedir <frame_dir>
   
   TESTING
   
   N
   th main.lua -test -skipsavedata -type float -modelname N_SGD -reloadmodel -save models/float -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/frames/
   
   W_C
   th main.lua -test -skipsavedata -type float -modelname W_C_SGD -reloadmodel -save models/float -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/whitened_frames_centered/
   
   B_C
      th main.lua -test -skipsavedata -type float -modelname B_C_SGD -reloadmodel -save models/float -framedir /afs/inf.ed.ac.uk/group/msc-projects/s1459650/blackened_frames_centered/
--]]

require 'torch'

--

local PATH_DEFAULT_MAT_IMG = '/afs/inf.ed.ac.uk/group/msc-projects/s1459650/workspace/cnn/mat/'
local PATH_DEFAULT_CSV_TRN = '/afs/inf.ed.ac.uk/group/msc-projects/s1459650/workspace/cnn/training_truncated.csv'
local PATH_DEFAULT_CSV_VAL = '/afs/inf.ed.ac.uk/group/msc-projects/s1459650/workspace/cnn/validation_truncated.csv'
local PATH_DEFAULT_CSV_TST = '/afs/inf.ed.ac.uk/group/msc-projects/s1459650/workspace/cnn/test_truncated.csv'
local PATH_DEFAULT_FRAMES = '/afs/inf.ed.ac.uk/group/msc-projects/s1459650/frames/'

--

cmd = torch.CmdLine()
cmd:text()
cmd:text('F4K RDS ConvNet')
cmd:text()
cmd:text('Options:')
-- global:
cmd:option('-seed', 1, 'fixed input seed for repeatable experiments')
cmd:option('-threads', 10, 'number of threads')
-- data:
cmd:option('-preprocess', true, 'preprocess the data - YUV & normalization')
cmd:option('-trainingcsv', PATH_DEFAULT_CSV_TRN, 'path to the training CSV file')
cmd:option('-validationcsv', PATH_DEFAULT_CSV_VAL, 'path to the validation CSV file')
cmd:option('-testcsv', PATH_DEFAULT_CSV_TST, 'path to the testing CSV file')
cmd:option('-framedir', PATH_DEFAULT_FRAMES, 'path to the input frames for the CSV files')
cmd:option('-framematdir', PATH_DEFAULT_MAT_IMG, 'path to the input frames for the CSV files')
cmd:option('-outmatdir', 'mat/', 'folder to store mat files')
cmd:option('-dataname', 'default', 'prefix for the data')
cmd:option('-flip', false, 'generate faux-samples through flipping on x-axis')
cmd:option('-rotate', false, 'generate faux-samples through rotating a number of times')
cmd:option('-recompute', false, 'ignore saved data, regenerate it')
cmd:option('-justbuild', false, 'just build and preprocess the data (and save it)')
cmd:option('-skipsavedata', false, 'dont save the generated partition')
-- model:
cmd:option('-model', 'convnet', 'type of model to construct: mlp | convnet')
cmd:option('-modelname', 'default', 'experiment identifier')
cmd:option('-reloadmodel', false, 'reloads a saved model to continue training')
-- loss:
cmd:option('-loss', 'nll', 'type of loss function to minimize: nll | mse | margin')
-- training:
cmd:option('-rootdir', '/disk/scratch/s1459650/cnn', 'root directory for saving things')
cmd:option('-save', '/disk/scratch/s1459650/cnn/results', 'subdirectory to save/log experiments in')
cmd:option('-plot', false, 'live plot')
cmd:option('-optimization', 'SGD', 'optimization method: SGD | ASGD | CG | LBFGS')
cmd:option('-learningRate', 1e-3, 'learning rate at t=0')
cmd:option('-batchSize', 128, 'mini-batch size (1 = pure stochastic)')
cmd:option('-weightDecay', 0, 'weight decay (SGD only)')
cmd:option('-momentum', 0, 'momentum (SGD only)')
cmd:option('-t0', 1, 'start averaging at t0 (ASGD only), in nb of epochs')
cmd:option('-maxIter', 2, 'maximum nb of iterations for CG and LBFGS')
cmd:option('-type', 'cuda', 'type: double | float | cuda')
-- execution:
cmd:option('-run', false, 'whether or not to run after setup')
cmd:option('-test', false, 'run the model specified in -modelname on the testing set')
cmd:option('-maxepoch', 400, 'max. number of training epochs')
cmd:option('-classify', false, 'classify new data')
cmd:text()
opt = cmd:parse(arg or {})

--

if opt.justbuild then
   dofile 'data.lua'
   get_training_data()
--   get_validation_data()
--   get_test_data()
   
   os.exit()
end

--

if opt.type == 'float' then
   print('==> Using floats')
   
   torch.setdefaulttensortype('torch.FloatTensor')
elseif opt.type == 'cuda' then
   print('==> Using CUDA')
   
   require 'cunn'  -- Can this be cuDNN?
   torch.setdefaulttensortype('torch.FloatTensor')
end

torch.setnumthreads(opt.threads)
torch.manualSeed(opt.seed)

--
print('==> Model name: ' .. opt.modelname)
--

dofile 'data.lua'
dofile 'model.lua'
dofile 'loss.lua'

--

if opt.classify then
   require 'mattorch'
   
   dofile 'classify.lua'
   
--   partition = get_classify_data()
--   Yhat = torch.Tensor(partition.size, 1):zero()
   
   Yhat = classify()
   
   -- For mattorch
   torch.setdefaulttensortype('torch.DoubleTensor')
   Yhat = Yhat:double()
   parts = string.split(opt.framedir, '/')
   mat = parts[#parts]
   path = paths.concat(opt.outmatdir, mat .. '.mat')
   
   mattorch.save(path, {Yhat_cnn = Yhat})
elseif opt.test then
   dofile 'train.lua'
   dofile 'test.lua'
   dofile 'test.lua'

   if not log_test then
   	log_test = optim.Logger(paths.concat(opt.save, 'test.log'))
   end

	test_data = get_test_data()
	Yhat = test(test_data, log_test)
	test_data = nil
   
   -- For mattorch
   require 'mattorch'
   
   torch.setdefaulttensortype('torch.DoubleTensor')
   Yhat = Yhat:double()
   path = paths.concat(opt.outmatdir, opt.modelname .. '.mat')
   
   mattorch.save(path, {Yhat_cnn = Yhat})
elseif opt.run then
   dofile 'train.lua'
   dofile 'test.lua'
   dofile 'run.lua'
end
