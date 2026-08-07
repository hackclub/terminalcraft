def log_to_file(data, filename="port_log.txt"):
    with open(filename, "a") as f:
        f.write(data + "\n")