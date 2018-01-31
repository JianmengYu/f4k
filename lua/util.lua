-- Imports

local paths = require 'paths'

-- Local variables

local os_name = nil;
local PATH_MAT = '/afs/inf.ed.ac.uk/group/msc-projects/s1459650/workspace/mat/cnn/'
local PATH_MAT_DICE = '/afs/inf.ed.ac.uk/user/s14/s1459650/workspace/mat/cnn/'
local PATH_SCRATCH = '/disk/scratch/s1459650/cnn/'
local VERBOSE = true;

--

function get_os_name()
	--[[
		This returns the kernel name:
		OS -> 'Darwin'
		Linux -> 'Linux'
		Windows -> 'Windows' 
	--]]

	if not os_name == nil then
		return os_name
	end
	
    -- Unix, Linux variants
    fh, err = io.popen("uname", "r")
	
    if fh then
        os_name = fh:read()
    end
	
    if os_name then 
		return os_name
	end

    -- 
    return "Windows"
end

function is_valid_mat_path(mat_path)
	return paths.dirp(get_mat_directory(mat_file))
end

is_mac = get_os_name() == 'Darwin'
is_linux = not is_mac
