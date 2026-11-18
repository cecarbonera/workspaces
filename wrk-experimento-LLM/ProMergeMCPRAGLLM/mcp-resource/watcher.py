import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import time, shutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from promerge_rag import promerge_files_indexes

# defauls paths of the folders for the file processing
DOCUMENTS = "./Documents"
PROCESSED = "./Processed"

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        # Indexing the new file in the Documents folder
        promerge_files_indexes(DOCUMENTS)

        # Move to "Processed" folder the (all) files from the Documentos folder to the Processed folder
        for file in os.listdir(DOCUMENTS):               
            shutil.move(os.path.join(DOCUMENTS, file), os.path.join(PROCESSED, file))

# Initialize the file processing by indexing existing files and setting up a watcher for new files in the Documentos folder
def initialize_files_processment():
    # Create the necessary directories if they don't exist
    for directories in [DOCUMENTS, PROCESSED]:
        os.makedirs(directories, exist_ok = True)

    # Initial message indicating that the file processing is starting
    print("Processing files... please wait!")

    # Indexing the new file in the Documents folder
    promerge_files_indexes(DOCUMENTS)

    # Move to "Processed" folder the (all) files from the Documentos folder to the Processed folder
    for file in os.listdir(DOCUMENTS):               
        shutil.move(os.path.join(DOCUMENTS, file), os.path.join(PROCESSED, file))    
    
    # Observer the Documentos folder for new files
    observer = Observer()
    observer.schedule(Handler(), DOCUMENTS, recursive = True)
    observer.start()

    # Logs a message indicating that the watcher has been activated and is monitoring for new files
    print("Watcher activated...")
    print("3nd Step - Finished.")        
    print("Process of Initialization Finished.")

    try:
        while True:
            time.sleep(5)   # Waits for 5 seconds before checking for new files again

    except KeyboardInterrupt:
        observer.stop()

    # Waits for the observer thread to finish before exiting the program
    observer.join()

#
# Must be commented to avoid running the file directly, as it is intended to be imported and used by other scripts.
#
if __name__ == "__main__":
    # Start the file processing initialization, which includes indexing existing files and setting up a watcher for new files in the Documentos folder
    initialize_files_processment()