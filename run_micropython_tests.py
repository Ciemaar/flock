import sys
import os

# Ensure src is in the path
sys.path.append(os.getcwd() + '/src')
sys.path.append(os.getcwd() + '/test')

import test_micropython_core
test_micropython_core.run_all_tests()
