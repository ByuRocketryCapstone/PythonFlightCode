from enum import Enum

class st(Enum):
    init_st = 1
    run_st = 2

state = st.run_st
print(str(state))