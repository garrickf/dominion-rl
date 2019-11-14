def generator():
    choices = [0, 1, 2, 3, 4, 5]
    # Prompt agent to make choice from set of discrete choices
    choice = (yield choices)
    print('chose', choice)
    choices = [i for i in range(4) if i != choice]
    choice = (yield choices)
    print('chose', choice)
    print('all done!')
    return