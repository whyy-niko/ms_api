from fastapi.responses import JSONResponse
import json
from database import get_sql_queries

class SQLAwareJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        # Добавляем SQL запросы к контенту
        if isinstance(content, (dict, list)):
            if not isinstance(content, dict):
                content = {"data": content}
            
            sql_queries = get_sql_queries()
            content['sql'] = [
                {
                    'query': query['statement'].strip(),
                    'parameters': str(query['parameters']),
                    'executemany': query['executemany']
                } for query in sql_queries
            ]
        
        return super().render(content)