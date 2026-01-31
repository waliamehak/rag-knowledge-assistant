from mangum import Mangum
from main import app

# Lambda handler - wraps FastAPI for AWS Lambda
handler = Mangum(app)