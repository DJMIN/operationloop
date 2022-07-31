
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    from operationloop import run_ui

    run_ui()
