#!/usr/bin/env python
"""End-to-end test of FinSight query pipeline"""

import sys
sys.path.insert(0, '.')

from backend.agent.graph import run_agent

print('\n' + '='*60)
print('FINSIGHT END-TO-END TEST')
print('='*60)

test_queries = [
    "What was Apple revenue in 2023?",
    "Compare Microsoft and Google R&D spending",
]

for i, query in enumerate(test_queries, 1):
    print(f'\n[Test {i}/{len(test_queries)}]')
    print(f'Query: {query}')
    print('-'*60)
    
    try:
        result = run_agent(query)
        
        print(f'✓ Success!')
        print(f'  Answer length: {len(result["answer"])} chars')
        print(f'  Sub-questions: {len(result["sub_questions"])}')
        print(f'  Sources: {len(result["sources"])}')
        print(f'  Retries: {result["retry_count"]}')
        
        if result.get('error'):
            print(f'  ⚠ Error: {result["error"]}')
            
    except Exception as e:
        print(f'✗ FAILED: {e}')
        import traceback
        traceback.print_exc()

print('\n' + '='*60)
print('All tests complete!')
print('='*60 + '\n')
