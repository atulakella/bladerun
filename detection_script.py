import os
import sys
import requests
from github import Github, PullRequest
import json
import math


def main(pr_number, github_token):
    # Authenticate with GitHub
    github_client = Github(github_token)
    repo = github_client.get_repo(os.getenv('GITHUB_REPOSITORY'))
    pr = repo.get_pull(pr_number)
    
    # Get list of changed files in the PR
    changed_files = get_changed_files(pr)
    
    llm_generated_count = 0
    total_lines_count = 0
    llm_pct = 0
    for file_path in changed_files:
        try:
            # Fetch file content
            file_content = repo.get_contents(file_path).decoded_content.decode('utf-8')
            llm_pct = pct_llm(file_content)
            print("sagar_dbg:" , file_content)
            lines = file_content.splitlines()
            
            for line in lines:
                total_lines_count += 1
                # Implement your logic to detect LLM-generated content
                if is_llm_generated(line):
                    llm_generated_count += 1
                    break
        
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    # Calculate percentage
    if total_lines_count > 0:
        llm_percentage = (llm_generated_count / total_lines_count) * 100
    else:
        llm_percentage = 0
    
    # Post comment with percentage
    print('sagar_dbg:', llm_pct)
    post_comment(pr, llm_pct, github_client)

def get_changed_files(pr: PullRequest):
    files = []
    for file in pr.get_files():
        files.append(file.filename)
    return files

def pct_llm(cnt):

    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTZiZDAzODQtNGNmZC00NjNiLTgzY2YtYTdhMDM5NjJmZDU0IiwidHlwZSI6ImFwaV90b2tlbiJ9.ghV8kpI_Ya3q2qczOqmp-Y8fd1fmnaIkbnze6ifUSFI"}

    url = "https://api.edenai.run/v2/text/ai_detection"
    payload = {
    "providers": "originalityai",
    "text": cnt,
    }

    response = requests.post(url, json=payload, headers=headers)

    result = json.loads(response.text)
    items = result['originalityai']['items']
    llm = 0
    llm = 0
    for item in items:
        if item['prediction'] == 'ai-generated':
            llm += 1
    pct = (llm / len(item['prediction']) ) * 100
    print('sagar_dbg:', pct)
    return pct

def is_llm_generated(line):
    # Implement your detection logic here
    # Example: Check for common patterns, language characteristics, etc.
    # This can involve regex, ML models, or specific keywords known to be generated by LLMs
    # Define the model and tokenizer
    

    return False
    

def post_comment(pr, llm_percentage, github_client):
    comment_body = f"ℹ️ **LLM Generated Code Detection**: {llm_percentage:.2f}% of the code changes appear to be LLM-generated."
    pr.create_issue_comment(comment_body)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python detection_script.py <pr_number> <github_token>")
        sys.exit(1)
    
    pr_number = int(sys.argv[1])
    github_token = sys.argv[2]
    
    main(pr_number, github_token)
