"""
EstateGPT Chat API Routes - Complete with Supabase
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
from datetime import datetime
import uuid
from groq import Groq
import json

# Import your existing database
from database import db

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Groq client (initialized lazily)
groq_client = None

def get_groq_client():
    global groq_client
    if groq_client is None:
        try:
            groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        except Exception as e:
            print(f"[Groq Init Warning] {str(e)}")
            groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    return groq_client

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
            db.client.table('chats').insert({
                'id': chat_id,
                'user_id': user_id,
                'title': message[:50]
            }).execute()
        
        # Save user message if authenticated
        if user_id and chat_id:
            db.client.table('messages').insert({
                'chat_id': chat_id,
                'role': 'user',
                'content': message
            }).execute()
        
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
        
        # Temporary hardcoded response (Groq has issues in Railway Python 3.13)
        ai_message = "Hello! I'm EstateGPT, your AI assistant for finding properties in Bucharest and Ilfov County. I can help you search for apartments, houses, and commercial properties. What are you looking for today?"
        
        # Check if property search
        search_indicators = ['apartment', 'house', 'property', 'bedroom', 'price', 'rent', 'buy', 'sale', 'garsoniera', 'studio']
        is_search_query = any(indicator in message.lower() for indicator in search_indicators)
        
        properties = []
        if is_search_query:
            try:
                from search import hybrid_search
                search_result = hybrid_search(message)
                properties = search_result.get('results', [])[:5]
            except Exception as search_error:
                print(f"[Search Error] {str(search_error)}")
        
        # Save assistant message
        if user_id and chat_id:
            db.client.table('messages').insert({
                'chat_id': chat_id,
                'role': 'assistant',
                'content': ai_message,
                'properties': properties if properties else None
            }).execute()
            
            db.client.table('chats').update({
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', chat_id).execute()
        
        return jsonify({
            'chatId': chat_id,
            'message': ai_message,
            'properties': properties,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"[Chat Error] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to process message'}), 500

# ============================================
# CHAT HISTORY
# ============================================

@chat_bp.route('/chat/<chat_id>', methods=['GET'])
@token_required
def get_chat_history(current_user_id, chat_id):
    """Get full chat history"""
    try:
        chat_result = db.client.table('chats').select('*').eq('id', chat_id).eq('user_id', current_user_id).execute()
        
        if not chat_result.data:
            return jsonify({'error': 'Chat not found'}), 404
        
        chat = chat_result.data[0]
        
        messages_result = db.client.table('messages').select('*').eq('chat_id', chat_id).order('created_at').execute()
        
        return jsonify({
            'chat': {
                'id': chat['id'],
                'title': chat['title'],
                'created_at': chat['created_at']
            },
            'messages': [
                {
                    'id': msg['id'],
                    'role': msg['role'],
                    'content': msg['content'],
                    'properties': msg.get('properties', []) or [],
                    'timestamp': msg['created_at']
                }
                for msg in messages_result.data
            ]
        })
        
    except Exception as e:
        print(f"[Chat History Error] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch chat history'}), 500

# ============================================
# CHAT LIST
# ============================================

@chat_bp.route('/chat/list', methods=['GET'])
@token_required
def get_chat_list(current_user_id):
    """Get user's chat list"""
    try:
        result = db.client.table('chats').select('*').eq('user_id', current_user_id).order('updated_at', desc=True).limit(50).execute()
        
        return jsonify([
            {
                'id': chat['id'],
                'title': chat['title'],
                'created_at': chat['created_at'],
                'updated_at': chat['updated_at']
            }
            for chat in result.data
        ])
        
    except Exception as e:
        print(f"[Chat List Error] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch chats'}), 500

# ============================================
# DELETE CHAT
# ============================================

@chat_bp.route('/chat/<chat_id>', methods=['DELETE'])
@token_required
def delete_chat(current_user_id, chat_id):
    """Delete a chat"""
    try:
        result = db.client.table('chats').delete().eq('id', chat_id).eq('user_id', current_user_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Chat not found'}), 404
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[Delete Chat Error] {str(e)}")
        import traceback
        traceback.print_exc()
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
        existing = db.client.table('favorites').select('*').eq('user_id', current_user_id).eq('listing_id', listing_id).execute()
        
        if not existing.data:
            db.client.table('favorites').insert({
                'user_id': current_user_id,
                'listing_id': listing_id
            }).execute()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[Add Favorite Error] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to add favorite'}), 500

@chat_bp.route('/favorites/<listing_id>', methods=['DELETE'])
@token_required
def remove_favorite(current_user_id, listing_id):
    """Remove listing from favorites"""
    try:
        db.client.table('favorites').delete().eq('user_id', current_user_id).eq('listing_id', listing_id).execute()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[Remove Favorite Error] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to remove favorite'}), 500

@chat_bp.route('/favorites', methods=['GET'])
@token_required
def get_favorites(current_user_id):
    """Get user's favorite listings"""
    try:
        favorites_result = db.client.table('favorites').select('listing_id').eq('user_id', current_user_id).order('created_at', desc=True).execute()
        
        if not favorites_result.data:
            return jsonify([])
        
        listing_ids = [fav['listing_id'] for fav in favorites_result.data]
        
        listings_result = db.client.table('listings').select('*').in_('id', listing_ids).execute()
        
        return jsonify(listings_result.data)
        
    except Exception as e:
        print(f"[Get Favorites Error] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch favorites'}), 500
