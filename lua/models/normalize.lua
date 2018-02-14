require 'image'
require 'nn'

function preprocess_data_yuv_normalize(imagein,opt)
-- lua shucks

  if opt == 'N_SGD' then
    mean = {0.39652687546177, 0.45261265063944, 0.42062426025794}
    std = {0.28132888018719, 0.30690810636064, 0.30367700787976}
  elseif opt == 'W_C_SGD' then
    mean = {0.9249023692381, 0.92963844758093, 0.92607431571841}
    std = {0.21736589663274, 0.20606532102447, 0.21408039791867}
  elseif opt == 'B_C_SGD' then
    mean = {0.048790299759605, 0.052937559625764, 0.049839084833519}
    std = {0.15689543246897, 0.16453823057925, 0.15784736844257}
  else
    mean = {0.5, 0.5, 0.5}
    std = {0.25, 0.25, 0.25}
  end

  imagein:double()
  imagein = image.rgb2yuv(imagein)

  for i=1,3 do
	imagein[i]:add(-mean[i])
	imagein[i]:div(std[i])
  end

  neighbourhood = image.gaussian1D(13)
  normalization = nn.SpatialContrastiveNormalization(1, neighbourhood, 1):double()

  for c=1,3 do
	imagein[{{c},{},{}}] = normalization:forward(imagein[{{c},{},{}}])
  end

  return imagein

end
