from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from pathlib import Path
from checker import check_plagiarism_files
from datetime import datetime

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Update paths to be relative to the machine directory
UPLOAD_FOLDER = Path(__file__).parent.parent / 'data' / 'answer'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

@app.route('/check-plagiarism', methods=['POST'])
def handle_upload():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    # Create a temporary folder for this session
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_folder = UPLOAD_FOLDER / f'temp_session_{session_id}'
    session_folder.mkdir(parents=True, exist_ok=True)
    
    try:
        # Save uploaded files
        saved_files = []
        total_files = len(files)
        
        socketio.emit('progress', {
            'status': 'Saving files...',
            'progress': 0,
            'total': total_files
        })

        for i, file in enumerate(files, 1):
            file_path = session_folder / file.filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(str(file_path))
            saved_files.append(file_path)
            
            socketio.emit('progress', {
                'status': f'Saving file {i}/{total_files}',
                'progress': i,
                'total': total_files
            })
        
        # Process files
        results = check_plagiarism_files(saved_files, session_id)
        
        # Cleanup
        import shutil
        shutil.rmtree(str(session_folder))
        
        return jsonify(results)
    except Exception as e:
        socketio.emit('progress', {
            'status': f'Error: {str(e)}',
            'error': True
        })
        import shutil
        shutil.rmtree(str(session_folder))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, port=5000)
