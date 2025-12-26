#!/usr/bin/env python3

"""
Unix AI Assistant - Interactive AI helper for Unix commands
Usage: python3 unixai.py "your question here"
"""

import sys
import os
import requests
import subprocess
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 unixai.py 'your question here'")
        print("\nExamples:")
        print("  python3 unixai.py 'find large files'")
        print("  python3 unixai.py 'check disk space'")
        print("  python3 unixai.py 'list all processes'")
        sys.exit(1)
    
    question = ' '.join(sys.argv[1:])    
    print(f"🤖 Question: {question}\n🔄 Asking AI...\n")

    api_key = os.environ.get('OPENAI_API_KEY')

    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set")
        print("\nTo fix:")
        print("export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    try:
        r = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': '''You are a Unix expert. When answering:
1. If user needs a command, provide it on a line starting with "COMMAND:"
2. Explain what it does
3. Warn about any risks

Example:
COMMAND: find . -type f -size +10M
EXPLANATION: Finds files larger than 10MB
NOTES: May take time on large directories'''
                    },
                    {'role': 'user', 'content': question}
                ],
                'max_tokens': 500
            },
            timeout=30
        )

        if r.status_code != 200:
            print(f"❌ API Error: {r.status_code}")
            print(r.text)
            sys.exit(1)
         
        response = r.json()['choices'][0]['message']['content']    

        print("💡 AI Response:")
        print("="*60)
        print(response)
        print("="*60)

        command = None

        for line in response.split('\n'):
            if line.startswith('COMMAND:'):
                command = line.replace('COMMAND:', '').strip()
                break

        if not command and '```' in response:
            match = re.search(r'```(?:bash)?\n(.+?)\n```', response, re.DOTALL)
            if match:
                command = match.group(1).strip()
             
        if command:
            print(f"\n🔧 Found command: {command}")
            dangerous = ['rm -rf /', 'mkfs', 'dd if=/dev/', ':(){:|:&};:', 'chmod -R 777 /'] 
            if any(d in command for d in dangerous):
                print("⚠️  DANGER: This command could harm your system!")
                return

            choice = input("\n❓ Execute? (y/n): ").lower()    

            if choice == 'y':
                print("\n⚡ Executing...\n")
                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if result.stdout.strip():
                        print("✅ Output:")
                        print(result.stdout)

                    elif result.returncode == 0:
                        print("✅ Command completed successfully")
                        print("💡 No output (normal if nothing matched)")    

                    if result.stderr.strip():
                        print("⚠️  Warnings:")
                        print(result.stderr)    


                except subprocess.TimeoutExpired:
                    print("⏱️  Timeout after 30 seconds")
                except Exception as e:
                    print(f"❌ Error: {e}")   

            else:
                print("❌ Not executed")        

               
    except requests.exceptions.ConnectionError:
        print("❌ Network error. Check internet connection.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
