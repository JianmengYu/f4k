require 'image'
require 'nn'
require 'torch'
require 'xlua'

--

local PATH_DEFAULT_CSV_TRN = '/afs/inf.ed.ac.uk/group/project/F4KC/train.csv'
local PATH_DEFAULT_FRAMES = '/afs/inf.ed.ac.uk/group/project/F4KC/image_N'

--

cmd = torch.CmdLine()
cmd:text()
cmd:text('F4K RDS ConvNet')
cmd:text()
cmd:text('Options:')
-- global:
cmd:option('-seed', 1, 'fixed input seed for repeatable experiments')
cmd:option('-threads', 40, 'number of threads')
-- data:
cmd:option('-preprocess', true, 'preprocess the data - YUV & normalization')
cmd:option('-trainingcsv', PATH_DEFAULT_CSV_TRN, 'path to the training CSV file')
--cmd:option('-validationcsv', PATH_DEFAULT_CSV_VAL, 'path to the validation CSV file')
--cmd:option('-testcsv', PATH_DEFAULT_CSV_TST, 'path to the testing CSV file')
cmd:option('-framedir', PATH_DEFAULT_FRAMES, 'path to the input frames for the CSV files')

cmd:option('-outmatdir', 'mat/', 'folder to store mat files')
cmd:option('-dataname', 'cnn_n', 'prefix for the data')
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
cmd:option('-rootdir', '/afs/inf.ed.ac.uk/group/project/F4KC/cnn', 'root directory for saving things')
cmd:option('-save', '/afs/inf.ed.ac.uk/group/project/F4KC/cnn/results', 'subdirectory to save/log experiments in')
cmd:option('-plot', false, 'live plot')
cmd:option('-optimization', 'SGD', 'optimization method: SGD | ASGD | CG | LBFGS')
cmd:option('-learningRate', 1e-3, 'learning rate at t=0')
cmd:option('-batchSize', 128, 'mini-batch size (1 = pure stochastic)')
cmd:option('-weightDecay', 0, 'weight decay (SGD only)')
cmd:option('-momentum', 0, 'momentum (SGD only)')
cmd:option('-t0', 1, 'start averaging at t0 (ASGD only), in nb of epochs')
cmd:option('-maxIter', 2, 'maximum nb of iterations for CG and LBFGS')
cmd:option('-type', 'float', 'type: double | float | cuda')
-- execution:
cmd:option('-run', false, 'whether or not to run after setup')
cmd:option('-test', false, 'run the model specified in -modelname on the testing set')
cmd:option('-maxepoch', 400, 'max. number of training epochs')
cmd:option('-classify', false, 'classify new data')
cmd:text()
opt = cmd:parse(arg or {})

if opt.justbuild then
   dofile 'data.lua'
   get_training_data()
--   get_validation_data()
--   get_test_data()
   
   os.exit()
end

if opt.type == 'float' then
   print('==> Using floats')
   
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

dofile 'train.lua'
dofile 'test.lua'
dofile 'run.lua'
