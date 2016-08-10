#! /bin/bash

# Uncomment following line for quiet output.
# python3 TodoTracker.py -Q -p ./ -f py,sh,to -ep DS_Store,git,gitignore,idea,ropeproject,vim,swp,vimrc,virutal,virtual |\
# 	more

# Uncomment following line for loud output.
python3 TodoTracker.py -p ./ -f py,sh,to -ep DS_Store,git,gitignore,idea,ropeproject,vim,swp,vimrc,virutal,virtual |\
	more


# The -ep flag has key phrases or sequences of characters for various folders that need to be avoided on this 
# particular project.
