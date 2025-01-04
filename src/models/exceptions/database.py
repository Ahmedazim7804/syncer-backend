
class DatabaseQueryFailed(Exception):
    def __init__(self, message: str = "Could not execute the query"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

class DatabseQuerySuccess(Exception):
    def __init__(self, message: str = "Query executed successfully"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message