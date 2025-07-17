from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import traceback
from datetime import datetime
from inference import run_inference, get_model_info  # Import get_model_info juga

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'webp', 'bmp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")  # WebSocket support

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global thresholds
confidence_threshold = 0.3
iou_threshold = 0.5

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_error(error_msg, exception=None):
    """Helper function untuk logging error"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] ERROR: {error_msg}")
    if exception:
        print(f"[{timestamp}] TRACEBACK: {traceback.format_exc()}")

# 1. Upload endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file part in request'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not file or not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # Get file info
        file_size = os.path.getsize(filepath)
        
        # Emit WebSocket event untuk update UI
        socketio.emit('file_uploaded', {
            'filename': filename,
            'file_size': file_size,
            'message': f'File {filename} uploaded successfully'
        })
        
        return jsonify({
            'success': True,
            'filename': filename,
            'file_size': file_size,
            'message': 'File uploaded successfully'
        }), 200
        
    except Exception as ex:
        log_error('Upload error', ex)
        return jsonify({
            'success': False,
            'error': f'Upload error: {str(ex)}'
        }), 500

# 2. Inference endpoint - FIXED VERSION
@app.route('/inference', methods=['POST'])
def do_inference():
    try:
        global confidence_threshold, iou_threshold
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        filename = data.get('filename')
        conf = float(data.get('conf', confidence_threshold))
        iou = float(data.get('iou', iou_threshold))
        
        # Validate input
        if not filename or not allowed_file(filename):
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        if not (0.0 <= conf <= 1.0):
            return jsonify({
                'success': False,
                'error': 'Confidence threshold must be between 0.0 and 1.0'
            }), 400
            
        if not (0.0 <= iou <= 1.0):
            return jsonify({
                'success': False,
                'error': 'IoU threshold must be between 0.0 and 1.0'
            }), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        # Emit WebSocket event untuk notifikasi start processing
        socketio.emit('inference_started', {
            'filename': filename,
            'conf': conf,
            'iou': iou,
            'message': 'Starting inference...'
        })
        
        # ✅ FIXED: Gunakan format baru - hanya 1 return value
        result = run_inference(filepath, conf, iou)
        
        # Check jika inference berhasil
        if not result.get("success", False):
            log_error(f"Inference failed for {filename}", None)
            
            # Emit error via WebSocket
            socketio.emit('inference_error', {
                'filename': filename,
                'error': result.get('error', 'Unknown inference error')
            })
            
            return jsonify(result), 500
        
        # Emit WebSocket event untuk notifikasi selesai
        socketio.emit('inference_completed', {
            'filename': filename,
            'total_detections': result.get('detection_summary', {}).get('total_detections', 0),
            'processing_time': result.get('inference_info', {}).get('total_processing_time', 0),
            'message': 'Inference completed successfully'
        })
        
        # Return result dalam format yang diperlukan frontend
        response = {
            'success': True,
            'output_url': result['image_info']['url'],  # URL gambar hasil
            'result': result,  # Full result object
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except ValueError as ve:
        error_msg = f'Invalid parameter values: {str(ve)}'
        log_error(error_msg, ve)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 400
        
    except Exception as ex:
        error_msg = f'Inference error: {str(ex)}'
        log_error(error_msg, ex)
        
        # Emit error via WebSocket
        socketio.emit('inference_error', {
            'filename': data.get('filename', 'unknown'),
            'error': error_msg
        })
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

# 3. Get uploaded file
@app.route('/uploads/<filename>')
def uploaded_files(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404

# 4. Serve static files (hasil inference)
@app.route('/static/<filename>')
def static_files(filename):
    try:
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Static file not found'
        }), 404

# 5. Model info endpoint
@app.route('/api/model-info', methods=['GET'])
def model_information():
    try:
        model_info = get_model_info()
        return jsonify(model_info)
    except Exception as e:
        log_error('Model info error', e)
        return jsonify({
            'success': False,
            'error': f'Failed to get model information: {str(e)}'
        }), 500

# 6. Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test model loading
        model_info = get_model_info()
        
        return jsonify({
            'status': 'healthy',
            'model_loaded': True,
            'model_info': {
                'name': model_info.get('model_name', 'Unknown'),
                'classes': model_info.get('total_classes', 0)
            },
            'folders': {
                'upload': UPLOAD_FOLDER,
                'output': OUTPUT_FOLDER
            },
            'thresholds': {
                'confidence': confidence_threshold,
                'iou': iou_threshold
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'model_loaded': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 7. Get current thresholds
@app.route('/api/thresholds', methods=['GET'])
def get_thresholds():
    return jsonify({
        'confidence': confidence_threshold,
        'iou': iou_threshold
    })

# 8. Set thresholds via HTTP (alternative to WebSocket)
@app.route('/api/thresholds', methods=['POST'])
def set_thresholds_http():
    try:
        global confidence_threshold, iou_threshold
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        if 'confidence' in data:
            conf = float(data['confidence'])
            if 0.0 <= conf <= 1.0:
                confidence_threshold = conf
            else:
                return jsonify({'error': 'Confidence must be between 0.0 and 1.0'}), 400
        
        if 'iou' in data:
            iou = float(data['iou'])
            if 0.0 <= iou <= 1.0:
                iou_threshold = iou
            else:
                return jsonify({'error': 'IoU must be between 0.0 and 1.0'}), 400
        
        # Emit via WebSocket
        socketio.emit('thresholds_updated', {
            'confidence': confidence_threshold,
            'iou': iou_threshold
        })
        
        return jsonify({
            'success': True,
            'confidence': confidence_threshold,
            'iou': iou_threshold,
            'message': 'Thresholds updated successfully'
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid numeric values'}), 400
    except Exception as e:
        log_error('Set thresholds error', e)
        return jsonify({'error': str(e)}), 500

# =====================================
# WEBSOCKET EVENTS
# =====================================

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {
        'message': 'Connected to YOLO inference server',
        'thresholds': {
            'confidence': confidence_threshold,
            'iou': iou_threshold
        }
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('set_threshold')
def set_threshold(data):
    try:
        global confidence_threshold, iou_threshold
        
        if 'confidence' in data:
            conf = float(data['confidence'])
            if 0.0 <= conf <= 1.0:
                confidence_threshold = conf
                print(f"Confidence threshold updated to {confidence_threshold}")
            else:
                emit('error', {'message': 'Confidence must be between 0.0 and 1.0'})
                return
        
        if 'iou' in data:
            iou = float(data['iou'])
            if 0.0 <= iou <= 1.0:
                iou_threshold = iou
                print(f"IoU threshold updated to {iou_threshold}")
            else:
                emit('error', {'message': 'IoU must be between 0.0 and 1.0'})
                return
        
        # Broadcast to all clients
        emit('thresholds_updated', {
            'confidence': confidence_threshold,
            'iou': iou_threshold
        }, broadcast=True)
        
    except ValueError:
        emit('error', {'message': 'Invalid threshold values'})
    except Exception as e:
        log_error('WebSocket set_threshold error', e)
        emit('error', {'message': f'Error setting threshold: {str(e)}'})

@socketio.on('get_status')
def handle_get_status():
    try:
        model_info = get_model_info()
        emit('status_update', {
            'model_loaded': True,
            'model_name': model_info.get('model_name', 'Unknown'),
            'total_classes': model_info.get('total_classes', 0),
            'thresholds': {
                'confidence': confidence_threshold,
                'iou': iou_threshold
            },
            'folders': {
                'upload': UPLOAD_FOLDER,
                'output': OUTPUT_FOLDER
            }
        })
    except Exception as e:
        emit('status_update', {
            'model_loaded': False,
            'error': str(e)
        })

# =====================================
# ERROR HANDLERS
# =====================================

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] / (1024*1024):.1f}MB'
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/upload (POST)',
            '/inference (POST)', 
            '/uploads/<filename> (GET)',
            '/static/<filename> (GET)',
            '/api/model-info (GET)',
            '/api/health (GET)',
            '/api/thresholds (GET/POST)'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# =====================================
# STARTUP
# =====================================

if __name__ == '__main__':
 
    # Test model loading
    try:
        model_info = get_model_info()
        print(f"✅ Model loaded: {model_info['model_name']}")
        print(f"📊 Supports {model_info['total_classes']} classes")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print("⚠️  Server will start but inference may not work")
    
    # Start server
    socketio.run(
        app, 
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        allow_unsafe_werkzeug=True  # For development only
    )