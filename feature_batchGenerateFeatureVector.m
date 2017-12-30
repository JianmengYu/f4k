function [features] = feature_batchGenerateFeatureVector(rgbimgs, binimgs)
% [rgbimg, binimg] = append_shrinkImage(rgbimg, binimg);  % TODO Matt not
% needed, all M x M
    len = size(binimgs,1)
    features = zeros(len, 2626);
    parfor i=1:100;
        features(i,:) = feature_generateFeatureVector(squeeze(rgbimgs(i,:,:,:)),squeeze(binimgs(i,:,:)),0);
    end