-- Imports

require 'torch'
require 'xlua'
require 'optim'

-- CUDAfy

if opt.type == 'cuda' then
	print('==> Converting model and criterion to CUDA')
	model:cuda()
	criterion:cuda()
end

-- Variables

classes = {'1','2','3','4','5','6','7','8','9','0'}
confusion = optim.ConfusionMatrix(classes)

log_training = optim.Logger(paths.concat(opt.save, opt.modelname .. '.training.log'))
log_validation = optim.Logger(paths.concat(opt.save, opt.modelname .. '.validation.log'))
log_test = optim.Logger(paths.concat(opt.save, opt.modelname .. '.test.log'))

if model then
	parameters, gradient_parameters = model:getParameters()
end

-- Optimiser

if opt.optimization == 'CG' then
   optim_state = {
      maxIter = opt.maxIter
   }
   optim_method = optim.cg
elseif opt.optimization == 'LBFGS' then
   optim_state = {
      learningRate = opt.learningRate,
      maxIter = opt.maxIter,
      nCorrection = 10
   }
   optim_method = optim.lbfgs
elseif opt.optimization == 'SGD' then
   optim_state = {
      learningRate = opt.learningRate,
      weightDecay = opt.weightDecay,
      momentum = opt.momentum,
      learningRateDecay = 1e-7
   }
   optim_method = optim.sgd
elseif opt.optimization == 'ASGD' then
   optim_state = {
      eta0 = opt.learningRate,
      t0 = trsize * opt.t0
   }
   optim_method = optim.asgd
else
   error('unknown optimization method')
end

-- Training

function train()
   local training_data = get_training_data()
   
   epoch = epoch or 1
   local time = sys.clock()
   model:training() -- Tell components they're in training mode
   shuffle = torch.randperm(training_data.size)
   
   print('==> Epoch on training data:')
   print('==> Online epoch #' .. epoch .. ' [batchSize=' .. opt.batchSize .. ']')
   
   for t=1,training_data.size,opt.batchSize do
      xlua.progress(t, training_data.size)
      
      -- Start mini batch
      local inputs = {}
      local targets = {}
      
      for i=t,math.min(t + opt.batchSize - 1, training_data.size) do
         local input = training_data.data[shuffle[i]]
         local target = training_data.Y[shuffle[i]]
         
         if opt.type == 'double' then
            input = input:double()
         elseif opt.type == 'cuda' then
            input = input:cuda()
         end
         
         table.insert(inputs, input)
         table.insert(targets, target)
      end
      -- End mini batch
      
      -- f(x) and df/dX
      local f_eval = function(x)
         if x ~= parameters then
            parameters:copy(x)
         end
         
         gradient_parameters:zero()  -- Reset
         local f = 0 -- Avg. of all criterions
         
         for i = 1,#inputs do -- Eval f for mini batch
            local output = model:forward(inputs[i])
            local err = criterion:forward(output, targets[i])
            f = f + err
            
            -- df/dW
            local df_do = criterion:backward(output, targets[i])
            model:backward(inputs[i], df_do)
            
            confusion:add(output, targets[i])
         end
         
         gradient_parameters:div(#inputs)
         f = f / #inputs
         
         return f, gradient_parameters
      end
      
      if optim_method == optim.asgd then
         _, _, average = optim_method(f_eval, parameters, optim_state)
      else
         optim_method(f_eval, parameters, optim_state)
      end
   end
   
   time = sys.clock() - time
   time = time / training_data.size
   print("\n==> Time to learn 1 sample = " .. (time * 1000) .. 'ms')
   print(confusion)
   
   log_training:add{['% mean class accuracy (train set)'] = confusion.totalValid * 100}
   
   -- Save the net
   local f_name = paths.concat(opt.save, opt.modelname .. '.' .. 'model.net')
   os.execute('mkdir -p ' .. sys.dirname(f_name))
   print('==> Saving model to ' .. f_name)
   torch.save(f_name, model)
   
   -- Next epoch
   confusion:zero()
   epoch = epoch + 1
   
   training_data = nil
end
