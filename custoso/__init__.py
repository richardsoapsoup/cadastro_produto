import threading
def exemploThread(parametro):

    thread = threading.Thread(target=exemploThread, args=(parametro,))
    thread.start()

