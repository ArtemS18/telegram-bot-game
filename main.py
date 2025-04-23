import os
import uvicorn
import yaml
from app.web.app import setup_app

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, "config.yaml")
    etc_config_path = os.path.join(base_dir, "etc", "config.yaml")
    
    
    app = setup_app(config_path, etc_config_path)
    
    host = app.etc_config.web.get("host", "127.0.0.1")
    port = app.etc_config.web.get("port", 8000)
    reload_flag = app.etc_config.debug 
    
    uvicorn.run(app, host=host, port=port, reload=reload_flag)
