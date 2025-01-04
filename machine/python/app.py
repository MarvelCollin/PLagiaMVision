from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
from pathlib import Path
from checker import check_plagiarism_files
from datetime import datetime
import json
import queue
import threading

app = Flask(__name__)
CORS(app)

progress_queues = {}

# Update paths to be relative to the machine directory
UPLOAD_FOLDER = Path(__file__).parent.parent / 'data' / 'answer'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

@app.route('/check-plagiarism', methods=['POST'])
def handle_upload():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    # Create a temporary folder for this session
    session_folder = UPLOAD_FOLDER / f'temp_session_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    session_folder.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded files maintaining folder structure
    saved_files = []
    for file in files:
        # Create subdirectories if they don't exist
        file_path = session_folder / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the file
        file.save(str(file_path))
        saved_files.append(file_path)
    
    try:
        # Create a unique session ID
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        progress_queues[session_id] = queue.Queue()
        
        # Start processing in a separate thread
        thread = threading.Thread(
            target=process_files_with_progress,
            args=(saved_files, session_id, progress_queues[session_id])
        )
        thread.start()
        
        return jsonify({"session_id": session_id})
    except Exception as e:
        # Cleanup on error
        import shutil
        shutil.rmtree(str(session_folder))
        return jsonify({'error': str(e)}), 500

@app.route('/progress/<session_id>', methods=['GET'])
def get_progress(session_id):
    def generate():
        q = progress_queues.get(session_id)
        if not q:
            return
            
        while True:
            try:
                progress = q.get(timeout=30)  # 30 second timeout
                if progress == "DONE":
                    del progress_queues[session_id]
                    break
                yield f"data: {json.dumps(progress)}\n\n"
            except queue.Empty:
                break
            
    return Response(generate(), mimetype='text/event-stream')

def process_files_with_progress(files, session_id, progress_queue):
    try:
        results = check_plagiarism_files(files, progress_queue)
        
        # Store final results
        progress_queue.put({
            "status": "complete",
            "results": results
        })
        progress_queue.put("DONE")
        
    except Exception as e:
        progress_queue.put({
            "status": "error",
            "message": str(e)
        })
        progress_queue.put("DONE")

if __name__ == '__main__':
    app.run(port=5000)
