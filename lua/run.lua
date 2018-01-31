

if not log_validation then
	log_validation = optim.Logger(paths.concat(opt.save, opt.modelname .. '.validation.log'))
end

epoch = 1

while epoch < opt.maxepoch do
	train()
	
	validation_data = get_validation_data()
	test(validation_data, log_validation)
	validation_data = nil
end
