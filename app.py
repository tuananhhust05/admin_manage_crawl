from app import create_app
from config import Config
import logging
import sys

# Cấu hình logging để hiển thị traceback trong terminal
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Hiển thị log ra terminal
    ]
)

# Tạo logger cho ứng dụng
logger = logging.getLogger(__name__)

app, mongo = create_app()

if __name__ == '__main__':
    logger.info(f"Starting Flask app on port {Config.PORT}")
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=True
    )
