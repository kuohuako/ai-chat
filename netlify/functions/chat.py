import json
import os
from openai import OpenAI
import google.generativeai as genai

def handler(event, context):
    # 處理 CORS 預檢請求
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': ''
        }

    # 只接受 POST
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }

    try:
        data = json.loads(event['body'])
        user_message = data.get('message', '')
        provider = data.get('provider', 'openai')  # 預設使用 OpenAI

        if not user_message:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': '訊息不能是空的'})
            }

        # 根據選擇的 provider 呼叫不同的 API
        if provider == 'google':
            ai_message = call_google_api(user_message)
        else:
            ai_message = call_openai_api(user_message)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': ai_message,
                'provider': provider
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


def call_openai_api(user_message):
    """使用 OpenAI GPT API"""
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    response = client.chat.completions.create(
        model="gpt-5.6-terra",
        messages=[
            {"role": "system", "content": "你是一個友善的 AI 助手，用繁體中文回答問題。"},
            {"role": "user", "content": user_message}
        ],
        max_tokens=500,
        temperature=0.7
    )

    return response.choices[0].message.content


def call_google_api(user_message):
    """使用 Google Gemini API"""
    genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))

    model = genai.GenerativeModel('gemini-3.5-flash')

    chat = model.start_chat(history=[])
    response = chat.send_message(
        f"你是一個友善的 AI 助手，請用繁體中文回答以下問題：\n\n{user_message}"
    )

    return response.text
