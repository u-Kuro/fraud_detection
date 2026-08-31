def sequence(*tasks):
    assert tasks
    for i in range(len(tasks) - 1):
        # noinspection statement-effect
        tasks[i] >> tasks[i + 1]
    # To return the first task in sequence as a direct downstream
    return tasks[0]