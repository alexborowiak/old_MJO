def back_directory(cwd, num):
    parts = cwd.split('/')
    total = len(parts) - num

    for i in range(total):
        if i == 0:
             direct = parts[i]
        else:
            direct = direct + '/'+ parts[i]
    return direct + '/'
