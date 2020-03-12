import sys

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }

    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]


platform = get_platform()


if platform == 'OS X':
    path =  '/Users/alexborowiak/Desktop/large_files/'

else:
    path == '/home/student.unimelb.edu.au/aborowiak/Desktop/Code/Scripts/big_files/'


precip = xr.open_dataset(path + 'AWAP_w.nc')
