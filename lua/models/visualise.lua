-- https://groups.google.com/forum/#!topic/torch7/Vb35a4701a4

function showFilters(weights, numFilters, filterSize)
    require 'nn'
    filters = {}

    label = label or ""
    bpp = 3

    if GRAYSCALE then
        bpp = 1
    end

    for i = 1, numFilters do
        bitmap = nn.Reshape(bpp, filterSize, filterSize)
        filters[i] = bitmap:forward(weights[i])
    end

    -- gfx.image(filters, {zoom=10, legend=label})
    return filters
end

-- showFilters(model:get(1).weights, 16, 5)
