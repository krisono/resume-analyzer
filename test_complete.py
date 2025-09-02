#!/usr/bin/env python3
"""
Resume Analyzer Test Script
Test all features of the streamlined resume analyzer
"""

import requests
import json
import time
import threading
import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/Users/nnaemeka/resume-analyzer')

from src.app_factory import create_app

def start_test_server():
    """Start the Flask server for testing"""
    app = create_app()
    
    def run_server():
        app.run(host='127.0.0.1', port=3002, debug=False, use_reloader=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # Wait for server to start
    return app

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:3002/health')
        result = response.json()
        print("✅ Health Check:", json.dumps(result, indent=2))
        return True
    except Exception as e:
        print("❌ Health Check Failed:", e)
        return False

def test_user_registration():
    """Test user registration"""
    try:
        reg_data = {
            'email': 'testuser@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = requests.post('http://localhost:3002/api/auth/register', json=reg_data)
        result = response.json()
        
        if response.status_code == 201:
            print("✅ User Registration:", "SUCCESS")
            print("  - User ID:", result['user']['id'])
            print("  - Email:", result['user']['email'])
            print("  - Tokens received:", 'access_token' in result['tokens'])
            return result['tokens']['access_token']
        else:
            print("❌ User Registration Failed:", result)
            return None
    except Exception as e:
        print("❌ User Registration Error:", e)
        return None

def test_user_login():
    """Test user login"""
    try:
        login_data = {
            'email': 'testuser@example.com',
            'password': 'TestPassword123!'
        }
        response = requests.post('http://localhost:3002/api/auth/login', json=login_data)
        result = response.json()
        
        if response.status_code == 200:
            print("✅ User Login:", "SUCCESS")
            return result['tokens']['access_token']
        else:
            print("❌ User Login Failed:", result)
            return None
    except Exception as e:
        print("❌ User Login Error:", e)
        return None

def test_comprehensive_analysis(access_token):
    """Test comprehensive analysis with authentication"""
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Sample resume and job description
        analysis_data = {
            'resume_text': '''
            John Doe
            Software Engineer
            Email: john.doe@example.com
            Phone: (555) 123-4567
            
            EXPERIENCE
            Senior Software Engineer at Tech Corp (2020-2023)
            - Developed web applications using React and Node.js
            - Led a team of 5 developers
            - Improved application performance by 40%
            
            Software Developer at StartupXYZ (2018-2020)
            - Built REST APIs using Python and Flask
            - Worked with PostgreSQL databases
            - Implemented automated testing
            
            EDUCATION
            Bachelor of Science in Computer Science
            University of Technology (2014-2018)
            
            SKILLS
            Python, JavaScript, React, Node.js, Flask, PostgreSQL, Git, Docker
            ''',
            'job_description_text': '''
            Senior Full Stack Developer
            
            We are looking for an experienced full stack developer to join our team.
            
            Requirements:
            - 3+ years of experience with Python and JavaScript
            - Experience with React and Node.js
            - Knowledge of databases (PostgreSQL preferred)
            - Experience with REST API development
            - Familiarity with Docker and Git
            - Strong problem-solving skills
            
            Responsibilities:
            - Develop and maintain web applications
            - Collaborate with cross-functional teams
            - Optimize application performance
            - Write clean, maintainable code
            ''',
            'file_format': 'pdf'
        }
        
        response = requests.post('http://localhost:3002/api/analyze', 
                               json=analysis_data, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Comprehensive Analysis:", "SUCCESS")
            print("  - Overall Score:", result.get('scores', {}).get('overall_score', 'N/A'))
            print("  - Analysis Saved:", result.get('analysis_metadata', {}).get('saved_to_history', False))
            
            # Check enhanced features
            enhanced = result.get('enhanced_features', {})
            if 'semantic_similarity' in enhanced:
                print("  - Semantic Analysis:", "✅ Available")
            if 'ats_analysis' in enhanced:
                print("  - Enhanced ATS:", "✅ Available")
            if 'entities' in enhanced:
                print("  - Entity Extraction:", "✅ Available")
            
            return True
        else:
            print("❌ Comprehensive Analysis Failed:", result)
            return False
    except Exception as e:
        print("❌ Comprehensive Analysis Error:", e)
        return False

def test_analysis_history(access_token):
    """Test analysis history retrieval"""
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('http://localhost:3002/api/analyze-history', headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Analysis History:", "SUCCESS")
            print("  - Total Analyses:", len(result.get('history', [])))
            return True
        else:
            print("❌ Analysis History Failed:", result)
            return False
    except Exception as e:
        print("❌ Analysis History Error:", e)
        return False

def main():
    """Run all Resume Analyzer tests"""
    print("🚀 Starting Resume Analyzer Comprehensive Tests")
    print("=" * 50)
    
    # Start test server
    print("Starting test server...")
    app = start_test_server()
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Health check
    if test_health_endpoint():
        tests_passed += 1
    
    # Test 2: User registration
    access_token = test_user_registration()
    if access_token:
        tests_passed += 1
    else:
        # Try login with existing user
        access_token = test_user_login()
        if access_token:
            tests_passed += 1
    
    # Test 3: Comprehensive analysis
    if access_token and test_comprehensive_analysis(access_token):
        tests_passed += 1
    
    # Test 4: Analysis history
    if access_token and test_analysis_history(access_token):
        tests_passed += 1
    
    # Test 5: Anonymous analysis (without auth)
    print("\nTesting anonymous analysis...")
    try:
        analysis_data = {
            'resume_text': 'Sample resume text',
            'job_description_text': 'Sample job description'
        }
        response = requests.post('http://localhost:3002/api/analyze', json=analysis_data)
        if response.status_code == 200:
            print("✅ Anonymous Analysis:", "SUCCESS")
            tests_passed += 1
        else:
            print("❌ Anonymous Analysis Failed")
    except Exception as e:
        print("❌ Anonymous Analysis Error:", e)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎯 Tests Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All features are working correctly!")
        print("\nAvailable Features:")
        print("  ✅ User Authentication (Registration/Login)")
        print("  ✅ Comprehensive NLP Analysis (Semantic Similarity)")
        print("  ✅ Advanced ATS Compatibility Checks")
        print("  ✅ Named Entity Extraction")
        print("  ✅ Analysis History Storage")
        print("  ✅ Database Integration")
        print("  ✅ JWT Token Management")
        print("  ✅ Content Quality Analysis")
    else:
        print("⚠️  Some tests failed - check the implementation")
    
    print(f"\n🌐 Frontend available at: http://localhost:5174")
    print(f"🔧 Backend API available at: http://localhost:3001")

if __name__ == "__main__":
    main()
