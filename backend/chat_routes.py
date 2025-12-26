"""
EstateGPT Chat API Routes
Flask backend for conversational property search
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta
import uuid
from groq import Groq
import json

# Import your existing database connection
from database import get_db_connection

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Initialize Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# JWT secret key
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-this')

# ============================================
# AUTHENTICATION MIDDLEWARE
# ============================================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# ============================================
# CHAT MESSAGE ENDPOINT
# ============================================

@chat_bp.route('/chat/message', methods=['POST'])
def send_chat_message():
    """Send a message in a chat conversation"""
    token = request.headers.get('Authorization')
    user_id = None
    
    if token:
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = data['user_id']
        except:
            pass
    
    data = request.json
    chat_id = data.get('chat_id')
    message = data.get('message')
    conversation_history = data.get('conversation_history', [])
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        # Create or get chat
        if not chat_id and user_id:
            chat_id = str(uuid.uuid4())
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chats (id, user_id, title) VALUES (%s, %s, %s)",
                (chat_id, user_id, message[:50])
            )
            conn.commit()
            cursor.close()
            conn.close()
        
        # Save user message if authenticated
        if user_id and chat_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, role, content) VALUES (%s, %s, %s)",
                (chat_id, 'user', message)
            )
            conn.commit()
            cursor.close()
            conn.close()
        
        # Build conversation context
        context_messages = []
        for msg in conversation_history[-5:]:
            context_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # System message
        system_message = """You are EstateGPT, a friendly real estate assistant for properties in Bucharest and Ilfov County, Romania.

When users search for properties:
1. Acknowledge their request warmly
2. Extract criteria (location, price, bedrooms, type)
3. Ask clarifying questions if needed
4. Be conversational and helpful"""
        
        context_messages.insert(0, {'role': 'system', 'content': system_message})
        context_messages.append({'role': 'user', 'content': message})
        
        # Get AI response
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=context_messages,
            temperature=0.7,
            max_tokens=500
        )
        
        ai_message = response.choices[0].message.content
        
        # Check if property search
        search_indicators = ['apartment', 'house', 'property', 'bedroom', 'price', 'rent', 'buy', 'sale']
        is_search_query = any(indicator in message.lower() for indicator in search_indicators)
        
        properties = []
        if is_search_query:
            # Import your search function
            from search_engine import hybrid_search
            search_result = hybrid_search(message)
            properties = search_result.get('results', [])[:5]
        
        # Save assistant message
        if user_id and chat_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, role, content, properties) VALUES (%s, %s, %s, %s)",
                (chat_id, 'assistant', ai_message, json.dumps(properties) if properties else None)
            )
            cursor.execute(
                "UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (chat_id,)
            )
            conn.commit()
            cursor.close()
            conn.close()
        
        return jsonify({
            'chatId': chat_id,
            'message': ai_message,
            'properties': properties,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"[Chat Error] {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500

# ============================================
# CHAT HISTORY
# ============================================

@chat_bp.route('/chat/<chat_id>', methods=['GET'])
@token_required
def get_chat_history(current_user_id, chat_id):
    """Get full chat history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, title, created_at FROM chats WHERE id = %s AND user_id = %s",
            (chat_id, current_user_id)
        )
        chat = cursor.fetchone()
        
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        cursor.execute(
            """SELECT id, role, content, properties, created_at 
               FROM messages 
               WHERE chat_id = %s 
               ORDER BY created_at ASC""",
            (chat_id,)
        )
        messages = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'chat': {
                'id': chat[0],
                'title': chat[1],
                'created_at': chat[2].isoformat()
            },
            'messages': [
                {
                    'id': msg[0],
                    'role': msg[1],
                    'content': msg[2],
                    'properties': msg[3] if msg[3] else [],
                    'timestamp': msg[4].isoformat()
                }
                for msg in messages
            ]
        })
        
    except Exception as e:
        print(f"[Chat History Error] {str(e)}")
        return jsonify({'error': 'Failed to fetch chat history'}), 500

# ============================================
# CHAT LIST
# ============================================

@chat_bp.route('/chat/list', methods=['GET'])
@token_required
def get_chat_list(current_user_id):
    """Get user's chat list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, title, created_at, updated_at 
               FROM chats 
               WHERE user_id = %s 
               ORDER BY updated_at DESC 
               LIMIT 50""",
            (current_user_id,)
        )
        chats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify([
            {
                'id': chat[0],
                'title': chat[1],
                'created_at': chat[2].isoformat(),
                'updated_at': chat[3].isoformat()
            }
            for chat in chats
        ])
        
    except Exception as e:
        print(f"[Chat List Error] {str(e)}")
        return jsonify({'error': 'Failed to fetch chats'}), 500

# ============================================
# DELETE CHAT
# ============================================

@chat_bp.route('/chat/<chat_id>', methods=['DELETE'])
@token_required
def delete_chat(current_user_id, chat_id):
    """Delete a chat"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM chats WHERE id = %s AND user_id = %s",
            (chat_id, current_user_id)
        )
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Chat not found'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[Delete Chat Error] {str(e)}")
        return jsonify({'error': 'Failed to delete chat'}), 500

# ============================================
# FAVORITES
# ============================================

@chat_bp.route('/favorites', methods=['POST'])
@token_required
def add_favorite(current_user_id):
    """Add listing to favorites"""
    data = request.json
    listing_id = data.get('property_id')
    
    if not listing_id:
        return jsonify({'error': 'Property ID required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO favorites (user_id, listing_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (current_user_id, listing_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[Add Favorite Error] {str(e)}")
        return jsonify({'error': 'Failed to add favorite'}), 500

@chat_bp.route('/favorites/<listing_id>', methods=['DELETE'])
@token_required
def remove_favorite(current_user_id, listing_id):
    """Remove listing from favorites"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM favorites WHERE user_id = %s AND listing_id = %s",
            (current_user_id, listing_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[Remove Favorite Error] {str(e)}")
        return jsonify({'error': 'Failed to remove favorite'}), 500

@chat_bp.route('/favorites', methods=['GET'])
@token_required
def get_favorites(current_user_id):
    """Get user's favorite listings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT l.* FROM listings l
               INNER JOIN favorites f ON l.id = f.listing_id
               WHERE f.user_id = %s
               ORDER BY f.created_at DESC""",
            (current_user_id,)
        )
        listings = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format listings
        return jsonify([dict(zip([col[0] for col in cursor.description], row)) for row in listings])
        
    except Exception as e:
        print(f"[Get Favorites Error] {str(e)}")
        return jsonify({'error': 'Failed to fetch favorites'}), 500
